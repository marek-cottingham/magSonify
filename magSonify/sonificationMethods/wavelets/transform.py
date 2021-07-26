USE_CACHING = False

import numpy as np
import scipy
import scipy.signal
import scipy.optimize

from .wavelets import Morlet
from scipy.interpolate import interp1d

def generateCwtScales(
    maxNumberSamples, dataLength, scaleSpacingLog=0.1, sampleSpacingTime=1, waveletFunction=Morlet()
):
    """ Generates a set of scales to be used to when scaling the wavlet function
    during CWT and ICWT.
    """
    # Based on CT98: https://psl.noaa.gov/people/gilbert.p.compo/Torrence_compo1998.pdf

    if maxNumberSamples is None or maxNumberSamples > dataLength:
        maxNumberSamples = dataLength

    smallestScale =_generateSmallestScale(sampleSpacingTime, waveletFunction)

    LargestScaleIndex = _generateLargestScaleIndex(
        maxNumberSamples, scaleSpacingLog, sampleSpacingTime, smallestScale
    )
    
    scales = smallestScale * 2**(scaleSpacingLog * np.arange(0, LargestScaleIndex + 1))
    return scales

def _generateLargestScaleIndex(maxNumberSamples, scaleSpacingLog, sampleSpacingTime, smallestScale):
    return int((1 / scaleSpacingLog) * np.log2(maxNumberSamples * sampleSpacingTime / smallestScale))

def _generateSmallestScale(sampleSpacingTime, wavelet):
    def f(s):
        return wavelet.fourier_period(s) - 2 * sampleSpacingTime
    return scipy.optimize.fsolve(f, 1)[0]

def cwt(x, scales, sampleSpacingTime=1, waveletFunction=Morlet()):
    """ Computes the forward continous wavelet transform.
    """
    # Based on CT98: https://psl.noaa.gov/people/gilbert.p.compo/Torrence_compo1998.pdf
    # output = np.zeros(
    #     (len(scales),) + x.shape,
    #     dtype=np.complex128
    # )
    output = []

    for i, s in enumerate(scales):
        pointsToCaptureWavelet = 10 * s / sampleSpacingTime

        times = np.arange((-pointsToCaptureWavelet + 1) / 2., (pointsToCaptureWavelet + 1) / 2.) 
        times *= sampleSpacingTime

        normalisationConstant = (sampleSpacingTime** (0.5) / s)
        wavelet = normalisationConstant * waveletFunction(times, s)

        output.append( scipy.signal.fftconvolve(x,wavelet,mode='same') )
    output = np.array(output,dtype=np.complex128)
    return output

def icwt(
    coefficients,scaleLogSpacing=0.1,sampleSpacingTime=1,waveletRescaleFactor=1,waveletTimeFactor=1
):
    """ Computes the inverse continous wavelet transform.

    :param coefficients:
        The coefficients produced from the forward CWT, in a 2D numpy array.
    """
    # Based on CT98: https://psl.noaa.gov/people/gilbert.p.compo/Torrence_compo1998.pdf
    real_sum = np.sum(coefficients.real.T, axis=-1).T
    x =  (
        scaleLogSpacing * sampleSpacingTime ** .5 / (waveletRescaleFactor * waveletTimeFactor)
    ) * real_sum
    return x

def icwt_noAdmissibilityCondition(coefficients,scales,**kwargs):
    """ Computes the inverse continous wavlet transform using an alternative algorithm.
    """
    # Based on the method presented in: 
    #   Computational implementation of the inverse continuous wavelet transform without a 
    #   requirement of the admissibility condition. Eugene B. Postnikov, Elena A. Lebedeva, 
    #   Anastasia I. Lavrova. 2015. https://arxiv.org/abs/1507.04971
    x = np.trapz(np.diff(coefficients).T,scales,axis=-1).T.imag
    x *= 2*np.pi
    return x

def interpolateCoeffs(coeffs,interpolate_factor):
    """ Interpolates the coefficients produced by CWT. Real and imaginary parts interpolated
    seperately.
    """
    real = coeffs.real
    imag = coeffs.imag

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
    coeffs_new = new_real + 1j * new_imag
    return coeffs_new

def interpolateCoeffsPolar(magnitude,phase,interpolate_factor):
    """ Interpolates the polar form of the coefficients produced by CWT. Magnitude and phase
    interpolated sperately.
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