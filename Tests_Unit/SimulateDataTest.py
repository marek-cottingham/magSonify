from datetime import datetime
import unittest
import numpy as np

if __name__ == "__main__":
    import context
    context.get()

from numpyUnitTestCase import numpyunittest_TestCase
from magSonify.SimulateData import SimulateData
from magSonify.TimeSeries import TimeSeries, generateTimeSeries

class SimulateDataTests(numpyunittest_TestCase):
    def pre(self):
        spacing = np.timedelta64(1,'s').astype('timedelta64[ns]')/44100
        ts = generateTimeSeries(
            datetime(2007,1,1,12,0,0),
            datetime(2007,1,1,12,0,10),
            spacing=spacing
        )
        return ts

    def test_genSine(self):
        ts = self.pre()
        x = SimulateData().genSine(ts,200)
        xstretch = SimulateData().genSineExpectation(ts,2,200)
        self.assertAlmostEqual(np.mean(x), 0)
        self.assertAlmostEqual(np.max(x), 1)
        self.assertAlmostEqual(np.min(x), -1)
        self.assertAlmostEqual(len(xstretch)//2,len(x))

if __name__ == "__main__":
    unittest.main()