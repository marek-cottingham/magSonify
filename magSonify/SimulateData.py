
from datetime import time
import numpy as np
from numpy.core.arrayprint import _array_str_implementation
from scipy import signal
from .TimeSeries import TimeSeries
from scipy.signal import chirp

class SimulateData():
    def _setupTimeSeries(s, timeSeries, stretch=None):
        timeSeries = timeSeries.copy()
        timeSeries.changeUnit(np.timedelta64(1,'s'))
        if stretch is not None:
            timeSeries.interpolate(stretch)
        return timeSeries
    
    def genSine(s,timeSeries: TimeSeries,frequency,amplitude=1,phase=0):
        """Generates a sine wave signal
        """
        timeSeries = s._setupTimeSeries(timeSeries)
        return np.sin(2*np.pi*frequency*timeSeries.asFloat() + phase)*amplitude

    def genSineExpectation(s,timeSeries: TimeSeries,stretch,frequency,amplitude=1,phase=0):
        """Generates the expected output after sine wave signal is time stretched by 
            a factor of {stretch}
        """
        frequency = stretch*frequency
        timeSeries = s._setupTimeSeries(timeSeries,stretch)
        return s.genSine(timeSeries,frequency,amplitude,phase)

    def genHarmonic(s,timeSeries: TimeSeries,frequencies,amplitude=1,phase=0):
        """Generates a set of overlapped sine waves
        """
        timeSeries = s._setupTimeSeries(timeSeries)
        signal = timeSeries.asFloat() * 0
        frequencies = np.array(frequencies)
        
        amplitude = np.array(amplitude)
        if amplitude.size == 1:
            amplitude = np.ones(frequencies.shape) * amplitude

        phase = np.array(phase)
        if phase.size == 1:
            phase = np.ones(frequencies.shape) * phase

        for i,f in enumerate(frequencies):
            signal = signal + s.genSine(timeSeries,f,amplitude[i],phase[i])
        return signal

    def genHarmonicExpectation(s,timeSeries: TimeSeries,stretch,frequencies,amplitude=1,phase=0):
        frequencies = stretch * np.array(frequencies)
        timeSeries = s._setupTimeSeries(timeSeries,stretch)
        return s.genHarmonic(timeSeries,frequencies,amplitude,phase)

    def genSweep(self,timeSeries: TimeSeries, f0, f1, amplitude=1, method='linear'):
        timeSeries = self._setupTimeSeries(timeSeries)
        times = timeSeries.asFloat()
        t1 = np.max(times)
        signal = chirp(times,f0,t1,f1,method=method) * amplitude
        return signal

    def genSweepExpectation(self,timeSeries:TimeSeries,stretch,f0,f1,amplitdue=1,method='linear'):
        timeSeries = self._setupTimeSeries(timeSeries,stretch)
        times = timeSeries.asFloat()
        t1 = np.max(times)
        signal = chirp(times,f0*stretch,t1,f1*stretch,method=method) * amplitdue
        return signal

    def waveOrientOffset(s,waveform,direction=(1,0,0),offset=(0,0,0)):
        """ Rotate and offset a given waveform in 3D space, returning a list with the series for the
        3 components
        
        direction:
            The axis the field amplitude oscillates in as a vector. This will be normalised to a 
            unit vector.
        offset:
            The offset of the origin of the wave.
        """
        b = [None,None,None]
        direction = np.array(direction)
        offset = np.array(offset)
        direction = direction / np.linalg.norm(direction)
        for i, bi in enumerate(b):
            b[i] = waveform*direction[i] + offset[i]
        return b