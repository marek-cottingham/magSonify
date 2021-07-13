import numpy as np
from scipy.interpolate.interpolate import interp1d

def generateTimeSeriesDates(start,end,timeUnit=np.timedelta64(1,'s'),num=None,spacing=None):
    """Generates a time series.
    Specify only {num} OR {spacing} exclusively.

    start:
        Datetime of start time
    end:
        Datetime of end time
    timeUnit:
        Unit of time to use. Default is 1 second.
    num:
        Number of points in time series.
    spacing:
        Spacing of points in time series.
    """
    start = np.datetime64(start)
    end = np.datetime64(end)
    intervalLength = end - start
    if num is not None and spacing is not None:
        raise ValueError("Only num or spacing should be specified, not both")
    if num is not None:
        t = np.linspace(
            0,
            intervalLength / timeUnit,
            num
        )
        time_series = TimeSeries(t,timeUnit,start)
    if spacing is not None:
        num = int(intervalLength/spacing)
        t = np.arange(0,num+1) * spacing
        time_series = TimeSeries(t,timeUnit,start)
    return time_series
    

class TimeSeries():
    def __init__(
        self,
        timeData,
        timeUnit=np.timedelta64(1,'s'),
        startTime = None
    ):
        """ Initialises time series from array of float, np.datetime64 or np.timedelta64
        timeUnit:
            The time unit to use, must be np.timedelta64
        """
        if timeData is None:
            pass
        timeData = np.array(timeData)
        if timeData.dtype.type == np.datetime64:
            # Store the start time and convert timeData to numpy.timedelta64 relative to the
            # start time
            if startTime is not None:
                startTime = timeData[0]
            timeData = timeData - startTime

        # Ensure start time is np.datetime64, not datetime.datetime
        startTime = np.datetime64(startTime)

        if timeData.dtype.type == np.timedelta64:
            # Convert time data to float, with units timeUnit
            # This ensures that the time can be manipulated using methods that cannot take
            # np.datetime64 as input
            timeData = timeData / timeUnit

        self.timeData = timeData
        self.timeUnit = timeUnit
        self.startTime = startTime

    def getMeanSampleInterval(self) -> np.timedelta64:
        """Return the mean interval between time points"""
        return self.getMeanSampleIntervalFloat() * self.timeUnit
    
    def getMeanSampleIntervalFloat(self) -> float:
        """Return the mean interval between time points in units timeUnit"""
        return float((self.timeData[-1] - self.timeData[0])/len(self.timeData))

    def asFloat(self) -> np.array((),dtype=np.float64):
        return self.timeData

    def asTimeDelta(self) -> np.array((),np.timedelta64):
        """Return the time data as np.timedelta64 since the start time"""
        return self.timeData * self.timeUnit

    def asDateTime(self) -> np.array((),np.datetime64):
        """Returns the time data as np.datatime64"""
        if self.startTime is None:
            raise ValueError("Cannot convert to datetime without starting time reference.")
        return self.asTimeDelta() + self.startTime

    def interpolate(self,factor):
        """ Convert the time series to a series with evenely space times over the same interval
        with {factor} times the original sample density.
        """
        self.timeData = np.linspace(
            self.timeData[0],
            self.timeData[-1],
            int(len(self.timeData) * factor)
        )
    
    def changeUnit(self,newTimeUnit):
        """ Change the units of time that the time series is expressed in to {newTimeUnit}
        """
        if newTimeUnit != self.timeUnit:
            self.timeData = self.timeData * (self.timeUnit / newTimeUnit)
            self.timeUnit = newTimeUnit


class DataSeries():
    def __init__(self,timeSeries,data):
        self.timeSeries = timeSeries
        self.data = data

    def fillNaN(self,const=0) -> None:
        """Fills nan values in the data with the constant {const}"""
        for i, d in enumerate(self.data):
            self.data[i] = np.nan_to_num(self.data[i],nan=const)

    def interpolate(self,ref_or_factor) -> None:
        """Interpolates the data and time series
        
        ref_or_factor:
            Either reference (TimeSeries or DataSeries) to interpolate data to or factor to multiply
            current TimeSeries density by. If reference is passed, s.TimeSeries will be set to the 
            new time series.
        """
        if isinstance(ref_or_factor,DataSeries):
            # If reference is a data series, extract it's time series
            ref_or_factor = ref_or_factor.timeSeries
        if isinstance(ref_or_factor,TimeSeries):
            # Set new times to the reference time series, with units and start time adjusted to match the current
            # time series
            try:
                newTimes = TimeSeries(ref_or_factor.asDateTime(),self.timeSeries.timeUnit,self.timeSeries.startTime)
            # If ref has no start time, consider it to be relative to the start time of the current time series
            except ValueError:
                newTimes = ref_or_factor.copy().changeUnit(self.timeSeries.timeUnit)
        else:
            # Set new times to an interpolation of the current time data
            newTimes = self.timeSeries.copy().interpolate(ref_or_factor)
        for i, d in enumerate(self.data):
            fd = interp1d(self.timeSeries.asFloat(),d,kind="cubic")
            self.data[i] = fd(newTimes.asFloat())

class DataSeries_1D(DataSeries):
    def __init___(self,timeSeries,x):
        self.timeSeries = timeSeries
        self.data = [x,]

class DataSeries_3D(DataSeries):
    def __init__(self,timeSeries,x,y,z):
        self.timeSeries = timeSeries
        self.data = [x,y,z]