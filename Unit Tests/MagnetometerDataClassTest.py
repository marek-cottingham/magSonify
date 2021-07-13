

from datetime import timedelta
import numpy
from context import Sonify
import os
import unittest
import pandas as pd
import numpy as np
from numpy import NaN, isnan
from numpyunittest import numpyunittest
if (3 == 4):
    import Sonify

class MagnetometerData_Tests(numpyunittest):
    def alternative_runningAverage(s):
        s.meanB = []
        df = pd.DataFrame(s.b,columns=("bx","by","bz"))
        df.rolling(window=200,center=True).mean()
        for i,name in zip((0,1,2),("bx","by","bz")):
            s.b[i] = df[name].to_numpy()

    def test_runningAverage(s):
        mag = Sonify.MagnetometerData()
        for i in range(3):
            mag.b[i] = np.array([
                0+i,1,2,0,1,2,3,3,3
            ],dtype=np.float64)
        mag.runningAverage(3)
        for i in range(3):
            testArray = np.array((NaN,(3+i)/3,1,1,1,2,8/3,3,NaN),dtype=np.float64)
            s.assertNumpyClose(mag.meanB[i],testArray)

    def test_runningAverageWindow(s):
        mag = Sonify.MagnetometerData(2000)
        mag = Sonify.MagnetometerData(
            numpy.timedelta64(int(3.056*1000),'ms')
        )
        for i in range(3):
            mag.b[i] = np.ones(1000)
        mag.t = np.arange(1000)*3
        n = mag.runningAverageWindow(34000)
        s.assertEqual(n,11)
        n = mag.runningAverageWindow(np.timedelta64(2,'m'))
        s.assertEqual(n,39)
        n = mag.runningAverageWindow(np.timedelta64(10000,'ms'))
        s.assertEqual(n,3)
        n = mag.runningAverageWindow(timedelta(seconds=27,milliseconds=845))
        s.assertEqual(n,9)
            

class GOESdata_Tests(unittest.TestCase):
    def suspended_test_readCSV(s):
        sampleFile = "GOESdata_readCSV.csv"
        sampleFolder = "GOESdata_readCSV"
        mag = Sonify.GOESdata()
        mag.read_csv(sampleFile,sampleFolder,skiprows=3)
        df = mag.dfChunks[0]
        s.assertEqual( df["HP_1"][0], 90.15 )
        s.assertTrue( isnan(df["HE_1"][0]) )
        s.assertTupleEqual( tuple(df.columns), ("HP_1","HE_1","HN_1") )

class THEMISdata_Tests(numpyunittest):
    def asserts_readCSV(s,mag):
        s.assertEqual(mag.b[0][0],56.1920)
        s.assertEqual(mag.b[1][8],772.33549)
        s.assertTrue(isnan(mag.b[2][21]))
        s.assertEqual(len(mag.t),28)
        s.assertEqual(len(mag.b[0]),28)
        s.assertEqual(len(mag.b[1]),28)
        s.assertEqual(len(mag.b[2]),28)

    def test_readCSV(s):
        sampleFile = "THEMISdata_readCSV.txt"
        sampleFolder = "THEMISdata_readCSV"
        mag = Sonify.THEMISdata()
        mag.readCSV(sampleFile,sampleFolder,skiprows=4)
        s.asserts_readCSV(mag)

    def test_readFolder(s):
        sampleFolder = "THEMISdata_readCSV"
        mag = Sonify.THEMISdata()
        mag.readFolder(sampleFolder,skiprows=4)
        s.asserts_readCSV(mag)

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    unittest.main()
    