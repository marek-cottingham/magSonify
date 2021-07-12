from timeit import default_timer as timer

start = timer()
from datetime import datetime
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

from copy import deepcopy

import pySonify as Sonify

end = timer()
print(f"Import time: {end - start}")

mag = Sonify.THEMISdata()

wlTimes = []
psTimes = []
preTimes = []

X = range(3,10)
X = (4,)
numberDays = 2
Xlen = len(X)
for i,day in enumerate(X):

    start = timer()

    mag.importCDAS(
        datetime(2007,9,day),
        datetime(2007,9,int(day+numberDays)),
    )
    mag.process()
    #mag.plotB()
    axD = mag.extractAxis(0)
    axD.timeToSecondsFloat()

    end = timer()
    preTimes.append(end-start)

    ### TEST PARAMETERS ###
    interpolateBefore = 1
    interpolateAfter = 16
    waveletSampleRateFactor = 1
    timeWindow = 0.015
    dj = 0.10

    stretch = interpolateAfter
    maxNumberSamples = int(1200/waveletSampleRateFactor*interpolateBefore)
    #maxNumberSamples = None
    ### END PARAMETERS ###

    if True:
        axWavelet = deepcopy(axD)
        start = timer()
        axWavelet.interpolate(interpolateBefore)
        wa, Wn = axWavelet.waveletPitchShift(
            stretch,interpolateW_n=interpolateAfter,dj = dj,maxNumberSamples=maxNumberSamples,
        )
        end = timer()
        #plt.plot(axWavelet.x)
        plt.show()
        axWavelet.genMono(
            f"wavelet x{stretch} {str(datetime(2007,9,day))[:10]} to {str(datetime(2007,9,day+numberDays-1))[:10]} {interpolateBefore}_{interpolateAfter}.wav",
            sampleRate=int(44100*waveletSampleRateFactor),
            #amplitudeB=25
        )
        wlTimes.append(end-start)

    axPS = deepcopy(axD)
    start = timer()
    axPS.interpolate(1)
    axPS.paulStretch(stretch,timeWindow)
    end = timer()
    axPS.genMono(
        f"paulstretch x{stretch} tw={timeWindow} {str(datetime(2007,9,day))[:10]} to {str(datetime(2007,9,day+numberDays-1))[:10]}.wav"
    )
    psTimes.append(end-start)

    print(f"  {(i+1)/Xlen*100} % complete")

print(f"Wavelets: {np.array(wlTimes)/numberDays} -> {np.mean(wlTimes)/numberDays} seconds per day of themis data")
print(f"Paulstretch: {np.array(psTimes)/numberDays} -> {np.mean(psTimes)/numberDays} seconds per day of themis data")
print(f"Pre-process: {np.array(preTimes)/numberDays} -> {np.mean(preTimes)/numberDays} seconds per day of themis data")