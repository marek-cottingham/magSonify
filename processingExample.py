from datetime import datetime
from pyMagnetoSonify.MagnetometerData import THEMISdata
from pyMagnetoSonify.TimeSeries import generateTimeSeries
import numpy as np
from ai import cdas
from pyMagnetoSonify.initialise import cdas_cache_path

#cdas.set_cache("False",cdas_cache_path)

mag = THEMISdata()

mag.importCdasAsync(
    datetime(2007,9,4),
    datetime(2007,9,5)
)

mag.interpolate_3s()
mag.magneticField.constrainAbsoluteValue(400)
mag.meanField = mag.magneticField.runningAverage(timeWindow=np.timedelta64(35,"m"))
mag.magneticField = mag.magneticField - mag.meanField
mag.fillLessThanRadius(6)
mag.convertToMeanFieldCoordinates()

mag.magneticFieldMeanFieldCorrdinates.fillNaN()

com = mag.magneticFieldMeanFieldCorrdinates.extractKey(0)
com.phaseVocoderStretch(16)
com.normalise()
com.genMonoAudio("Example of com x16 with phase vocoder.wav")

pol = mag.magneticFieldMeanFieldCorrdinates.extractKey(1)
pol.phaseVocoderStretch(16)
pol.normalise()
pol.genMonoAudio("Example of pol x16 with phase voccoder.wav")