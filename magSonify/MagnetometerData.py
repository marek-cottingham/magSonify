
from datetime import datetime
from .TimeSeries import TimeSeries, generateTimeSeries
from .DataSet import DataSet, DataSet_3D, DataSet_3D_Placeholder, DataSet_Placeholder
from .DataSet_1D import DataSet_1D
from threading import Thread
import numpy as np
from numpy import logical_or, logical_and

from ai import cdas 

class MagnetometerData():
    """Class providing a high level api for data import and processing"""
    def __init__(self):
        self.magneticField = DataSet_3D_Placeholder()
        """The magnetic field at the satellite"""
        self.position = DataSet_3D_Placeholder()
        """The position of the satellite"""
        self.meanField = DataSet_3D_Placeholder()
        """The mean magnetic field after a rolling average"""
        self.magneticFieldMeanFieldCoordinates = DataSet_3D_Placeholder()
        """The magnetic field in mean field align coordinates"""

        self.peemIdentifyMagnetosheath = DataSet_Placeholder()
        """Required information for removal of magnetosheath

        ``keys: 'density','velocity_x','flux_x',flux_y'`` """

    def _importAsync(self,funcs,startDatetime,endDatetime,*args) -> None:
        """ Runs the CDAS imports defined in ``funcs`` asyncronously.

        :param funcs:
            Tuple of functions to execute. Each function should be of the form
            ``func(startDatetime,endDatetime,*args) -> None``. Any imported data
            should be written to a class attribute.

            .. Warning::

                These functions should not read data from the class or modify the same attributes
                as there is no prevention of a race condition. The functions are run simulataneously
                using ``threading`` library.

        :param startDatetime:
            Start of data range as ``datatime.datetime`` or ``numpy.datetime64``
        :param endDatetime:
            End of data range as ``datatime.datetime`` or ``numpy.datetime64``
        :param \*args:
            Arbitrary arguments to be passed to the functions.
        """
        arguments = (startDatetime,endDatetime,*args)
        fetchers = []
        for func in funcs:
            fetch = Thread(target=func,args=arguments)
            fetch.start()
            fetchers.append(fetch)
        for fetch in fetchers:
            fetch.join()

    def fillLessThanRadius(self,radiusInEarthRadii,const=0) -> None:
        """Fills all values in the magnetic field with ``const`` when the radius is below the 
        specified value.
        """
        assert(self.position.timeSeries == self.magneticField.timeSeries)
        radiusMask = self.position.data["radius"] < radiusInEarthRadii
        self.magneticField.fillFlagged(radiusMask,const)

    def convertToMeanFieldCoordinates(self) -> None:
        """ Converts the magnetic field data in :attr:`magneticField` to mean field coordinates,
        saving the output in :attr:`magneticFieldMeanFieldCoordinates`.
        
        .. warning::

            :attr:`meanField` must be specified and contain a 3D dataset with the mean 
            magnetic field.

            :attr:`magneticField` must be specified
        """
        assert(self.position.timeSeries == self.magneticField.timeSeries)
        assert(self.magneticField.timeSeries == self.meanField.timeSeries)

        fieldUnitVector = self.meanField.copy()
        fieldUnitVector.makeUnitVector()
        earthUnitVector = -(self.position.copy())
        earthUnitVector.makeUnitVector()

        polUnitVector = fieldUnitVector.cross(earthUnitVector)
        polUnitVector.makeUnitVector()
        torUnitVector = fieldUnitVector.cross(polUnitVector)
        torUnitVector.makeUnitVector()

        self.magneticFieldMeanFieldCoordinates = self.magneticField.coordinateTransform(
            fieldUnitVector,
            polUnitVector,
            torUnitVector
        )

    def removeMagnetosheath(self) -> None:
        """Removes portions of magnetic field data while the satellite is in the magnetosheath.

        .. warning::

            :attr:`peemIdentifyMagnetosheath` must be specified.
        """
        fluxX = self.peemIdentifyMagnetosheath.data['flux_x']
        fluxY = self.peemIdentifyMagnetosheath.data['flux_y']
        perpFlux = (fluxX**2 + fluxY**2)**(1/2)
        density = self.peemIdentifyMagnetosheath.data['density']
        velocityX = self.peemIdentifyMagnetosheath.data['velocity_x']
        removeSheathFlags = logical_and(
            (self.position.data["radius"] > 8),
            logical_or(
                (density > 10),
                logical_or(
                    (velocityX < -200),
                    (perpFlux > 2e7)
                )
            )
        )
        self.magneticField.fillFlagged(removeSheathFlags)

    
