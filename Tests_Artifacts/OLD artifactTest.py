
import os
import numpy as np
import matplotlib.pyplot as plt
from numpy.core.records import array
from scipy.ndimage import uniform_filter1d
from scipy.optimize import curve_fit
from numpy.random import default_rng

import pySonify as Sonify

wavelets = Sonify.waveletsLocal
rng = default_rng()

def waveletStretch(interpolateBefore, interpolateAfter, dj, axD):
        axD.interpolate(interpolateBefore)
        axD.waveletPitchShift(
            interpolateBefore*interpolateAfter,
            dj,
            interpolateW_n=interpolateAfter
        )

def paulStretch(stretch,timeWindow,axD):
    axD.paulStretch(stretch,timeWindow)

def pre_setupBlankTimeSeries(endTime=0.1):
    mag = Sonify.SimulateData()
    mag.t = np.linspace(0.0,endTime,int(44100*endTime))
    return mag

def component_sine(
    frequency=256/5,
    stretch=1,
    stretchFunction=None,
    endTime=0.1
):
    mag = pre_setupBlankTimeSeries(endTime)
    axD = Sonify.DataAxis(
        mag.t.copy(),
        mag.genSine(None,1,frequency)
    )
    expectation = mag.genSineExpectation(
        None,
        stretch=stretch,
        amplitude=1,
        frequency=frequency
    )
    stretchFunction(axD)
    after = axD.x
    return expectation, after

def component_harmonic(
    frequencies=[200,2000],
    stretch = 1,
    stretchFunction = None,
    endTime=0.1
):
    mag = pre_setupBlankTimeSeries(endTime)
    axD = Sonify.DataAxis(
        mag.t.copy(),
        mag.genHarmonic(None,frequencies)
    )
    expectation = mag.genHarmonicExpectation(
        None,
        stretch=stretch,
        amplitude=1,
        frequencies=frequencies
    )
    stretchFunction(axD)
    after = axD.x
    return expectation, after

def frequencyScan(freqs,componentGenerator,processing):
    output = []
    N = len(freqs)
    for i,f in enumerate(freqs):
        expectation, after = componentGenerator(f)
        output.append(processing(expectation,after))
        print(f"  {round(i/N*100)} % complete",end="\r",flush=True)
    return np.array(output)

def wavelet_computeAmpScale(freqs,processingFunction,componentFunction,interpolateBefore=1,interpolateAfter=1,dj=1):
    componentGenerator = lambda f: componentFunction(
        f,
        stretch = interpolateBefore*interpolateAfter,
        stretchFunction = lambda axD: waveletStretch(interpolateBefore,interpolateAfter,dj,axD)
    )
    processingFunction
    return frequencyScan(freqs,componentGenerator,processingFunction)

def processing_maxAbs(expectation,after):
    return np.max(np.abs(after))

def processing_meanAbs(expectation,after):
    return np.mean(np.abs(after))

def processing_rSquared(expectation,after):
    ss_tot = np.sum(
        (after - np.mean(after))**2
    )
    ss_res = np.sum(
        (after - expectation[:len(after)])**2
    )
    rSquared = 1 - ss_res / ss_tot
    if rSquared > 1:
        raise ValueError(f"Computed an r-squared greater than 1, with ss_res: {ss_res}, ss_tot: {ss_tot}")
    return rSquared

def processing_chiSquare(expectation,a):
    chiSquare = np.sum(
        ( (a - expectation[:len(a)]) / expectation[:len(a)] )**2
    )
    return chiSquare/len(a)

def PSD(e,a):
    e = np.abs(np.fft.rfft(e))**2
    a = np.abs(np.fft.rfft(a))**2
    return e, a

def processing_PSD_rSquared(expectation, after):
    expectation, after = PSD(expectation,after)
    return processing_rSquared(expectation,after)

def processing_PSD_chiSquare(expectation,after):
    expectation, after = PSD(expectation, after)
    return processing_chiSquare(expectation,after)

