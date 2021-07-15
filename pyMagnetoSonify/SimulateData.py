
from .MagnetometerData import MagnetometerData
import numpy as np

class SimulateData(MagnetometerData):
    
    def genSine(s,t,amplitude,frequency,phase=0):
        """Generates a sine wave signal
        Requires that s.t is populated with time values
        """
        if t is None:
            t = s.t
        return np.sin(2*np.pi*frequency*(t) + phase)*amplitude

    def genSineExpectation(s,t,stretch,amplitude,frequency,phase=0):
        """Generates the expected output after sine signal is time stretched by a factor of stretch
        """
        frequency = stretch*frequency
        if t is None:
            t = s.t
        t = np.linspace(
            t[0],
            t[-1],
            int(stretch*len(t))
        )
        return s.genSine(t,amplitude,frequency,phase)

    def genHarmonic(s,t,frequencies,amplitude=1,phase=0):
        """Generates a set of overlapped sine waves
        Requires that s.t is populated with time values
        """
        if t is None:
            t = s.t

        signal = t*0
        frequencies = np.array(frequencies)

        try:
            amplitude = np.array(amplitude)
            assert len(amplitude) != 1
        except:
            amplitude = np.ones(frequencies.shape) * amplitude
        try:
            phase = np.array(phase)
            assert len(phase) != 1
        except:
            phase = np.ones(frequencies.shape) * phase

        for i,f in enumerate(frequencies):
            signal = signal + s.genSine(t,amplitude[i],f,phase[i])
        return signal

    def genHarmonicExpectation(s,t,stretch,frequencies,amplitude=1,phase=0):
        frequencies = stretch * np.array(frequencies)
        if t is None:
            t = s.t
        t = np.linspace(
            t[0],
            t[-1],
            int(stretch*len(t))
        )
        return s.genHarmonic(t,frequencies,amplitude,phase)

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