class THEMISdata(MagnetometerData):
    def interpolate(self,spacingInSeconds=3) -> None:
        """Interpolates data sets :attr:`magneticField`, :attr:`position` and 
        :attr:`peemIdentifyMagnetosheath` to the specified spacing.

        A default spacing of 3s is chossen for THEMIS data. This is slightly smaller than the mean
        sample spacing in the raw magnetometer data of ~3.17 s. Using a consistent value aids in 
        establishing the correspondence between frequencies in sonified audio and the raw data.
        """
        refTimeSeries = generateTimeSeries(
            self.magneticField.timeSeries.getStart(),
            self.magneticField.timeSeries.getEnd(),
            spacing=np.timedelta64(spacingInSeconds,'s')
        )
        for x in (
            self.magneticField,
            self.position,
            self.peemIdentifyMagnetosheath
        ):
            x.interpolateReference(refTimeSeries)

    def importCDAS(self,startDatetime,endDatetime,satellite="D") -> None:
        """ Imports magnetic field, position, radial distance and peem data for the designated 
            THEMIS satellite and datetime range.
            The possible satellite letters are: "A", "B", "C", "D" or "E".
            See also: :meth:`MagnetometerData._importAsync`
        """
        funcs = (self._importCdasMagneticField,self._importCdasPosition,self._importCdasPeem)
        self._importAsync(funcs,startDatetime,endDatetime,satellite)

    def _importCdasPosition(s, startDatetime, endDatetime, satellite) -> None:
        data = cdas.get_data(
            'sp_phys',
            f'TH{satellite.upper()}_OR_SSC',
            startDatetime,
            endDatetime,
            ['XYZ_GSM','RADIUS'],
        )
        s.position = DataSet_3D(
            TimeSeries(data["EPOCH"]),
            {
                0: data["X"],
                1: data["Y"],
                2: data["Z"],
                "radius": data["RADIUS"]
            }
        )

    def _importCdasMagneticField(s, startDatetime, endDatetime, satellite) -> None:
        data = cdas.get_data(
            'sp_phys',
            f'TH{satellite.upper()}_L2_FGM',
            startDatetime,
            endDatetime,
            [f'th{satellite.lower()}_fgs_gsmQ']
        )
        s.magneticField = DataSet_3D(
            TimeSeries(data["UT"]),
            [
                data[f"BX_FGS-{satellite}"],
                data[f"BY_FGS-{satellite}"],
                data[f"BZ_FGS-{satellite}"]
            ]
        )
    
    def _importCdasPeem(s,startDatetime,endDatetime,satellite) -> None:
        data = cdas.get_data(
           'sp_phys',
           f'TH{satellite.upper()}_L2_MOM',
           startDatetime,
           endDatetime,
           [
               f'th{satellite.lower()}_peem_density',
               f'th{satellite.lower()}_peem_velocity_gsm',
               f'th{satellite.lower()}_peem_flux'
            ]
        )
        timeSeries = TimeSeries(data["UT"])
        s.peemIdentifyMagnetosheath = DataSet(
            timeSeries,
            {
                'density': data[f"N_ELEC_MOM_ESA-{satellite.upper()}"],
                'velocity_x': data[f'VX_ELEC_GSM_MOM_ESA-{satellite.upper()}'],
                'flux_x': data[f'FX_ELEC_MOM_ESA-{satellite.upper()}'],
                'flux_y': data[f'FY_ELEC_MOM_ESA-{satellite.upper()}']
            }
        )
    
    def defaultProcessing(self,removeMagnetosheath=False,minRadius=4) -> None:
        """Performs a standard processing procedure on THEMIS data.

        :param removeMagnetosheath: Whether to remove data while in the magnetosheath
        :param minRadius: Radius in earth radii below which to remove magnetic field data
        """
        self.magneticField.removeDuplicateTimes()
        self.peemIdentifyMagnetosheath.removeDuplicateTimes()
        self.interpolate()
        self.magneticField.constrainAbsoluteValue(400)
        self.meanField = self.magneticField.runningAverage(timeWindow=np.timedelta64(35,"m"))
        self.magneticField = self.magneticField - self.meanField
        self.fillLessThanRadius(minRadius)
        if removeMagnetosheath:
            self.removeMagnetosheath()
        self.convertToMeanFieldCoordinates()

        self.magneticFieldMeanFieldCoordinates.fillNaN()