from __future__ import annotations

from operator import add, neg, sub
from typing import List, Tuple
from .Audio import writeoutAudio
import numpy as np
from scipy.interpolate.interpolate import interp1d
from scipy.ndimage.filters import uniform_filter1d
from .TimeSeries import TimeSeries
from copy import deepcopy

class DataSet():
    """Represents a data set with multiple data series sampled at common time points.
    
    :param timeSeries:
        Time series representing the sampling times.
    :param data:
        Dictionary of numpy arrays containing the data. Convention is for 'x', 'y' and 'z' axes 
        to be represented under the keys ``int`` ``0``, ``1`` and ``2`` respectively if they are 
        present. Array should be 1D.
    """
    def __init__(self,timeSeries: TimeSeries,data):
        # We use a copy of the time series here in order to prevent issues occuring due to multiple
        # data sets sharing the same time series.
        self.timeSeries: TimeSeries = timeSeries.copy()
        """:class:`TimeSeries` represeting the sampling times for the dataset"""

        data = self._convertToDictIfArray(data)
        self.data: dict = data
        """Dictionary of numpy arrays containing the data."""

    def _convertToDictIfArray(self,data):
        try:
            data.items()
        except AttributeError:
            data = dict(enumerate(data))
        return data

    def items(self) -> enumerate:
        """Returns an iterable containing all key-value pairs in :attr:`data`.
        Equivalent to ``self.data.items()``
        """
        return self.data.items()

    def keys(self) -> enumerate:
        """Returns an iterable containing all keys in :attr:`data`.
        Equivalent to ``self.data.keys()``
        """
        return self.data.keys()

    def fillNaN(self,const=0) -> None:
        """Fills ``NaN`` values in the data with the constant ``const``"""
        for i, d in self.items():
            self.data[i] = np.nan_to_num(d,nan=const)

    def constrainAbsoluteValue(self,max) -> None:
        """Limits the data to within bounds of ``-max`` to ``+max``, values outside 
        are set to ``-max`` or ``+max`` respectively.
        """
        for i, d in self.items():
            d[d>max] = max
            d[d<-max] = -max

    def interpolateFactor(self,factor: float) -> None:
        """Interpolates the data set, increasing the sample time resolution by 
        ``factor`` times and evenly spacing the samples. 
        If ``factor < 1``, reduces sample resolution.
        """
        newTimes = self.timeSeries.copy()
        newTimes.interpolate(factor)
        self._interpolate(newTimes)

    def interpolateReference(self,ref: TimeSeries) -> None:
        """Interpolates the data set such that the new sample times are those of 
        the time series ``ref``.

        .. note::
            This can extrapolate outside the data range - there is no range checking. 
            This extrapolation is not reliable and should only be allowed for points very slightly 
            outside the data range.
        """

        self._setupTimeSeriesForInterpolation(ref)
        self._interpolate(ref)

    def _interpolate(self, newTimes: TimeSeries):
        for i, d in self.items():
            fd = interp1d(self.timeSeries.asFloat(),d,kind="cubic",fill_value="extrapolate")
            self.data[i] = fd(newTimes.asFloat())

        self.timeSeries = newTimes

    def _setupTimeSeriesForInterpolation(self, ref: TimeSeries) -> None:
        """Sets up :attr:`timeSeries` for interpolation by matching the units and 
        start time of ``ref``"""
        if ref.startTime is not None:
            self.timeSeries = TimeSeries(
                self.timeSeries.asDatetime(),
                ref.timeUnit,
                ref.startTime
            )
        else:
            self.timeSeries.changeUnit(ref.timeUnit)


    def runningAverage(self,samples=None,timeWindow=None) -> DataSet:
        """Returns a running average of the data with window size ``samples`` or period ``timeWindow``.
        Pass only ``samples`` OR ``timeWindow`` exculsively.
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
        return type(self)(self.timeSeries,meanData)

    def extractKey(self,key) -> DataSet_1D:
        """Extract element from ``self.data[key]`` in new data set"""
        return DataSet_1D(self.timeSeries,deepcopy(self.data[key]))

    def genMonoAudio(self,key,file,sampleRate=44100) -> None:
        """Generate a mono audio file from data in the series ``self.data[key]``
        
        :param int sampleRate:
            The sample rate of the output audio, default is 44100.
        """
        writeoutAudio(self.data[key],file,sampleRate)

    def copy(self) -> DataSet:
        """Returns a copy of the data set"""
        return type(self)(self.timeSeries,deepcopy(self.data))

    def fillFlagged(self,flags: np.array,const=0) -> None:
        """Fill values according to an array of flags, across all components

        :param flags: 
            `Boolean array index 
            <https://numpy.org/devdocs/reference/arrays.indexing.html#boolean-array-indexing>`_
            of same length as the data set, identifying the indicies to fill.
        :param const:
            The value to fill with.
        """
        for i,d in self.items():
            d[flags] = const

    def removeDuplicateTimes(self) -> None:
        """Removes duplicate values in the time series by deleting all but the first occurence.
        Removes correspoinding points in each component.
        """
        unique, index = np.unique(self.timeSeries.times, return_index=True)
        self.timeSeries.times = unique
        for i,d in self.items():
            self.data[i] = d[index]

    def _iterate(self,lamb: function,replace=False) -> dict:
        """Execute function ``lamb`` on each component in :attr:`data`
        
        :param lamb:
            Function to perform on each component, should accept a single parameter which is a 
            1D numpy array and return an array of the same shape as output.
        :type lamb: function
        :return: 
            A dictionary of numpy arrays with the same keys as in :attr:`data`, unless 
            ``replace=True``, in which case returns ``None``.
        :rtype: ``dict`` | ``None``
        """
        newData = {}
        for i,d in self.items():
            if replace:
                self.data[i] = lamb(d)
            else:
                newData[i] = lamb(d)
        if replace:
            return None
        return newData

    def _iteratePair(self,other: DataSet,lamb: function) -> DataSet:
        """Execute function ``lamb`` on each component pair in ``self.data`` and ``other.data`` 
        with the same keys. ``self`` and ``other`` must have the same time series and same keys in 
        :attr:`data`.

        :param lamb:
            Performed on each component, should accept two parameters which are 
            1D numpy arrays of the same shape and return an array of the same shape as output.
        :type lamb: function
        """
        self._raiseIfTimeSeriesNotEqual(other)
        res = {}
        for i, d in self.items():
            res[i] = lamb(d,other.data[i])
        return type(self)(self.timeSeries,res)

    def _raiseIfTimeSeriesNotEqual(self, other):
        if (self.timeSeries != other.timeSeries):
            raise ValueError("Datasets do not have the same time series")

    def __getitem__(self,subscript):
        """
        Supports using slices to extract a subsection along the time axis::

            myNewDataSet   = myDataSet[100:200]
            myOtherDataSet = myDataSet[200:None:3]
        """
        if isinstance(subscript,slice):
            res = self._iterate(
                lambda series: series[subscript]
            )
            return type(self)(self.timeSeries[subscript],res)
    
    def __add__(self,other) -> DataSet:
        """
        Supports addition: ``sumDataSet = firstDataSet + secondDataSet``

        Requires: ``firstDataSet.timeSeries == secondDataSet.timeSeries``
        """
        return self._iteratePair(other,add)

    def __sub__(self,other) -> DataSet:
        """Supports subtraction: ``diffDataSet = firstDataSet - secondDataSet```"""
        return self._iteratePair(other,sub)

    def __neg__(self) -> DataSet:
        """Supports negation: ``negDataSet = - DateSet``"""
        res = self._iterate(neg)
        return type(self)(self.timeSeries,res)

from .DataSet_1D import DataSet_1D
        
class DataSet_3D(DataSet):
    """Represents a data set with multiple data series sampled at common time points.
    
    :param timeSeries:
        Time series representing the sampling times.
    :param data:
        Dictionary of numpy arrays containing the data. The dictionary must have the keys
        ``int`` ``0``, ``1`` and ``2`` which represent the 'x', 'y' and 'z' axes respectively. 
        Array should be 1D. Other keys may be included, although these will be ignored by vector 
        specific methods, eg. :meth:`cross`, :meth:`dot`.
    """
    def __init__(self,timeSeries: TimeSeries,data):
        try:
            indiciesInKeys = 0 in data.keys() and 1 in data.keys() and 2 in data.keys()
        except AttributeError: # Raised when data is list not dictionary
            indiciesInKeys = len(tuple(enumerate(data))) >= 3
        if not indiciesInKeys:
            raise AttributeError("Data must contain the keys 0, 1 and 2")
        super().__init__(timeSeries,data)

    def genStereoAudio(self,file,sampleRate=44100) -> None:
        """Generates a stereo audio output in the specified file"""
        audio = np.array([
            self.data[0] + 0.5 * self.data[1],
            0.5 * self.data[1] + self.datca[2],
        ])
        writeoutAudio(audio.T,file,sampleRate)

    def cross(self,other) -> DataSet_3D:
        """Computes the cross product of 3D datasets"""
        self._raiseIfTimeSeriesNotEqual(other)
        res = {}
        sd = self.data
        od = other.data
        res[0] = sd[1] * od[2] - sd[2] * od[1]
        res[1] = sd[2] * od[0] - sd[0] * od[2]
        res[2] = sd[0] * od[1] - od[1] * sd[0]
        return DataSet_3D(self.timeSeries,res)

    def dot(self,other) -> DataSet_3D:
        """Computes the dot product of 3D datasets"""
        self._raiseIfTimeSeriesNotEqual(other)
        res = {}
        for i in (0,1,2):
            res[i] = self.data[i] * other.data[i]
        return DataSet_3D(self.timeSeries,res)

    def makeUnitVector(self) -> None:
        """Normalises the 3D vector to length 1, giving the unit vector"""
        sd = self.data
        vectorMagnitude = sd[0] ** 2 + sd[1] ** 2 + sd[2]**2
        vectorMagnitude = vectorMagnitude**(1/2)
        divideByMagnitude = lambda series: series / vectorMagnitude
        self._iterate(divideByMagnitude,replace=True)

    def coordinateTransform(self,xBasis,yBasis,zBasis) -> DataSet_3D:
        """Performs a coordinate transform to a system with the specified basis vectors.
        
        :param '_Basis':
            A basis vector, specified as a unit vectior which varies over time. Must be expressed 
            in the original coordinate system.
        :type '_Basis': :class:`DataSet_3D`
        """
        bases = [xBasis,yBasis,zBasis]
        res = {}
        sd = self.data
        for i, basis in enumerate(bases):
            self._raiseIfTimeSeriesNotEqual(basis)
            res[i] = sd[0] * basis.data[0] + sd[1] * basis.data[1] + sd[2] * basis.data[2]
        return DataSet_3D(self.timeSeries,res)