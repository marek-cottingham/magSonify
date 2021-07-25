
from datetime import datetime, time
from .TimeSeries import TimeSeries, generateTimeSeries
from .DataSet import DataSet, DataSet_3D
from .DataSet_1D import DataSet_1D
from threading import Thread
import numpy as np
from numpy import logical_or, logical_and

from ai import cdas 

class MagnetometerData():
    """Class providing a high level api for data import and processing"""
    def __init__(self):
        self.magneticField: DataSet_3D = None
        """The magnetic field at the satellite"""
        self.position: DataSet_3D = None
        """The position of the satellite"""
        self.meanField: DataSet_3D = None
        """The mean magnetic field after a rolling average"""
        self.magneticFieldMeanFieldCoordinates: DataSet_3D = None
        """The magnetic field in mean field align coordinates"""

        self.peemIdentifyMagnetosheath: DataSet = None
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
            Start of data range as ``datetime.datetime`` or ``numpy.datetime64``
        :param endDatetime:
            End of data range as ``datetime.datetime`` or ``numpy.datetime64``
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

        :attr:`peemIdentifyMagnetosheath` must be specified, otherwise no action is taken.
        """
        if self.peemIdentifyMagnetosheath is None:
            return None
        
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

    def _interpolateReference(self, refTimeSeries: TimeSeries) -> None:
        """Removes duplicate times, then interpolates data sets :attr:`magneticField`, 
        :attr:`position` and :attr:`peemIdentifyMagnetosheath` to match the specified time series, 
        if the data sets are not None."""
        for x in (
            self.magneticField,
            self.position,
            self.peemIdentifyMagnetosheath,
        ):
            if x is not None:
                x.removeDuplicateTimes()
                x.interpolateReference(refTimeSeries)
    
class THEMISdata(MagnetometerData):
    def interpolate(self,spacingInSeconds=3) -> None:
        """Interpolates data sets :attr:`magneticField`, :attr:`position` and 
        :attr:`peemIdentifyMagnetosheath` to the specified spacing, if they are not None.

        A default spacing of 3s is chossen for THEMIS data. This is slightly smaller than the mean
        sample spacing in the raw magnetometer data of ~3.17 s. Using a consistent value aids in 
        establishing the correspondence between frequencies in sonified audio and the raw data.
        """
        refTimeSeries = generateTimeSeries(
            self.magneticField.timeSeries.getStart(),
            self.magneticField.timeSeries.getEnd(),
            spacing=np.timedelta64(spacingInSeconds,'s')
        )
        self._interpolateReference(refTimeSeries)

    def importCDAS(self,startDatetime,endDatetime,satellite="D") -> None:
        """ Imports magnetic field, position, radial distance and peem data for the designated 
            THEMIS satellite and datetime range.
            The possible satellite letters are: "A", "B", "C", "D" or "E".
            See also: :meth:`MagnetometerData._importAsync`
        """
        funcs = (self._importCdasMagneticField,self._importCdasPosition,self._importCdasPeem)
        self._importAsync(funcs,startDatetime,endDatetime,satellite)

    def _importCdasPosition(self, startDatetime, endDatetime, satellite) -> None:
        cdasArgs = (
            'sp_phys',
            f'TH{satellite.upper()}_OR_SSC',
            startDatetime,
            endDatetime,
            ['XYZ_GSM','RADIUS'],
        )
        timeSeriesKey = "EPOCH"
        targetKeys = {
            0: 'X', 1: 'Y', 2: 'Z', 'radius': "RADIUS"
        }
        self.position = self._importCdasItemWithExceptions(
            cdasArgs,timeSeriesKey,targetKeys,DataSet_3D
        )

    def _importCdasMagneticField(self, startDatetime, endDatetime, satellite) -> None:
        cdasArgs = (
            'sp_phys',
            f'TH{satellite.upper()}_L2_FGM',
            startDatetime,
            endDatetime,
            [f'th{satellite.lower()}_fgs_gsmQ']
        )
        timeSeriesKey = "UT"
        targetKeys = {
            0: f"BX_FGS-{satellite.upper()}",
            1: f"BY_FGS-{satellite.upper()}",
            2: f"BZ_FGS-{satellite.upper()}"
        }
        self.magneticField = self._importCdasItemWithExceptions(
            cdasArgs,timeSeriesKey,targetKeys,DataSet_3D
        )
    
    def _importCdasPeem(self,startDatetime,endDatetime,satellite) -> None:
        cdasArgs = (
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
        timeSeriesKey = "UT"
        targetKeys = {
            'density': f"N_ELEC_MOM_ESA-{satellite.upper()}",
            'velocity_x': f'VX_ELEC_GSM_MOM_ESA-{satellite.upper()}',
            'flux_x': f'FX_ELEC_MOM_ESA-{satellite.upper()}',
            'flux_y': f'FY_ELEC_MOM_ESA-{satellite.upper()}',
        }
        self.peemIdentifyMagnetosheath = self._importCdasItemWithExceptions(
            cdasArgs,timeSeriesKey,targetKeys,DataSet
        )

    def _importCdasItemWithExceptions(self,
        cdasArgs: tuple,
        timeSeriesKey: str,
        targetKeys: dict,
        returnClassType: type = DataSet,
    ):
        """Imports cdas data for the given ``cdasArgs``, extracting a dataset.

        :param tuple cdasArgs: Arguments for ``ai.cdas.get_data()``
        :param str timeSeriesKey: The key that the times are refered to as in CDAS data return
        :param dict targetKeys:
            Dictionary where its values are the keys in CDAs data to include in the data set, and
            its keys are the keys that should be used to reference these within the data set.
        :param type returnClassType: 
            Class used to construct the returned data set, eg. :class:`DataSet`, :class:`DataSet_3D`
        """
        data = cdas.get_data(*cdasArgs)
        if data is None:
            raise CdasImportError.CdasNoDataReturnedError
        timeSeries = TimeSeries(data[timeSeriesKey])
        selecetedData = {}

        for key, cdasKey in targetKeys.items():
            try:
                d = data[cdasKey]
            except KeyError:
                raise CdasImportError.CdasKeyMissingError(f"Key not found:",cdasKey)
            selecetedData[key] = d

        return returnClassType(timeSeries,selecetedData)
    
    def defaultProcessing(self,
        removeMagnetosheath=False,
        minRadius=4,
        allowSkipMagnetosheathRemovalIfInsufficientData = True
    ) -> None:
        """Performs a standard processing procedure on THEMIS data.

        :param removeMagnetosheath: Whether to remove data while in the magnetosheath
        :param minRadius: Radius in earth radii below which to remove magnetic field data
        """
        self.interpolate()
        self.magneticField.constrainAbsoluteValue(400)
        self.meanField = self.magneticField.runningAverage(timeWindow=np.timedelta64(35,"m"))
        self.magneticField = self.magneticField - self.meanField
        self.fillLessThanRadius(minRadius)
        if removeMagnetosheath:
            self.removeMagnetosheath()
        self.convertToMeanFieldCoordinates()
        self.magneticFieldMeanFieldCoordinates.fillNaN()

class CdasImportError(Exception):
    class CdasNoDataReturnedError(Exception):
        pass
    class CdasKeyMissingError(Exception):
        pass