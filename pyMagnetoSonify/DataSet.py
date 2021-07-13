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
            if startTime is not None:
                raise ValueError(
                    (f"Start time is specified twice." 
                    "Data series: {timeData[0]} Passed by user: {startTime}")
                )
            # Store the start time and convert timeData to numpy.timedelta64 relative to the
            # start time
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

    def asTimeDelta(self) -> np.timedelta64:
        """Return the time data as np.timedelta64 since the start time"""
        return self.timeData * self.timeUnit

    def asDateTime(self) -> np.datetime64:
        """Returns the time data as np.datatime64"""
        return self.asTimeDelta() + self.startTime