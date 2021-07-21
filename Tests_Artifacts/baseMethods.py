"""A set of functions used to construct artifact tests from idealised signals and render
the output of the tests
"""

import context

context.get()

from datetime import datetime

import magSonify
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from magSonify import DataSet_1D, SimulateData
from magSonify import TimeSeries
from scipy.interpolate.interpolate import interp1d
from scipy.ndimage import uniform_filter1d


def getBeforeAndExpectation_Sine(freq,duration_seconds,stretch = 16):
    """Get generated data sets for a simulated sine wave, before and after a time stretch"""
    ts = _getTestingTimeSeries(duration_seconds)
    genFunc = SimulateData().genSine
    genFuncExpectaion = SimulateData().genSineExpectation
    kwargs = {
        'frequency': freq,
    }
    before, expectation = _getBeforeAndExpectation_Func(
        kwargs, stretch, ts, genFunc, genFuncExpectaion
    )
    return before, expectation

def getBeforeAndExpectation_Harmonic(freqs,duration_seconds,stretch = 16):
    """Get generated data sets for a simulated harmonic, before and after a time stretch"""
    ts = _getTestingTimeSeries(duration_seconds)
    genFunc = SimulateData().genHarmonic
    genFuncExpectaion = SimulateData().genHarmonicExpectation
    kwargs = {
        'frequencies': freqs,
    }
    before, expectation = _getBeforeAndExpectation_Func(
        kwargs, stretch, ts, genFunc, genFuncExpectaion
    )
    return before, expectation

def getBeforeAndExpectation_Sweep(
    startingFreq,finalFreq,duration_seconds,stretch=16,method='logarithmic'
):
    """Get generated data sets for a simulated frequency sweep, before and after a time stretch"""
    ts = _getTestingTimeSeries(duration_seconds)
    genFunc = SimulateData().genSweep
    genFuncExpectation = SimulateData().genSweepExpectation
    kwargs = {
        'f0': startingFreq,
        'f1': finalFreq,
        'method': method
    }
    before, expect = _getBeforeAndExpectation_Func(
        kwargs, stretch, ts, genFunc, genFuncExpectation
    )
    return before, expect

def _getBeforeAndExpectation_Func(kwargs, stretch, ts: TimeSeries, genFunc, genFuncExpectation):
    before = magSonify.DataSet_1D(
        ts,
        genFunc(
            ts,
            **kwargs,
        )
    )
    new_ts = ts.copy()
    new_ts.interpolate(stretch)
    expectation = magSonify.DataSet_1D(
        new_ts,
        genFuncExpectation(
            ts,
            stretch,
            **kwargs,
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

def PSD(dataSet: DataSet_1D) -> np.array:
    """Compute the PSD of a data set"""
    return np.abs(np.fft.rfft(dataSet.x))**2 / len(dataSet.x)

def PSD_freqs(dataSet: DataSet_1D,sampleRate=44100) -> np.array:
    """Compute the corresponding frequencies for the PSD of a data set"""
    return np.fft.rfftfreq(len(dataSet.x),d=1/sampleRate)

def normalisePSD(psd):
    """Normalise a PSD so that its highest peak has a magnitude of 1"""
    return psd/np.max(psd)

def plotPSD(expectation,after,showPlot=True):
    """Plots the PSD of the provided pair of data sets"""
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
    """Reduce PSD resolution to allow plotting with matplotlib. Smooths the PSD.

    :returns: ``( reducedFreq: np.array, reducedPSD: np.array )``
    """
    reducedFreq = np.linspace(min(frequencies),max(frequencies),n)
    smoothPSD = uniform_filter1d(
        PSD,len(PSD)//n,mode='constant',cval=0, origin=0
    )
    f = interp1d(frequencies,smoothPSD,'linear')
    reducedPSD = f(reducedFreq)
    reducedPSD = normalisePSD(reducedPSD)
    return reducedFreq, reducedPSD

def getAfterAlgorithm(before: magSonify.DataSet_1D,stretch,algorithm):
    """Process data series with the given time stretch algorithm
    
    :param algorithm:
        Can be 'waveletStretch', 'paulStretch', 'phaseVocoderStretch' or 'wsolaStretch'
    """
    after = before.copy()
    getattr(after,algorithm)(stretch)
    return after

def plotPSD_Sine(algorithm,freq, stretch, showPlot=True):
    """See also: :func:`baseMethods.compare_Sine`"""
    expectation, after = compare_Sine(algorithm, freq, stretch)
    plotPSD(expectation,after,showPlot)

def compare_Sine(algorithm, freq, stretch):
    """Computes the expeted and actual time stretch on a sine wave with the given algorithm
    
    See also: :func:`baseMethods.getAfterAlgorithm`"""
    before, expectation = getBeforeAndExpectation_Sine(freq,0.2,stretch)
    after = getAfterAlgorithm(before, stretch,algorithm)
    return expectation,after

def plotPSD_Harmonic(algorithm,freqs, stretch, showPlot=True):
    """See also: :func:`baseMethods.compare_Harmonic`"""
    expectation, after = compare_Harmonic(algorithm, freqs, stretch)
    plotPSD(expectation,after,showPlot)

def compare_Harmonic(algorithm, freqs, stretch):
    """Computes the expeted and actual time stretch on a harmonic with the given algorithm
    
    See also: :func:`baseMethods.getAfterAlgorithm`"""
    before,expectation = getBeforeAndExpectation_Harmonic(freqs,0.2,stretch)
    after = getAfterAlgorithm(before,stretch,algorithm)
    return expectation, after

def getAfterPaustretch(before: magSonify.DataSet_1D, stretch):
    return getAfterAlgorithm(before,stretch,'paulStretch')

def plotPSDpaulstretchSine(freq,stretch,showPlot=True):
    plotPSD_Sine('paulStretch',freq, stretch, showPlot)

def plotPSDpaulstretchHarmonic(freqs,stretch,showPlot=True,):
    plotPSD_Harmonic('paulStretch',freqs, stretch, showPlot)


