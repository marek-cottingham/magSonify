import numpy as np


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
        if isinstance(timeData,np.datetime64):
            # Store the start time and convert timeData to numpy.timedelta64 relative to the
            # start time
            if startTime is not None:
                startTime = timeData[0]
            timeData = timeData - startTime

        # Ensure start time is np.datetime64, not datetime.datetime
        startTime = np.datetime64(startTime)

        if isinstance(timeData,np.timedelta64):
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
        pass

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
    def __init__(self):
        raise NotImplemented

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
            ref_or_factor = ref_or_factor.TimeSeries
        if isinstance(ref_or_factor,TimeSeries):
            # Set new times to the reference time series, with units and start time adjusted to match the current
            # time series
            try:
                newTimes = TimeSeries(ref_or_factor.asDateTime(),self.TimeSeries.timeUnit,self.TimeSeries.startTime)
            # If ref has no start time, consider it to be relative to the start time of the current time series
            except ValueError:
                newTimes = ref_or_factor.copy().changeUnit(self.TimeSeries.timeUnit)
        else:
            # Set new times to an interpolation of the current time data
            newTimes = self.TimeSeries.interpolate(ref_or_factor)
        raise NotImplemented

class DataSeries_1D(DataSeries):
    def __init___(self,TimeSeries,x):
        self.TimeSeries = TimeSeries.copy()
        self.data = [x,]

class DataSeries_3D(DataSeries):
    def __init__(self,TimeSeries,x,y,z):
        self.TimeSeries = TimeSeries.copy()
        self.data = [x,y,z]