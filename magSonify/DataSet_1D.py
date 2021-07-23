from .sonificationMethods.paulstretch_mono import paulstretch
from .TimeSeries import TimeSeries
from .DataSet import DataSet
import numpy as np
from .sonificationMethods import wavelets
import audiotsm
from audiotsm.io.array import ArrayReader, ArrayWriter
from copy import deepcopy

class DataSet_1D(DataSet):
    """Represents a data set with one component, ie. where the samples are scalars.
    Supports a series of time stretching methods.

    :param timeSeries:
        Time series representing the sampling times.
    :param x:
        The single data series as type ``numpy.array``. The length of the array 
        should be the same as that of ``timeSeries``.
        
        Can also pass a dict with the single key ``0``, in which case the 
        corresponding value should be populated with a numpy array. This is used
        allow compatibility with inherited methods from DataSet.
    """
    def __init__(self,timeSeries: TimeSeries,x):
        if self._isInitWithDict(x):
            self.data = x
        else:
            self.data = {0: x}
        
        self.timeSeries = timeSeries

    def _isInitWithDict(self,x):
        try:
            if len(x.keys()) == 1 and 0 in x.keys():
                return True
            return False
        except AttributeError:
            return False

    @property
    def x(self) -> np.array:
        """Quick get/set access for ``self.data[0]``"""
        return self.data[0]

    @x.setter
    def x(self,x):
        self.data[0] = x

    def genMonoAudio(self, file, sampleRate=44100) -> None:
        return super().genMonoAudio(0, file, sampleRate)
 
    def normalise(self,maxAmplitude=1) -> None:
        """Normalises the data set to within a maximum amplitude. Should be used before
        attempting to output audio.
        """
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
        """Pitch shifts the data on specified axes by ``shift`` times using 
        the continous wavlet transform.
        
        :param shift:
            The multiple by which to shift the pitch of the input field.
        :param scaleLogSpacing:
            Scale spacing in log space, a lower value leads to higher
            resolution in frequency space and more processing time.
        :param interpolateFactor:
            If not None, specifies the facator by which the density of the coefficients should be
            increased. Used when generating time stretched audio.
        :param maxNumberSamples:
            The maximum number of samples for the largest scale in the wavelet wavelets.transform, used to
            prevent computations for inaubidle frequencies.
        :param wavelet:
            Wavelet function to use. If none is given, the Morlet wavelet will be used by default.
        :param preserveScaling:
            Whether to preserve the scaling of the data when outputing.
        """

        sampleSeperation = self.timeSeries.getMeanIntervalFloat()
        self.fillNaN()
        
        scales = wavelets.transform.generateCwtScales(
            maxNumberSamples,
            len(self.x),
            scaleLogSpacing,
            sampleSeperation,
            wavelet,
        )
        coefficients = wavelets.transform.cwt(self.x,scales,sampleSeperation,wavelet)

        self.coefficients = coefficients

        # Rescale the coefficients as in
        #   A Wavelet-based Pitch-shifting Method, Alexander G. Sklar
        #   https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.70.5079&rep=rep1&type=pdf

        magnitude = np.abs(coefficients)
        phase = np.unwrap(np.angle(coefficients),axis=1)

        if interpolateFactor is not None:
            magnitude, phase = wavelets.transform.interpolateCoeffsPolar(
                magnitude,phase,interpolateFactor
            )
            self._stretchTimeseries(interpolateFactor)

        coefficients_shifted = magnitude * np.exp(1j * phase * shift)

        self.coefficients_shifted = coefficients_shifted

        # Scaling constants are generally redudant if generating audio as data will be normalised
        if preserveScaling:
            rx = wavelets.transform.icwt(
                coefficients_shifted,
                scaleLogSpacing,
                sampleSeperation,
                wavelet.C_d,
                wavelet.time(0)
            )
        else:
            rx = wavelets.transform.icwt(coefficients_shifted)
        self.x = np.real(rx)
    
    def _stretchTimeseries(self, stretch):
        self.timeSeries.interpolate(stretch)
    
    def _correctTimeseries(self):
        self.timeSeries = self.timeSeries[:len(self.x)]

    def waveletStretch(
        self,stretch,interpolateBefore=None,interpolateAfter=None,scaleLogSpacing=0.12
    ) -> None:
        """Time stretches the data using wavelet transforms.
        
        :param stretch:
            The factor by which to stretch the data.
        :param interpolateBefore:
            Interpolation factor prior to forward CWT.
        :param interpolateAfter:
            Interpolation factor after the forward CWT. Default is ``stretch`` if both
            ``interpolateBefore`` and ``interpolateAfter`` are ``None``.
        :param scaleLogSpacing:
            Spacing between scales for the CWT. Lower values improve frequency resolution
            at the cost of increasing computation time.
        """
        if interpolateBefore is None and interpolateAfter is None:
            interpolateAfter = stretch
        if interpolateBefore is not None:
            self.interpolateFactor(interpolateBefore)
        self.waveletPitchShift(stretch,scaleLogSpacing,interpolateAfter)

    def paulStretch(self,stretch,window=0.015) -> None:
        """Stretches the data according the paulstretch algorithm.

        :param stretch:
            The factor by which to stretch the data.
        :param window:
            The window size to be used by the paulstrtch algorithm. A ``window`` of 0.1 is
            equivalent to 4410 data points.
        
        .. note::

            Some samples may be clipped at the end of the data set.
        """
        self._stretchTimeseries(stretch)
        self.x = paulstretch(self.x,stretch,window)
        self._correctTimeseries()

    def phaseVocoderStretch(self,stretch,frameLength=512,synthesisHop=None) -> None:
        """Time stretches the data using a phase vocoder
        
        See also: `audiotsm.phasevocoder <https://audiotsm.readthedocs.io/en/latest/tsm.html#audiotsm.phasevocoder>`_

        :param frameLength: the length of the frames
        :type frameLength: int
        :param synthesisHop: 
            the number of samples between two consecutive synthesis frames (``frameLength // 16`` by default).
        :type synthesisHop: int

        .. note::

            Some samples may be clipped at the end of the data set.
        """
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
        self._stretchTimeseries(stretch)
        self._correctTimeseries()

    def wsolaStretch(self,stretch,frameLength=512,synthesisHop=None,tolerance=None) -> None:
        """Time stretches the data using WSOLA

        See also: `audiotsm.wsola <https://audiotsm.readthedocs.io/en/latest/tsm.html#audiotsm.wsola>`_

        :param frame_length: the length of the frames
        :type frame_length: int
        :param synthesis_hop: 
            the number of samples between two consecutive synthesis frames (``frame_length // 8`` by default).
        :type synthesis_hop: int

        .. note::

            Some samples may be clipped at the end of the data set.
        """
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
        self._stretchTimeseries(stretch)
        self._correctTimeseries()