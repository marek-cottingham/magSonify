
from pyMagnetoSonify.TimeSeries import TimeSeries, generateTimeSeries
from pyMagnetoSonify.DataSet import DataSet, DataSet_3D, DataSet_3D_Placeholder, DataSet_Placeholder
from pyMagnetoSonify.DataSet_1D import DataSet_1D
from threading import Thread
import numpy as np
from numpy import logical_or, logical_and

from ai import cdas 

class MagnetometerData():
    def __init__(self):
        self.magneticField = DataSet_3D_Placeholder()
        self.position = DataSet_3D_Placeholder()
        self.meanField = DataSet_3D_Placeholder()
        self.magneticFieldMeanFieldCorrdinates = DataSet_3D_Placeholder()

        self.peemDensity = DataSet_Placeholder()
        self.peemFlux = DataSet_3D_Placeholder()
        self.peemVelocity = DataSet_3D_Placeholder()

    def importCDAS(self):
        raise NotImplementedError

    def fillLessThanRadius(self,radiusInEarthRadii,const=0):
        assert(self.position.timeSeries == self.magneticField.timeSeries)
        radiusMask = self.position.data["radius"] < radiusInEarthRadii
        self.magneticField.fillMask(radiusMask,const)

    def convertToMeanFieldCoordinates(self) -> None:
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

        self.magneticFieldMeanFieldCorrdinates = self.magneticField.coordinateTransform(
            fieldUnitVector,
            polUnitVector,
            torUnitVector
        )

    def removeMagnetosheath(self):
        # Beta
        perpflux = self.peemFlux.data[0]**2 + self.peemFlux.data[1]**2
        perpflux = perpflux**(1/2)
        removeSheathMask = logical_and(
            (self.position.data["radius"] > 8),
            logical_or(
                (self.peemDensity.x > 10),
                logical_or(
                    (self.peemVelocity.data[0] < -200),
                    (perpflux > 2e7)
                )
            )
        )
        self.magneticField.fillMask(removeSheathMask)

    
class THEMISdata(MagnetometerData):
    def interpolate_3s(self):
        """Iterpolates all data to 3 second spacing"""
        timeSeries_3s = generateTimeSeries(
            self.magneticField.timeSeries.getStart(),
            self.magneticField.timeSeries.getEnd(),
            spacing=np.timedelta64(3,'s')
        )
        for x in (
            self.magneticField,
            self.position,
            self.peemDensity,
            self.peemVelocity,
            self.peemFlux
        ):
            x.interpolate(timeSeries_3s)

    def importCDAS(s,startDate,endDate,satellite="D"):
        """ Imports magnetic field, position, radial distance and peem data for the designated THEMIS
            satellite and date range.
            The possible satellite letters are: "A", "B", "C", "D" or "E".
            Consider using importCdasAsync instead, as this is faster.
        """
        args = (startDate,endDate,satellite)
        s._importCdasMagneticField(*args)
        s._importCdasPosition(*args)
        s._importCdasPeem(*args)

    def importCdasAsync(self,startDate,endDate,satellite="D"):
        """ Imports magnetic field, position, radial distance and peem data for the designated 
            THEMIS satellite and date range.
            The possible satellite letters are: "A", "B", "C", "D" or "E".
        """
        args = (startDate,endDate,satellite)
        fetchers = []
        # These functions cannot modify the same variables/attributes as there 
        # is no prevention of a race condition
        funcs = (self._importCdasMagneticField,self._importCdasPosition,self._importCdasPeem)
        for func in funcs:
            fetch = Thread(target=func,args=args)
            fetch.start()
            fetchers.append(fetch)
        for fetch in fetchers:
            fetch.join()

    def _importCdasPosition(s, startDate, endDate, satellite):
        data = cdas.get_data(
            'sp_phys',
            f'TH{satellite.upper()}_OR_SSC',
            startDate,
            endDate,
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

    def _importCdasMagneticField(s, startDate, endDate, satellite):
        data = cdas.get_data(
            'sp_phys',
            f'TH{satellite.upper()}_L2_FGM',
            startDate,
            endDate,
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
    
    def _importCdasPeem(s,startDate,endDate,satellite):
        data = cdas.get_data(
           'sp_phys',
           f'TH{satellite.upper()}_L2_MOM',
           startDate,
           endDate,
           [
               f'th{satellite.lower()}_peem_density',
               f'th{satellite.lower()}_peem_velocity_gsm',
               f'th{satellite.lower()}_peem_flux'
            ]
        )
        timeSeries = TimeSeries(data["UT"])
        s.peemDensity = DataSet_1D(
            timeSeries,
            data[f"N_ELEC_MOM_ESA-{satellite.upper()}"]
        )
        s.peemVelocity = DataSet_3D(
            timeSeries,
            [
                data[f'VX_ELEC_GSM_MOM_ESA-{satellite.upper()}'],
                data[f'VY_ELEC_GSM_MOM_ESA-{satellite.upper()}'],
                data[f'VZ_ELEC_GSM_MOM_ESA-{satellite.upper()}']
            ]
        )
        s.peemFlux = DataSet_3D(
            timeSeries,
            [
                data[f'FX_ELEC_MOM_ESA-{satellite.upper()}'],
                data[f'FY_ELEC_MOM_ESA-{satellite.upper()}'],
                data[f'FZ_ELEC_MOM_ESA-{satellite.upper()}'],
            ]
        )