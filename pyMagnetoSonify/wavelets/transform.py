USE_CACHING = False

import numpy as np
import scipy
import scipy.signal
import scipy.optimize

from .wavelets import Morlet
from scipy.interpolate import interp1d

# Import the memory function. This is used to perform data caching during testing
# in order to decrease the time needed to rerun the same test
# @TheMuonNeutrino 2021 07 13: Using caching here is discouraged, this does not appear
#   to improve performance

if USE_CACHING:
    import joblib
    from ..initialise import memory_cache_path
    memory = joblib.Memory(
        memory_cache_path,
        verbose = 0,
        bytes_limit= int(1.07e9)
    )

def generateCwtScales(maxNumberSamples, N, dj=0.1, dt=1, wavelet=Morlet()):
    """ Generates a set of scales to be used to when scaling the wavlet function
    during CWT and ICWT.

    maxNumberSamples:
        The maximum number of samples in the largest scale, used to limit the lowest
        frequecies consider by the transforms.
    N:
        The length of the data.
    dj:
        The scale spacing in log space.
    dt:
        Time spacing of data samples.
    wavelet:
        The wavlet function to use.
    """
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

def cwt(data, scales, dt=1, wavelet=Morlet()):
    """ Computes the forward continous wavelet transform.
    data:
        Data to perform transform on.
    scales:
        Set of scales used to rescale the wavelet function.
    dt:
        Time spacing of data samples.
    wavelet:
        The wavlet function to use.
    """
    ### Generate blank output
    # Wavelets can be complex so output is complex
    output = np.zeros((len(scales),) + data.shape, dtype=np.complex128)

    for ind, width in enumerate(scales):
        # Number of points needed to capture wavelet
        M = 10 * width / dt

        # Times to use, centred at zero
        t = np.arange((-M + 1) / 2., (M + 1) / 2.) * dt

        # Normalise wavlets
        norm = (dt** (0.5) / width)
        wavelet_data = norm * wavelet(t, width)
        output[ind,:] = scipy.signal.fftconvolve(
            data,
            wavelet_data,
            mode='same'
        )
    return output

def icwt(coefficients,dj=0.1,dt=1,waveletRescaleFactor=1,waveletTimeFactor=1):
    """ Computes the inverse continous wavelet transform.

    coefficients:
        The coefficients produced from the forward CWT, in a 2D numpy array.
    dj:
        The scale spacing in log space
    dt:
        Time spacing of data samples
    waveletResacleFactor, waveletTimeFactor:
        Rescaling factors which depend on the wavelet function used. Data is rescaled by
        1 / (waveletRescaleFactor * waveletTimeFactor).
    """
    real_sum = np.sum(coefficients.real.T, axis=-1).T
    x_n =  (dj * dt ** .5 / (waveletRescaleFactor * waveletTimeFactor)) * real_sum
    return x_n

def icwt_noAdmissibilityCondition(coefficients,scales,**kwargs):
    """ Computes the inverse continous wavlet transform.
    """

    x_n = np.trapz(np.diff(coefficients).T,scales,axis=-1).T.imag
    x_n *= 2*np.pi
    return x_n

def interpolateCoeffs(W_n,interpolate_factor):
    """ Interpolates the coefficients produced by CWT. Real and imaginary parts interpolated
    seperately.
    """
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
    """ Interpolates the polar form of the coefficients produced by CWT. Magnitude and phase
    interpolated spereately.
    """
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