USE_CACHING = False

import numpy as np
import scipy
import scipy.signal
import scipy.optimize

from .wavelets import Morlet
from scipy.interpolate import interp1d

# Import the memory function. This is used to perform data caching during testing
# in order to decrease the time needed to rerun the same test

if USE_CACHING:
    import joblib
    from ..initialise import memory_cache_path
    memory = joblib.Memory(
        memory_cache_path,
        verbose = 0,
        bytes_limit= int(1.07e9)
    )

# Define names to import when importing all methods from this module
__all__ = ['cwt', 'WaveletAnalysis', 'WaveletTransform']

def generateCwtScales(maxNumberSamples, dj, dt, wavelet, N):
        if maxNumberSamples is None or maxNumberSamples > N:
            maxNumberSamples = N
        # Smallest scale
        def f(s):
            return wavelet.fourier_period(s) - 2 * dt
        s0 = scipy.optimize.fsolve(f, 1)[0]
        # Largest scale
        J = int((1 / dj) * np.log2(maxNumberSamples * dt / s0))
        # Generate scales
        sj = s0 * 2 ** (dj * np.arange(0, J + 1))
        return sj

def cwt(data, wavelet, scales, dt):

    ### Generate blank output
    # wavelets can be complex so output is complex
    output = np.zeros((len(scales),) + data.shape, dtype=np.complex128)

    for ind, width in enumerate(scales):
        # number of points needed to capture wavelet
        M = 10 * width / dt
        # times to use, centred at zero
        t = np.arange((-M + 1) / 2., (M + 1) / 2.) * dt
        # sample wavelet and normalise

        # square root scaled version
        #norm = (dt / width) ** (0.5)

        norm = (dt** (0.5) / width)
        wavelet_data = norm * wavelet(t, width)
        output[ind, :] = scipy.signal.fftconvolve(data,
                                                  wavelet_data,
                                                  mode='same')
    return output

if USE_CACHING:
    cwt = memory.cache(cwt)

def original_icwt(W_n,s,dj,dt,C_d,Y_00):
    # square root scaled version
    #real_sum = np.sum(W_n.real.T / s ** .5, axis=-1).T

    print(dt)

    real_sum = np.sum(W_n.real.T, axis=-1).T

    x_n = real_sum * (dj * dt ** .5 / (C_d * Y_00))
    return x_n

def alternative_icwt(W_n,s,dj,dt,C_d,Y_00):
    x_n = np.trapz(np.diff(W_n).T,s,axis=-1).T.imag
    x_n *= 2*np.pi
    return x_n

icwt = original_icwt

def use_original_icwt():
    global icwt
    icwt = original_icwt

def use_alternative_icwt():
    global icwt
    icwt = alternative_icwt

def interpolateCoeffs(W_n,interpolate_factor):
    real = W_n.real
    imag = W_n.imag

    original_steps = np.linspace(0,1,real.shape[1])
    new_steps = np.linspace(0,1,int(real.shape[1]*interpolate_factor))

    new_real = []
    new_imag = []

    for i in range(real.shape[0]):
        freal = interp1d(original_steps,real[i],kind="cubic")
        fimag = interp1d(original_steps,imag[i],kind='cubic')
        new_real.append(
            freal(new_steps)
        )
        new_imag.append(
            fimag(new_steps)
        )
    new_real = np.array(new_real)
    new_imag = np.array(new_imag)
    W_n_new = new_real + 1j * new_imag
    return W_n_new

def interpolateCoeffsPolar(magnitude,phase,interpolate_factor):
    original_steps = np.linspace(0,1,magnitude.shape[1])
    new_steps = np.linspace(0,1,int(magnitude.shape[1]*interpolate_factor))

    new_mag = []
    new_phase = []

    for i in range(magnitude.shape[0]):
        fmagnitude = interp1d(original_steps,magnitude[i],kind="cubic")
        fphase = interp1d(original_steps,phase[i],kind='cubic')
        new_mag.append(
            fmagnitude(new_steps)
        )
        new_phase.append(
            fphase(new_steps)
        )
    
    magnitude = np.array(new_mag)
    phase = np.array(new_phase)
    return magnitude, phase