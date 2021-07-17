

import context

context.get()

from datetime import datetime

import magSonify
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from magSonify import DataSet_1D, SimulateData
from scipy.interpolate.interpolate import interp1d
from scipy.ndimage import uniform_filter1d
from scipy.optimize.minpack import curve_fit


def getBeforeAndExpectation_Sine(freq,duration_seconds,stretch = 16):
    ts = _getTestingTimeSeries(duration_seconds)
    genFunc = SimulateData().genSine
    genFuncExpectaion = SimulateData().genSineExpectation
    before, expectation = _getBeforeAndExpectation_Func(
        freq, stretch, ts, genFunc, genFuncExpectaion
    )
    return before, expectation

def getBeforeAndExpectation_Harmonic(freqs,duration_seconds,stretch = 16):
    ts = _getTestingTimeSeries(duration_seconds)
    genFunc = SimulateData().genHarmonic
    genFuncExpectaion = SimulateData().genHarmonicExpectation
    before, expectation = _getBeforeAndExpectation_Func(
        freqs, stretch, ts, genFunc, genFuncExpectaion
    )
    return before, expectation

def _getBeforeAndExpectation_Func(freq, stretch, ts, genFunc, genFuncExpectaion):
    before = magSonify.DataSet_1D(
        ts,
        genFunc(
            ts,
            freq,
        )
    )
    expectation = magSonify.DataSet_1D(
        ts,
        genFuncExpectaion(
            ts,
            stretch,
            freq,
        )
    )
    return before,expectation

def _getTestingTimeSeries(duration_seconds):
    seconds = int(duration_seconds)
    microseconds = int((duration_seconds-seconds)*1e6)
    ts = magSonify.generateTimeSeries(
        datetime(2010,1,1,0,0,0,0),
        datetime(2010,1,1,0,0,seconds,microseconds),
        spacing=np.timedelta64(1,'s').astype('timedelta64[ns]')/44100
    )
    
    return ts

def PSD(dataSet: DataSet_1D):
    return np.abs(np.fft.rfft(dataSet.x))**2 / len(dataSet.x)

def PSD_freqs(dataSet: DataSet_1D,sampleRate=44100):
    return np.fft.rfftfreq(len(dataSet.x),d=1/sampleRate)

def normalisePSD(psd):
    return psd/np.max(psd)

def plotPSD(expectation,after,showPlot=True):
    expectationPSD = PSD(expectation)
    actualPSD = PSD(after)
    expectation_frequencies = PSD_freqs(expectation)
    actual_frequencies = PSD_freqs(after)
    
    plt.plot(
        *reducePlotResolution(expectation_frequencies,expectationPSD)
        )
    plt.plot(
        *reducePlotResolution(actual_frequencies,actualPSD)
        )
    plt.xlabel("Hz")
    plt.yscale("log")
    if showPlot:
        plt.show()

def reducePlotResolution(frequencies,PSD,n=1000):
    reducedFreq = np.linspace(min(frequencies),max(frequencies),n)
    smoothPSD = uniform_filter1d(
        PSD,len(PSD)//n,mode='constant',cval=0, origin=0
    )
    f = interp1d(frequencies,smoothPSD,'linear')
    redPSD = f(reducedFreq)
    redPSD = normalisePSD(redPSD)
    return reducedFreq, redPSD

def getAfterAlgorithm(before: magSonify.DataSet_1D,stretch,algorithm):
    after = before.copy()
    getattr(after,algorithm)(stretch)
    return after

def plotPSD_Sine(algorithm,freq, stretch, showPlot=True):
    expectation, after = compare_Sine(algorithm, freq, stretch)
    plotPSD(expectation,after,showPlot)

def compare_Sine(algorithm, freq, stretch):
    before, expectation = getBeforeAndExpectation_Sine(freq,0.2,stretch)
    after = getAfterAlgorithm(before, stretch,algorithm)
    return expectation,after

def plotPSD_Harmonic(algorithm,freqs, stretch, showPlot=True):
    expectation, after = compare_Harmonic(algorithm, freqs, stretch)
    plotPSD(expectation,after,showPlot)

def compare_Harmonic(algorithm, freqs, stretch):
    before,expectation = getBeforeAndExpectation_Harmonic(freqs,0.2,stretch)
    after = getAfterAlgorithm(before,stretch,algorithm)
    return expectation, after

def getAfterPaustretch(before: magSonify.DataSet_1D, stretch):
    return getAfterAlgorithm(before,stretch,'paulStretch')

def plotPSDpaulstretchSine(freq,stretch,showPlot=True):
    plotPSD_Sine('paulStretch',freq, stretch, showPlot)

def plotPSDpaulstretchHarmonic(freqs,stretch,showPlot=True,):
    plotPSD_Harmonic('paulStretch',freqs, stretch, showPlot)

# def processing_PSD_runningMean_gaussianFit(expecation,actual,**kwargs):
#     pass

# def processing_PSD_gaussianfit(expectation, actual,**kwargs):
#     """ Returns the fractional change in the parameters of a gaussian fit to the data
#     """
#     expectationPSD, actualPSD, expectation_frequencies, actual_frequencies = PSD_with_freqs(expectation, actual)
    
#     expectationPeaks = fitNnarrowGaussian(expectation_frequencies,expectationPSD,**kwargs)
#     actualPeaks = fitNnarrowGaussian(actual_frequencies,actualPSD,**kwargs)
    
#     return expectationPeaks, actualPeaks

# def gaussianFunction(x,amp,u,sigma):
#     return amp * np.exp(
#         -(x-u)**2 / (2 * sigma**2)
#     )

# def fitNnarrowGaussian(x,y,n=2,windowDist=15):
#     y = y.copy()
#     xPeaks = []
#     for i in range(n):
#         imax = np.argmax(y)
#         start = max(0,imax-windowDist)
#         end = min(len(x),imax+windowDist)
#         window_x = x[start:end]
#         window_y = y[start:end]
#         params, _ = curve_fit(gaussianFunction,window_x,window_y,[y[imax],x[imax],5])
#         xPeaks.append(np.abs(params))
#         y[start:end] = 0
    
#     def keyFunc(x):
#         return x[1]

#     xPeaks.sort(key=keyFunc)
#     return xPeaks
