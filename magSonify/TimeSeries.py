from __future__ import annotations
from datetime import datetime
import typing
import numpy as np
from numpy import datetime64, timedelta64

def generateTimeSeries(
    start: datetime64,
    end: datetime64,
    timeUnit: timedelta64 = timedelta64(1,'s'),
    number: int = None,
    spacing: timedelta64 = None
):
    """Generates a time series.
    Specify only ``num`` OR ``spacing`` exclusively.

    :param datetime64 start:
        Datetime of start time
    :param datetime64 end:
        Datetime of end time
    :param timedelta64 timeUnit:
        Unit of time to use. Default is 1 second.
    :param int number:
        Number of points in time series.
    :param timedelta64 spacing:
        Spacing of points in time series.
    """
    start = np.datetime64(start)
    end = np.datetime64(end)
    intervalLength = end - start

    if number is not None and spacing is not None:
        raise ValueError("Only num or spacing should be specified, not both")

    if number is not None:
        return _GenerateTimeSeriesWithNumber(start, timeUnit, number, intervalLength)

    if spacing is not None:
        return _GenerateTimeSeriesWithSpacing(start, timeUnit, spacing, intervalLength)

def _GenerateTimeSeriesWithSpacing(start, timeUnit, spacing, intervalLength):
    number = int(intervalLength/spacing)
    t = np.arange(0,number+1) * spacing
    return TimeSeries(t,timeUnit,start)

def _GenerateTimeSeriesWithNumber(start, timeUnit, number, intervalLength):
    t = np.linspace(
            0,
            intervalLength / timeUnit,
            number
        )
    return TimeSeries(t,timeUnit,start)
    

class TimeSeries():
    """Represents a series of time points and allows for manipulation.

        :param timeData:
            Array of ``float``, ``np.datetime64``, ``datetime.datetime`` or ``np.timedelta64`` 
            represeting the time data
        :param timeUnit:
            The time unit to use, must be ``np.timedelta64``
        :param startTime:
            Datetime to construct the series relative to
        """
    def __init__(
        self,
        times,
        timeUnit=np.timedelta64(1,'s'),
        startTime = None
    ):
        

        times = np.array(times)

        timeTypeIsDatetime = (type(times[0]) == type(datetime(2020,1,1)))
        if timeTypeIsDatetime:
            times = np.array(times,dtype=np.datetime64)
        
        if times.dtype.type == np.datetime64:
            if startTime is None:
                startTime = times[0]
            times = times - startTime

        if startTime is not None:
            startTime = np.datetime64(startTime)

        # This will run during the import process for both datetime64 and timedelta64
        if times.dtype.type == np.timedelta64:
            # Using float representation of times allows use of numpy functions which do not accept 
            #   datetime64
            times = times / timeUnit

        self.times = times
        """A numpy array of times stored as ``np.float``"""
        self.timeUnit = timeUnit
        """The time unit used stored as ``np.timedelta64``"""
        self.startTime = startTime
        """The starting time of the series stored as ``np.datetime64``"""

    def _raiseIfNoStartTime(self) -> None:
        if self.startTime is None: 
            raise ValueError("Time series is defined only for relative times (startTime is None)")

    def getStart(self) -> np.datetime64:
        self._raiseIfNoStartTime()
        return self.startTime

    def getEnd(self) -> np.datetime64:
        self._raiseIfNoStartTime()
        return self.startTime + self.times[-1] * self.timeUnit

    def getMeanInterval(self) -> np.timedelta64:
        return self.getMeanIntervalFloat() * self.timeUnit
    
    def getMeanIntervalFloat(self) -> float:
        return float((self.times[-1] - self.times[0])/len(self.times))

    def asFloat(self) -> np.array( () ,np.float64):
        """:rtype: `np.array(dtype = np.timedelta64)`"""
        return self.times

    def asTimedelta(self) -> np.array( () ,np.timedelta64):
        """:rtype: `np.array(dtype = np.timedelta64)`"""
        return self.times * self.timeUnit

    def asDatetime(self) -> np.array( () ,np.datetime64):
        """:rtype: `np.array(dtype = np.datetime64)`"""
        self._raiseIfNoStartTime()
        return self.asTimedelta() + self.startTime

    def asNumpy(self) -> np.array:
        """Returns the most suitable numpy represenation"""
        if self.startTime is not None:
            return self.asDatetime()
        return self.asTimedelta()

    def argFirstAfter(self,datetime) -> int:
        """Returns the argument of the first time occuring after ``datetime``"""
        datetime = np.datetime64(datetime)
        self._raiseIfNoStartTime()
        val = (datetime - self.startTime) / self.timeUnit
        return np.argmax(self.times - val)

    def interpolate(self,factor) -> None:
        """Convert the time series to a series with evenely space times over the same interval
        with ``factor`` times the original sample density.
        """
        self.times = np.linspace(
            self.times[0],
            self.times[-1],
            int(len(self.times) * factor)
        )
    
    def changeUnit(self,newTimeUnit: np.timedelta64) -> None:
        """Change the units of time that the time series is expressed in to ``newTimeUnit``
        """
        if newTimeUnit != self.timeUnit:
            self.times = self.times * (self.timeUnit / newTimeUnit)
            self.timeUnit = newTimeUnit

    def copy(self) -> TimeSeries:
        """Copies the time series"""
        return type(self)(self.times.copy(),self.timeUnit,self.startTime)

    def __eq__(self,other: TimeSeries) -> bool:
        """
        Supports equality testing::
            
            firstTimeSeries == secondTimeSeries
        """
        return (
            self is other 
            or  np.all(self.asNumpy() == other.asNumpy())
        )
    
    def __getitem__(self,subscript:slice) -> TimeSeries:
        """
        Supports getting a subset of times using a slice::

            myNewTimeSeries = myTimeSeries[100:200]
        """
        if isinstance(subscript,slice):
            return type(self)(self.times[subscript],self.timeUnit,self.startTime)