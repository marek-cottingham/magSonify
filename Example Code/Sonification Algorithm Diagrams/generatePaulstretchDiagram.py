import core
import context
context.get()

import magSonify
import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.axes
import numpy as np
from magSonify.sonificationMethods.paulstretch_mono import paulstretch

### Parameters ###
stretch = 2

scan = 150-250
interval = 950

xlow = 6300+scan
xhigh = 6300+scan+interval

useBreakingLines = True
useSubplotVariedLengths = False

event = (
        datetime.datetime(2008,12,7),
        datetime.datetime(2008,12,8)
    )

showFullDay_waveforms = False
showFullDay_spetrogram = False
### End Params ###

pol, polBefore = core.setup(event)

pol._stretchTimeseries(stretch)
pol.x, coefficients = paulstretch(pol.x,stretch,0.015,debugOutput=True)
pol._correctTimeseries()

if useSubplotVariedLengths:
    fig = plt.figure(figsize=(16,9))

    ax1: matplotlib.axes.Axes = plt.subplot2grid((3, 16), (0, 3), rowspan=1, colspan=10)
    ax2: matplotlib.axes.Axes = plt.subplot2grid((3, 16), (1, 3), rowspan=1, colspan=10)
    ax3: matplotlib.axes.Axes = plt.subplot2grid((3, 16), (2, 0), rowspan=1, colspan=16)
else:
    fig, (ax1, ax2, ax3) = plt.subplots(3,1,figsize=(8,4.5),sharex='all')


ax1: matplotlib.axes.Axes = ax1
ax2: matplotlib.axes.Axes = ax2
ax3: matplotlib.axes.Axes = ax3

xlim1 = slice(xlow,xhigh)
xlim2 = slice(xlow*stretch,xhigh*stretch)

timesBefore = polBefore.timeSeries.asFloat()
times = pol.timeSeries.asFloat()

N = coefficients.shape[0]/len(polBefore.x)
xlimcoeffs = slice(int(xlow*N),int(xhigh*N)+2)

# Disable the use of range restriction
if showFullDay_spetrogram: 
    xlim1 = xlim2 = slice(None,None)
if showFullDay_waveforms:
    xlimcoeffs = slice(None,None)


cmap = 'plasma'

preStretchX = timesBefore[xlim1] - timesBefore[xlow]

timesRelativeToIntervalStart = timesBefore - timesBefore[xlow]

ax1.plot(preStretchX,polBefore.x[xlim1])

coefficientsTimes = np.linspace(
    timesRelativeToIntervalStart[0],
    timesRelativeToIntervalStart[-1],
    coefficients.shape[0]+1
)[:-1]
coefficientsTimes += (timesRelativeToIntervalStart[1]-timesRelativeToIntervalStart[0])/2

coefficients = coefficients[xlimcoeffs,:]
coefficients = np.log(coefficients)
coefficientsTimes = coefficientsTimes[xlimcoeffs]

print(coefficientsTimes)

ax2.pcolormesh(
    coefficientsTimes,
    np.arange(0,coefficients.shape[1]),
    coefficients.T,
    shading='auto',
    cmap=cmap,
)

if useBreakingLines:
    lw = 4
    ax2.grid(True, which='minor', axis='x', linestyle='-', color='k',linewidth=lw)
    ax2.set_xticks(
        coefficientsTimes + (coefficientsTimes[1]-coefficientsTimes[0])/2,
        minor=True
    )

postStretchX = pol.timeSeries.asFloat()[xlim2] - pol.timeSeries.asFloat()[xlow*stretch]

ax3.plot(postStretchX,pol.x[xlim2])

ax2.set_yscale('log')

ax3.set_xlabel("Time since start of interval [s]")
ax1.set_ylabel("Field [nT]")
ax2.set_ylabel("Frequency [Hz]")
ax3.set_ylabel("Amplitude")

for ax in (ax1, ax2):
    plt.setp(ax.get_xticklabels(), visible=False)

for ax in (ax1,ax2,ax3):
    ax.set_xlim([preStretchX[0],preStretchX[-1]])

plt.show()
plt.savefig("Paulstretch Diagram.svg")