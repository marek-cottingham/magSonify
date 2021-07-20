import context
context.get()

from datetime import datetime
from magSonify.MagnetometerData import THEMISdata
import numpy as np

mag = THEMISdata()

event2007_09_04 = (datetime(2007,9,4), datetime(2007,9,5))
event2008_12_07 = (datetime(2008,12,7), datetime(2008,12,10))
event2011_09_02 = (datetime(2011, 9, 2), datetime(2011, 9, 6))

# Import the satellite data, specifying which themis satellite to use
mag.importCdasAsync(
    *event2008_12_07,
    satellite='D'
)

# Sometimes CDAS has duplicate time entries, we remove all but the first in order to prevent
# errors when interpolating the data
mag.magneticField.removeDuplicateTimes()
mag.peemIdentifyMagnetosheath.removeDuplicateTimes()

# Interpolate the data to a consistent, know spacing
mag.interpolate_3s()

mag.magneticField.constrainAbsoluteValue(400)

# Compute the mean field, this is both to allow the mean field to be subtracted and for use later
# in .convertToMeanFieldCoordinates(). Note that the exact attribute name: .meanField must be 
# preserved in order for .convertToMeanFieldCoordinates() to work.
mag.meanField = mag.magneticField.runningAverage(timeWindow=np.timedelta64(35,"m"))
mag.magneticField = mag.magneticField - mag.meanField

mag.fillLessThanRadius(4)
mag.removeMagnetosheath()
mag.convertToMeanFieldCoordinates()

mag.magneticFieldMeanFieldCoordinates.fillNaN()

# Extract each of the field components as a 1D data set, perform the time stretch and output as
# audio
com = mag.magneticFieldMeanFieldCoordinates.extractKey(0)
com.phaseVocoderStretch(16)
com.normalise()
com.genMonoAudio("Example of com x16 with phase vocoder.wav")

pol = mag.magneticFieldMeanFieldCoordinates.extractKey(1)
pol.phaseVocoderStretch(16)
pol.normalise()
pol.genMonoAudio("Example of pol x16 with phase vocoder.wav")

tor = mag.magneticFieldMeanFieldCoordinates.extractKey(2)
tor.phaseVocoderStretch(16)
tor.normalise()
tor.genMonoAudio("Example of tor x16 with phase vocoder.wav")

# Disable the wavelet stretch output if it's taking too long
# exit()

com = mag.magneticFieldMeanFieldCoordinates.extractKey(0)
com.waveletStretch(16,0.5,16)
com.normalise()
com.genMonoAudio("Example of com x16 with wavelets.wav",sampleRate=44100//2)

pol = mag.magneticFieldMeanFieldCoordinates.extractKey(1)
pol.waveletStretch(16,0.5,16)
pol.normalise()
pol.genMonoAudio("Example of pol x16 with wavelets.wav",sampleRate=44100//2)

tor = mag.magneticFieldMeanFieldCoordinates.extractKey(2)
tor.waveletStretch(16,0.5,16)
tor.normalise()
tor.genMonoAudio("Example of tor x16 with wavelets.wav",sampleRate=44100//2)