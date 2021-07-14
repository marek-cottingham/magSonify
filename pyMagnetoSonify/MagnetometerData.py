
from pyMagnetoSonify.DataSet import DataSet, DataSet_3D, TimeSeries
import numpy as np
from ai import cdas 

class MagnetometerData():
    def __init__(self):
        pass

    def importCDAS(self):
        self.magneticField = DataSet_3D()
        self.position = DataSet_3D()
        self.meanField = DataSet_3D()

    def fillLessThanRadius(self,radiusInEarthRadii,const=0):
        assert(self.position.timeSeries == self.magneticField.timeSeries)
        radiusMask = np.array(self.position.data["radius"] < radiusInEarthRadii, dtype=np.int8 )
        for i,d in self.magneticField.items():
            d[radiusMask] = const

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



    
class THEMISdata(MagnetometerData):
    def importCDAS(s,startDate,endDate,satellite="D"):
        """ Imports magnetic field, satellite and radial distance data for the designated THEMIS
            satellite and given date range.
            The possible satellite letters are: "A", "B", "C", "D" or "E"
        """
        data = cdas.get_data(
            'sp_phys',
            f'TH{satellite.upper()}_L2_FGM',
            startDate,
            endDate,
            [f'th{satellite.lower()}_fgs_gsmQ']
        )
        s.magneticField = DataSet_3D(
            TimeSeries(data["UT"]),
            data[f"BX_FGS-{satellite}"],
            data[f"BY_FGS-{satellite}"],
            data[f"BZ_FGS-{satellite}"]
        )
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
        def process(s):
            """ Compact call for the default set of initial processing operations
            """
            pass