def processing_MinusAmplitudeDifference(expectation,after,
        diffProcessingFunction = lambda diff, expectation: np.mean(np.abs(diff)) / np.mean(np.abs(expectation))
    ):
            M = len(after)
            diff = (expectation[:M]-after)
            if False:
                plt.figure()
                plt.plot(expectation,label="Expectation")
                plt.plot(after,label="Actual")
                #plt.plot(uniform_filter1d(expectation,20,mode='constant'),label="Expectation - Rolling mean (20)")
                #plt.plot(uniform_filter1d(after,20,mode='constant'),label="Actual - Rolling mean (20)")
                #plt.plot( np.arange(M//4,3*M//4,1), diff,label="Difference")
                plt.xlabel("Sample number")
                plt.ylabel("Amplitude")
                plt.legend()
                plt.show()
            diff = diff[M//4:3*M//4]
            return 1 - diffProcessingFunction(diff,expectation)

def processing_PSD_runningMean_gaussianFit(expecation,actual,**kwargs):
    pass

def processing_PSD_gaussianfit(expectation, actual,**kwargs):
    """ Returns the fractional change in the parameters of a gaussian fit to the data
    """
    expectation, actual, expectation_frequencies, actual_frequencies = PSD_with_freqs(expectation, actual)
    
    ePeaks = fitNnarrowGaussian(expectation_frequencies,expectation,**kwargs)
    aPeaks = fitNnarrowGaussian(actual_frequencies,actual,**kwargs)
    
    return ePeaks, aPeaks

def PSD_with_freqs(expectation, actual, sampleRate=44100):
    expectation_frequencies = np.fft.rfftfreq(len(expectation),d=1/sampleRate)
    actual_frequencies = np.fft.rfftfreq(len(actual),d=1/sampleRate)
    expectation, actual = PSD(expectation,actual)
    return expectation,actual,expectation_frequencies,actual_frequencies

def gaussianFunction(x,amp,u,sigma):
    return amp * np.exp(
        -(x-u)**2 / (2 * sigma**2)
    )

def fitNnarrowGaussian(x,y,n=2,windowDist=15):
    y = y.copy()
    xPeaks = []
    for i in range(n):
        imax = np.argmax(y)
        start = max(0,imax-windowDist)
        end = min(len(x),imax+windowDist)
        window_x = x[start:end]
        window_y = y[start:end]
        params, _ = curve_fit(gaussianFunction,window_x,window_y,[y[imax],x[imax],5])
        xPeaks.append(np.abs(params))
        y[start:end] = 0

        #print(params)
    
    def keyFunc(x):
        return x[1]

    xPeaks.sort(key=keyFunc)
    return xPeaks

def test_sineAmpScaleFactorWithFrequency_varyingMethods():
    ### PARAMETERS ###
    freqs = [100,250,400,1000,4000,10000,15000]
    freqs = np.arange(200,20001,400)
    interpolateBefore = 1
    interpolateAfter = 1
    dj = 0.1

    processingFunction = processing_maxAbs #processing_meanAbs
    ### END PARAMETERS ###

    def test_sub_plotAmpScale_sine(plotLabel):
        ampScale = wavelet_computeAmpScale(
            freqs,processingFunction,component_sine,interpolateBefore,interpolateAfter,dj
        )
        ampScale = ampScale / ampScale[0]
        plt.plot(freqs,ampScale,label=plotLabel)
        pass

    test_sub_plotAmpScale_sine("CT, GC 1998")

    wavelets.transform.use_alternative_icwt()
    test_sub_plotAmpScale_sine("EP, EL, Al 2015")
    wavelets.transform.use_original_icwt()

    freqs = np.arange(200,20001,200)
    matScale = np.genfromtxt("matlabAmpScalingWithFrequency-Morse.txt",delimiter=",")
    matScale = matScale/matScale[0]
    plt.plot(freqs,matScale,label="Matlab - Morse")

    matScale = np.genfromtxt("matlabAmpScalingWithFrequency-Morlet.txt",delimiter=",")
    matScale = matScale/matScale[0]
    plt.plot(freqs,matScale,label="Matlab - Morlet")

    plt.xlabel('Frequency of sine wave (Hz)')
    plt.ylabel('Amplitude scaling after icwt(cwt())')
    plt.legend()
    plt.show()

def wavelet_compareHarmonicSineAmpScale():
    freqs = np.arange(400,20001,400)
    #freqs = (400,)
    interpolateBefore = 1
    interpolateAfter = 1
    dj = 0.1

    processingFunction = processing_rSquared
    processingFunctionSine = processingFunction
    #processingFunctionSine = lambda e,a: processingFunction(e,a,n=1)
    def select(data):
        return data
        ePeaks, aPeaks = data
        proportionPeaks = (np.array(aPeaks) - np.array(ePeaks)) / np.array(ePeaks)
        res = []
        for i,v in enumerate(proportionPeaks):
            res.append( proportionPeaks[i][0][0] )
        return res

    data = wavelet_computeAmpScale(
        freqs,processingFunctionSine,component_sine,interpolateBefore,interpolateAfter,dj
    )
    data = select(data)
    plt.plot(freqs,data,label="Sine wave")

    def computeHarmonicHighScaling(freqs,baseF=200):
        return frequencyScan(
            freqs,
            lambda f: component_harmonic(
                [baseF,f],
                stretch=interpolateAfter*interpolateBefore,
                stretchFunction=(
                    lambda axD: waveletStretch(interpolateBefore,interpolateAfter,dj,axD)
                )
            ),
            #processing_MinusAmplitudeDifference
            processingFunction
        )

    data = computeHarmonicHighScaling(freqs)
    data = select(data)
    plt.plot(freqs,data,label="Harmonic w/ 200 Hz")

    data = computeHarmonicHighScaling(freqs,baseF=2000)
    data = select(data)
    plt.plot(freqs,data,label="Harmonic w/ 2000 Hz",ls="dashed")

    plt.xlabel('Frequency of signal (Hz)')
    #plt.ylabel('Amptlitude scaling after icwt(cwt())')
    plt.ylabel("R^2 comparing expectation and result after icwt(cwt())")
    #plt.ylabel("R^2 comparing PSD of expectation and result after icwt(cwt())")
    #plt.ylabel("Fractional error in PSD peak parameter")
    plt.legend()
    plt.show()

def rand_harmonic(min_n,max_n,min_f,max_f):
    num = rng.integers(min_n,max_n+1)
    freqs = rng.integers(min_f,max_f,num)
    return freqs

def peak_AmplitudeAttenuationPercent(ePeak,aPeak):
    return (aPeak[0] - ePeak[0]) / ePeak[0] * 100

def peak_WidthChangePercent(ePeak,aPeak):
    res = (aPeak[2] - ePeak[2]) / ePeak[2] * 100
    return res

def peak_MagnitudeAttenuationPercent(ePeak,aPeak):
    eMag = ePeak[0]/ePeak[2]
    aMag = aPeak[0]/aPeak[2]
    return ((aMag - eMag) / eMag) * 100

def test_attenuationByPeakFrequency():
    ### Parameters ###
    number_of_test_harmonics = 100
    min_peaks_per_harmonic = 1
    max_peaks_per_harmonic = 1

    min_f = 50
    max_f = 20000

    use_paulstretch = False

    use_rand_harmonic = True

    use_dedicate_freq = False
    listOfFrequencies = (
        (11370,12010),
        (12000,),
        (17660,),
    )

    interpolateBefore = 1
    interpolateAfter = 16
    
    dj = 0.1
    timeWindow = 0.015

    PLOT_FIT_FAILS = False
    PLOT_ALL = False
    ### End parameters ###

    stretch = interpolateBefore * interpolateAfter
    if use_paulstretch:
        stretchFunction = lambda axD: paulStretch(stretch,timeWindow,axD)
        windowDist = 20
        endTime = 2
    else:
        stretchFunction = lambda axD: waveletStretch(interpolateBefore,interpolateAfter,dj,axD)
        windowDist = 10
        endTime = 0.1

    if use_rand_harmonic:
        freqGen = lambda: rand_harmonic(min_peaks_per_harmonic,max_peaks_per_harmonic,min_f,max_f)
    if use_dedicate_freq:
        freqGen = iter(listOfFrequencies)


    peaksFrequency = []
    peaks_AmplitudeAttenuationPercent = []
    peaks_WidthChangePercent = []
    peaks_MagnitudeAttenuationPercent = []

    allRuns_aPeaks = []
    allRuns_ePeaks = []
    axObj = Sonify.DataAxis((0,),(0,))

    successful = 0
    fileNum = 0
    while successful < number_of_test_harmonics:
        try:
            freqs = next(freqGen)
        except StopIteration:
            break
        except TypeError:
            freqs = freqGen()

        #print(freqs)
        try:
            fileNum += 1
            expectation, actual = component_harmonic(
                    freqs,stretch,stretchFunction,endTime
                )
            #axObj.writeoutAudio(actual,f"_audio\{fileNum} actual {freqs}.wav",amplitudeB=np.max(np.abs(actual)))
            #axObj.writeoutAudio(expectation,f"_audio\{fileNum} expectation {freqs}.wav",amplitudeB=np.max(np.abs(expectation)))
            ePeaks, aPeaks = processing_PSD_gaussianfit(
                expectation, actual, n=len(freqs), windowDist = windowDist
            )
        except RuntimeError as e:
            print((
                "Input frequencies resulted in a condition where PSD of stretched data could not be"
                f" fit succsesfully. \n Frequencies = {freqs}"
            ))
            if PLOT_FIT_FAILS:
                plt.plot(expectation)
                plt.plot(actual)
                plt.show()
                expectation, actual, expectation_frequencies, actual_frequencies = PSD_with_freqs(expectation, actual)
                plt.plot(expectation_frequencies,expectation)
                plt.plot(actual_frequencies,actual)
                plt.show()
        else:
            if PLOT_ALL:
                expectationPSD, actualPSD, expectation_frequencies, actual_frequencies = PSD_with_freqs(expectation, actual)
                plt.plot(expectation_frequencies,expectationPSD)
                plt.plot(actual_frequencies,actualPSD)
                plt.yscale('log')
                plt.xlabel("Frequency (Hz)")
                plt.ylabel("Amplitude (-)")
                plt.show()
            allRuns_aPeaks.append(aPeaks)
            allRuns_ePeaks.append(ePeaks)
            successful += 1
            print(f"  {int((successful)/number_of_test_harmonics*100)} % complete",end="\r",flush=True)
            
    # Extract individual pairs of peaks -> Stack along first axis 
    allRuns_aPeaks = np.concatenate(allRuns_aPeaks,0)
    allRuns_ePeaks = np.concatenate(allRuns_ePeaks,0)

    # -> Coiterate
    for i,ePeak in enumerate(allRuns_ePeaks):
        aPeak = allRuns_aPeaks[i]
        # Write attenuation / phase difference etc. and peak freqency to data
        amp = peak_AmplitudeAttenuationPercent(ePeak,aPeak)
        width = peak_WidthChangePercent(ePeak,aPeak)
        mag = peak_MagnitudeAttenuationPercent(ePeak,aPeak)
        if not (amp < -100 or amp > 1e6 or width < -100 or width > 1e6 or mag <-100 or mag > 1e6):
            peaksFrequency.append(ePeak[1])
            peaks_AmplitudeAttenuationPercent.append(amp)
            peaks_WidthChangePercent.append(width)
            peaks_MagnitudeAttenuationPercent.append(mag)
        else:
            print(f"Peak failed plot criteria: expected={ePeak}, actual={aPeak}, amp={amp}, width={width}, mag={mag}")
            
    plt.scatter(peaksFrequency,peaks_AmplitudeAttenuationPercent,marker="x",label="Amplitude")
    plt.scatter(peaksFrequency,peaks_WidthChangePercent,marker="x",label="Sigma")
    #plt.scatter(peaksFrequency,peaks_MagnitudeAttenuationPercent,marker="x",label="Amplitude / Sigma")
    
    plt.xlabel("Frequency of PSD peak")
    plt.ylabel("Change in PSD peak parameter (%)")
    plt.legend()
    plt.show()

def paulstretch_compareHarmonicSineAmpScale():
    freqs = np.arange(400,20001,400)
    stretch = 1
    timeWindow = 0.1

    def computeHarmonicHighScaling(freqs,baseF=200):
        return frequencyScan(
            freqs,
            lambda f: component_harmonic(
                [baseF,f],
                stretch=stretch,
                stretchFunction=(
                    lambda axD: paulStretch(stretch,timeWindow,axD)
                )
            ),
            processing_MinusAmplitudeDifference
        )

    ampScale = paulstretch_computeAmpScale(freqs,component_sine,stretch,timeWindow)
    ampScale = ampScale/ampScale[0]
    plt.plot(freqs,ampScale,label="Sine wave")

    ampScale = computeHarmonicHighScaling(freqs)
    ampScale = ampScale/ampScale[0]
    plt.plot(freqs,ampScale,label="Discrepancy in harmonic w/ 200 Hz")

    ampScale = computeHarmonicHighScaling(freqs,baseF=2000)
    ampScale = ampScale/ampScale[0]
    plt.plot(freqs,ampScale,label="Discrepancy in harmonic w/ 2000 Hz")

    plt.xlabel('Frequency of signal (Hz)')
    plt.ylabel('Amptlitude scaling after icwt(cwt())')
    plt.legend()
    plt.show()

def paulstretch_computeAmpScale(freqs,componentFunction,stretch,timeWindow):
    componentGenerator = lambda f: componentFunction(
        f,
        stretch,
        stretchFunction = lambda axD: paulStretch(stretch,timeWindow,axD)
    )
    processing = lambda e, after: np.max(np.abs(after))
    return frequencyScan(freqs,componentGenerator,processing)

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    
    test_attenuationByPeakFrequency()
    #test_sineAmpScaleFactorWithFrequency_varyingMethods()
