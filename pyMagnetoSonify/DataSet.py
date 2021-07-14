from operator import add, mul, neg, sub
from pyMagnetoSonify.Audio import writeoutAudio
import numpy as np
from scipy.interpolate.interpolate import interp1d
from scipy.ndimage.filters import uniform_filter1d
from . import TimeSeries
from . import DataSet_1D

class DataSet():
    def __init__(self,timeSeries: TimeSeries,data):
        self.timeSeries = timeSeries
        self.data = data

    def items(self):
        """Returns a list of tuples, containg index-data pairs for each element in DataSeries.data
        """
        try:
            dataInterateOver = self.data.items()
        except AttributeError:
            dataInterateOver = enumerate(self.data)
        return dataInterateOver
    
    def keys(self):
        """Returns all keys in DataSeries.data"""
        return [x[0] for x in self.items()] 

    def fillNaN(self,const=0) -> None:
        """Fills nan values in the data with the constant {const}"""
        for i, d in self.items():
            self.data[i] = np.nan_to_num(d,nan=const)

    def constrainAbsoluteValue(self,max):
        """Limits the data to within bounds of -max to +max, values outside are set to -max or +max
        """
        for i, d in self.items():
            d[d>max] = max
            d[d<-max] = -max

    def interpolate(self,ref_or_factor) -> None:
        """Interpolates the data and time series
        
        ref_or_factor:
            Either reference (TimeSeries or DataSeries) to interpolate data to or factor to multiply
            current TimeSeries density by. If reference is passed, s.TimeSeries will be set to the 
            new time series.
        """
        if isinstance(ref_or_factor,DataSet):
            ref_or_factor = ref_or_factor.timeSeries

        newTimes = self._getInterpolationTimeSeries(ref_or_factor)

        for i, d in self.items():
            fd = interp1d(self.timeSeries.asFloat(),d,kind="cubic")
            self.data[i] = fd(newTimes.asFloat())

    def _getInterpolationTimeSeries(self, ref_or_factor):
        if isinstance(ref_or_factor,TimeSeries):
            if ref_or_factor.startTime is not None:
                newTimes = TimeSeries(
                    ref_or_factor.asDatetime(),
                    self.timeSeries.timeUnit,
                    self.timeSeries.startTime
                )
            else:
                newTimes = ref_or_factor.copy()
                newTimes.changeUnit(self.timeSeries.timeUnit)
        else: #Treat ref_or_factor as number
            newTimes = self.timeSeries.copy()
            newTimes.interpolate(ref_or_factor)
        return newTimes

    def runningAverage(self,samples=None,timeWindow=None):
        """Returns a running average of the data with window size {samples} or period {timeWindow}.
        Pass only {samples} OR {timeWindow} exculsively.
        """
        if timeWindow is not None:
            samples = int(timeWindow / self.timeSeries.getMeanInterval())

        if samples == 0:
            raise ValueError("Cannot generate a running average for an interval of 0 samples.")

        def _runningAverage(d):
            mean_d = uniform_filter1d(
                d,samples,mode='constant',cval=0, origin=0
            )
            # First samples/2 values are distorted by edge effects, so we set them to np.nan
            mean_d[0:samples//2] = np.nan
            mean_d[-samples//2+1:] = np.nan
            return mean_d

        meanData = self._iterate(_runningAverage)
        return DataSet(self.timeSeries,meanData)

    def extractKey(self,key):
        """Extract element from data[key] in new DataSet"""
        return DataSet_1D.DataSet_1D(self.timeSeries,self.data[key])

    def genMonoAudio(self,key,file,**kwargs):
        writeoutAudio(self.data[key],file,**kwargs)

    def _iterate(self,lamb):
        """Execute function {lamb} on each element in self.data"""
        res = {}
        for i,d in self.items():
            res[i] = lamb(d)
        return res

    def _iteratePair(self,other,lamb):
        """Execute function {lamb} on each element pair in self.data and self.other with the same 
        keys
        """
        self._raiseIfTimeSeriesNotEqual(other)
        res = {}
        for i, d in self.items():
            res[i] = lamb(d,other.data[i])
        return DataSet(self.timeSeries,res)

    def _raiseIfTimeSeriesNotEqual(self, other):
        if (self.timeSeries != other.timeSeries):
            raise ValueError("Datasets do not have the same time series")
    
    def __add__(self,other):
        return self._iteratePair(other,add)

    def __sub__(self,other):
        return self._iteratePair(other,sub)

    def __neg__(self):
        return self._iterate(neg)
        
class DataSet_3D(DataSet):
    def __init__(self,timeSeries: TimeSeries,data):
        indiciesInKeys = 0 in data.keys() and 1 in data.keys and 2 in data.keys
        if not indiciesInKeys:
            raise AttributeError("Data must contain the keys 0, 1 and 2")
        super().__init__(timeSeries,data)

    def genStereoAudio(self,file,**kwargs):
        audio = np.array([
            self.data[0] + 0.5 * self.data[1],
            0.5 * self.data[1] + self.datca[2],
        ])
        writeoutAudio(audio.T,file,**kwargs)

    def cross(self,other):
        """Computes the cross product of 3D datasets"""
        self._raiseIfTimeSeriesNotEqual(other)
        res = {}
        sd = self.data
        od = other.data
        res[0] = sd[1] * od[2] - sd[2] * od[1]
        res[1] = sd[2] * od[0] - sd[0] * od[2]
        res[2] = sd[0] * od[1] - od[1] * sd[0]
        return DataSet_3D(self.timeSeries,res)

    def dot(self,other):
        """Computes to dot product of 3D datasets"""
        self._raiseIfTimeSeriesNotEqual(other)
        res = {}
        for i in (0,1,2):
            res[i] = self.data[i] * other.data[i]
        return DataSet_3D(self.timeSeries,res)