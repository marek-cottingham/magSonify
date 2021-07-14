from datetime import datetime
from pyMagnetoSonify.TimeSeries import TimeSeries, generateTimeSeries
import pyMagnetoSonify as Sonify
import numpy as np

mag = Sonify.THEMISdata()
mag.importCDAS(
    datetime(2007,9,3),
    datetime(2007,9,4)
)

timeSeries_3s = generateTimeSeries(
    mag.magneticFieldData.timeSeries.getStart(),
    mag.magneticFieldData.timeSeries.getEnd(),
    spacing=np.timedelta64(3,'s')
)

mag.magneticFieldData.interpolate(timeSeries_3s)
mag.positionData.interpolate(mag.magneticFieldData)

mag.magneticFieldData.constrainAbsoluteValue(400)
mag.meanField = mag.magneticFieldData.runningAverage(timeWindow=np.timedelta64(35,"m"))
mag.magneticFieldData = mag.magneticFieldData - mag.meanField
mag.fillLessThanRadius(5)

mag.magneticFieldData.fillNaN()