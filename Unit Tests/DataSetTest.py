
import context
context.get()

from datetime import datetime
from pyMagnetoSonify.TimeSeries import TimeSeries
from pyMagnetoSonify.TimeSeries import generateTimeSeries
import unittest
import numpy as np
import os

class TimeSeriesTest(unittest.TestCase):
    def initialise(self):
        # Expect 1 sample every 27 s -> every 13.5 float
        series0 = generateTimeSeries(
            datetime(2020,4,2),
            datetime(2020,4,3,6),
            timeUnit=np.timedelta64(2,'s'),
            number = 4001
        )
        series1 = generateTimeSeries(
            datetime(2020,4,2),
            datetime(2020,4,3,6),
            timeUnit=np.timedelta64(1,'h'),
            spacing=np.timedelta64(36,'s')
        )
        return (series0,series1)

    def test_generatorNum(self):
        series = self.initialise()
        self.assertAlmostEqual(series[0].times[3],13.5*3)
        self.assertAlmostEqual(series[0].times[-1],54000)
        self.assertEqual(series[0].startTime,np.datetime64(datetime(2020,4,2)))
        self.assertEqual(series[0].timeUnit,np.timedelta64(2,'s'))
        self.assertEqual(len(series[0].times),4001)

    def test_generatorSpacing(self):
        series = self.initialise()
        self.assertAlmostEqual(series[1].times[3],0.03)
        self.assertAlmostEqual(series[1].times[-1],30.0)
        self.assertEqual(series[1].startTime,np.datetime64(datetime(2020,4,2)))
        self.assertEqual(series[1].timeUnit,np.timedelta64(1,'h'))
        self.assertEqual(len(series[1].times),3001)

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    unittest.main()