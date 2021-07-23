

if __name__ == "__main__":
    import context
    context.get()

import os
import unittest
from datetime import datetime

import numpy as np
from magSonify.TimeSeries import TimeSeries, generateTimeSeries


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
        spacing = np.timedelta64(1,'s').astype('timedelta64[ns]')/44100
        series2 = generateTimeSeries(
            datetime(2007,1,1,12,0,0),
            datetime(2007,1,1,12,0,10),
            spacing=spacing
        )
        return (series0,series1,series2)

    def test_generatorNum(self):
        allSeries = self.initialise()
        self.assertAlmostEqual(allSeries[0].times[3],13.5*3)
        self.assertAlmostEqual(allSeries[0].times[-1],54000)
        self.assertEqual(allSeries[0].startTime,np.datetime64(datetime(2020,4,2)))
        self.assertEqual(allSeries[0].timeUnit,np.timedelta64(2,'s'))
        self.assertEqual(len(allSeries[0].times),4001)

    def test_generatorSpacing(self):
        allSeries = self.initialise()
        self.assertAlmostEqual(allSeries[1].times[3],0.03)
        self.assertAlmostEqual(allSeries[1].times[-1],30.0)
        self.assertEqual(allSeries[1].startTime,np.datetime64(datetime(2020,4,2)))
        self.assertEqual(allSeries[1].timeUnit,np.timedelta64(1,'h'))
        self.assertEqual(len(allSeries[1].times),3001)

        series2 = allSeries[2]
        self.assertAlmostEqual(series2.times[3],3/44100)

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    unittest.main()
