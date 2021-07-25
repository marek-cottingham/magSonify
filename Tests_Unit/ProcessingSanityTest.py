"""Series of sanity tests for data processing, using known features of DataSet"""

if __name__ == "__main__":
    import context
    context.get()

import unittest
import numpy as np
import magSonify
from magSonify.MagnetometerData import THEMISdata
from magSonify.DataSet import DataSet
from magSonify.DataSet_1D import DataSet_1D
from datetime import date, datetime

class THEMISProcessingTestCase(unittest.TestCase):
    eventSuite = (
        (datetime(2007,9,4,6),datetime(2007,9,4,18),"d"),
        (datetime(2008,12,7,6),datetime(2008,12,7,18),"d"),
    )

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

    def _import(
            self,
            event=(datetime(2007,9,4,6),datetime(2007,9,4,18),"d")
        ):
        mag = THEMISdata()
        mag.importCDAS(*event)
        return mag

    def testProcessing(self):
        for event in self.eventSuite:
            self._testProcessingForEvent(event)

    def _testProcessingForEvent(self,event):
        step_list =[
        "mag = self._import(event)"
        "mag.position.removeDuplicateTimes()",
        "mag.magneticField.removeDuplicateTimes()",
        "if mag.peemIdentifyMagnetosheath is not None: mag.peemIdentifyMagnetosheath.removeDuplicateTimes()",
        "mag.interpolate()",
        "mag.magneticField.constrainAbsoluteValue(400)",
        "mag.meanField = mag.magneticField.runningAverage(timeWindow=np.timedelta64(35,\"m\"))",
        "mag.magneticField = mag.magneticField - mag.meanField",
        "mag.fillLessThanRadius(4)",
        "mag.removeMagnetosheath()",
        "mag.convertToMeanFieldCoordinates()",
        "mag.magneticFieldMeanFieldCoordinates.fillNaN()",
        ]
        mag = None
        for step in step_list:
            try:
                exec(step)
                self.verify_magSane(mag)
            except Exception:
                print("Exception while running:",step)
                raise

    def testSonification(self):
        for event in self.eventSuite:
            self._testSonificationForEvent(event)

    def _testSonificationForEvent(self, event):
        mag: DataSet_1D = self._import(event)
        mag.defaultProcessing()
        for alg, algArgs in {
                "phaseVocoderStretch": (16,),
                "waveletStretch": (16,),
                "waveletStretch": (16, 0.5, 16),
                "paulStretch": (16,),
                "wsolaStretch": (16,),
                "phaseVocoderStretch": (16,), # This is run twice to detect a particular regression bug
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