"""Series of sanity tests for data processing, using known features of DataSet"""

import context
context.get()

import unittest
import numpy as np
import magSonify
from magSonify.MagnetometerData import THEMISdata
from magSonify.DataSet import DataSet
from magSonify.DataSet_1D import DataSet_1D
from datetime import datetime

class THEMISProcessingTestCase(unittest.TestCase):
    def verify_magSane(self,mag:THEMISdata):
        """Performs sanity tests on THEMISdata class instances"""
        for name,expectedkeys in {
            "magneticField": (0,1,2),"magneticFieldMeanFieldCoordinates": (0,1,2), 
            "peemIdentifyMagnetosheath": ('density','velocity_x','flux_x','flux_y'),
            "position": (0, 1, 2, 'radius'), "meanField": (0,1,2)
        }.items():
            attr: DataSet = getattr(mag,name)
            if attr is not None:
                attrkeys = attr.keys()
                for key in expectedkeys:
                    try:
                        self.assertIn(key,attrkeys)
                        self.assertEqual(
                            len(attr.timeSeries.asDatetime()),
                            len(attr.data[key])
                        )
                        self.assertNotEqual(len(attr.timeSeries.asDatetime()),0)
                        self.assertFalse(np.all(attr.data[key] == 0))
                    except Exception:
                        print("Exception relates to name: {name}, key: {key}")
                        raise

    def verify_axSane(self,ax: DataSet_1D):
        self.assertIn(0,ax.keys())
        self.assertEqual(
            len(ax.timeSeries.asDatetime()),
            len(ax.x)
        )
        self.assertNotEqual(len(ax.timeSeries.asDatetime()),0)
        self.assertFalse(np.all(ax.x == 0))

    def testImport(self):
        mag = self._import()
        self.verify_magSane(mag)

    def _import(self):
        mag = THEMISdata()
        mag.importCDAS(datetime(2007,9,4),datetime(2007,9,5))
        return mag

    def testProcessing(self):
        step_list =["mag.position.removeDuplicateTimes()",
        "mag.magneticField.removeDuplicateTimes()",
        "if mag.peemIdentifyMagnetosheath is not None: mag.peemIdentifyMagnetosheath.removeDuplicateTimes()",
        "mag.interpolate()",
        "mag.magneticField.constrainAbsoluteValue(400)",
        "mag.meanField = mag.magneticField.runningAverage(timeWindow=np.timedelta64(35,\"m\"))",
        "mag.magneticField = mag.magneticField - mag.meanField",
        "mag.fillLessThanRadius(4)",
        "mag.removeMagnetosheath()",
        "mag.convertToMeanFieldCoordinates()",
        "mag.magneticFieldMeanFieldCoordinates.fillNaN()",]
        mag = self._import()
        for step in step_list:
            try:
                exec(step)
                self.verify_magSane(mag)
            except Exception:
                print("Exception while running:",step)
                raise

    def testSonification(self):
        mag: DataSet_1D = self._import()
        mag.defaultProcessing()
        for alg, algArgs in {
            "waveletStretch": (16,),
            "waveletStretch": (16, 0.5, 16),
            "paulStretch": (16,),
            "phaseVocoderStretch": (16,),
            "wsolaStretch": (16,)
        }.items():
            try:
                ax = mag.magneticFieldMeanFieldCoordinates.extractKey(0)
                getattr(ax,alg)(*algArgs)
                self.verify_axSane(ax)
            except Exception:
                print("Exception while running:", alg, "with arguments", algArgs)
                raise

if __name__ == "__main__":
    unittest.main()