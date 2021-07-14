from datetime import datetime
from pyMagnetoSonify.MagnetometerData import THEMISdata
from pyMagnetoSonify.TimeSeries import generateTimeSeries
import numpy as np

mag = THEMISdata()
mag.importCDAS(
    datetime(2007,9,4),
    datetime(2007,9,5)
)

timeSeries_3s = generateTimeSeries(
    mag.magneticField.timeSeries.getStart(),
    mag.magneticField.timeSeries.getEnd(),
    spacing=np.timedelta64(3,'s')
)

mag.magneticField.interpolate(timeSeries_3s)
mag.position.interpolate(mag.magneticField)

mag.magneticField.constrainAbsoluteValue(400)
mag.meanField = mag.magneticField.runningAverage(timeWindow=np.timedelta64(35,"m"))
mag.magneticField = mag.magneticField - mag.meanField
mag.fillLessThanRadius(6)
mag.convertToMeanFieldCoordinates()

mag.magneticFieldMeanFieldCorrdinates.fillNaN()

ax = mag.magneticFieldMeanFieldCorrdinates.extractKey(1)
ax.phaseVocoderStretch(16)
ax.normalise()
ax.genMonoAudio("newProcessing phase vocoder.wav")