from .paulstretch_mono import paulstretch
from .TimeSeries import TimeSeries
from .DataSet import DataSet
import numpy as np
from .wavelets import transform, wavelets
import audiotsm
from audiotsm.io.array import ArrayReader, ArrayWriter

class DataSet_1D(DataSet):
    def __init__(self,timeSeries: TimeSeries,x):
        self.timeSeries = timeSeries
        self.data = [x,]

    @property
    def x(self):
        return self.data[0]

    @x.setter
    def x(self,x):
        self.data[0] = x

    def genMonoAudio(self, file, **kwargs):
        return super().genMonoAudio(0, file, **kwargs)
 
    def normalise(self,maxAmplitude=1):
        self.x = self.x / np.max(np.abs(self.x)) * maxAmplitude

    def waveletPitchShift(
            self,
            shift=1,
            scaleLogSpacing=0.125,
            interpolateFactor = None,
            maxNumberSamples = 1200,
            wavelet=wavelets.Morlet(),
            preserveScaling=False
        ) -> None:
        """Pitch shifts the data on specified axes by {shift} times using continous wavlet transform.

        Parameters
        ----------
        shift:
            The multiple by which to shift the pitch of the input field.
        scaleLogSpacing:
            Scale spacing in log space, a lower value leads to higher
            resolution in frequency space and more processing time.
        interpolateFactor:
            If not None, specifies the facator by which the density of the coefficients should be
            increased. Used when generating time stretched audio.
        maxNumberSamples:
            The maximum number of samples for the largest scale in the wavelet transform, used to
            prevent computations for inaubidle frequencies.
        wavelet:
            Wavelet function to use. If none is given, the Morlet wavelet will be used by default.
        preserveScaling:
            Whether to preserve the scaling of the data when outputing.
        """

        sampleSeperation = self.timeSeries.getMeanIntervalFloat()
        self.fillNaN()

        scales = transform.generateCwtScales(
            maxNumberSamples,
            len(self.x),
            scaleLogSpacing,
            sampleSeperation,
            wavelet,
        )
        coefficients = transform.cwt(self.x,scales,sampleSeperation,wavelet)

        self.coefficients = coefficients

        # Rescale the coefficients as in
        #   A Wavelet-based Pitch-shifting Method, Alexander G. Sklar
        #   https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.70.5079&rep=rep1&type=pdf

        magnitude = np.abs(coefficients)
        phase = np.unwrap(np.angle(coefficients),axis=1)

        if interpolateFactor is not None:
            magnitude, phase = transform.interpolateCoeffsPolar(
                magnitude,phase,interpolateFactor
            )
            self.timeSeries.interpolate(interpolateFactor)

        coefficients_shifted = magnitude * np.exp(1j * phase * shift)

        self.coefficients_shifted = coefficients_shifted

        # Scaling constants are generally redudant if generating audio as data will be normalised
        if preserveScaling:
            rx = transform.icwt(
                coefficients_shifted,
                scaleLogSpacing,
                sampleSeperation,
                wavelet.C_d,
                wavelet.time(0)
            )
        else:
            rx = transform.icwt(coefficients_shifted)

        self.x = np.real(rx)

    def paulStretch(self,stretch,timeWindow=0.015):
        """ Stretches the data according the paulstretch algorithm
        stretch:
            The factor by which to stretch the data
        timeWindow:
            The window size to be used by the paulstrtch algorithm. A timeWindow of 0.1 is
            equivalent to a window of 4410 data points.
        """
        self.timeSeries.interpolate(stretch)
        self.x = paulstretch(self.x,stretch,timeWindow)

    def phaseVocoderStretch(self,stretch,frameLength=512,synthesisHop=None):
        if synthesisHop is None:
            synthesisHop = frameLength//16
        reader = ArrayReader(np.array((self.x,)))
        writer = ArrayWriter(reader.channels)
        timeSeriesModification = audiotsm.phasevocoder(
            reader.channels,
            speed = 1/stretch,
            frame_length=frameLength,
            synthesis_hop=synthesisHop,
        )
        timeSeriesModification.run(reader, writer)
        self.x = writer.data.flatten()

    def wolsaStretch(self,stretch,frameLength=512,synthesisHop=None,tolerance=None):
        if synthesisHop is None:
            synthesisHop = frameLength//8
        reader = ArrayReader(np.array((self.x,)))
        writer = ArrayWriter(reader.channels)
        timeSeriesModification = audiotsm.wsola(
            reader.channels,
            speed = 1/stretch,
            frame_length=frameLength,
            synthesis_hop=synthesisHop,
            tolerance=tolerance
        )
        timeSeriesModification.run(reader, writer)
        self.x = writer.data.flatten()

