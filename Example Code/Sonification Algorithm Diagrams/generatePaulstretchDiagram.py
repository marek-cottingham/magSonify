
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

scan = -64 # Allows shifting the start of the interval
interval = 512//2*3 # Number of samples in the interval

xlow = 6272+scan
xhigh = 6272+scan+interval

useBreakingLines = True
useSubplotVariedLengths = True

event = (
        datetime.datetime(2008,12,7),
        datetime.datetime(2008,12,8)
    )

showFullDay_waveforms = False
showFullDay_spetrogram = False
### End Params ###

pol, polBefore = core.setup(event)

pol._stretchTimeseries(stretch)
# Window for paulstretch is specifed so as to be equivalent to a window of 512 samples when using 
# the default sample rate of 44100
pol.x, coefficients, startPos, windowSeries = paulstretch(pol.x,stretch,512/44100,debugOutput=True)
pol._correctTimeseries()


ax1, ax2, ax3, ax1r, ax3r = core.setup3axesWithTwinsForWindows(useSubplotVariedLengths)


xlim1 = slice(xlow,xhigh)
xlim2 = slice(xlow*stretch,xhigh*stretch)

timesBefore = polBefore.timeSeries.asFloat()
times = pol.timeSeries.asFloat()

N = coefficients.shape[0]/len(polBefore.x)
xlimcoeffs = slice(int(xlow*N)-1,int(xhigh*N)+2)

# Disable the use of range restriction
if showFullDay_waveforms: 
    xlim1 = xlim2 = slice(None,None)
if showFullDay_spetrogram:
    xlimcoeffs = slice(None,None)


cmap = 'plasma'

preStretchX = timesBefore[xlim1] - timesBefore[xlow]

timesRelativeToIntervalStart = timesBefore - timesBefore[xlow]

lastWindowLine_ax1 = core.plotWindows(startPos, windowSeries, ax1r, xlimcoeffs, timesRelativeToIntervalStart)

magFieldPlotLine, = ax1.plot(preStretchX,polBefore.x[xlim1])

coefficientsTimes = timesRelativeToIntervalStart[startPos]
coefficientsTimes = coefficientsTimes + (timesRelativeToIntervalStart[1]-timesRelativeToIntervalStart[0])/2

coefficients = coefficients[xlimcoeffs,:]
coefficients = np.log(coefficients)
coefficientsTimes = coefficientsTimes[xlimcoeffs]

freqs = np.fft.rfftfreq(len(windowSeries),3)

ax2.pcolormesh(
    coefficientsTimes,
    freqs,
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

lastWindowLine_ax3 = core.plotWindows(startPos, windowSeries, ax3r, xlimcoeffs, timesRelativeToIntervalStart)

afterPlotLine, = ax3.plot(postStretchX,pol.x[xlim2])

ax2.set_yscale('log')
ax2.set_ylim([
    freqs[1],freqs[-50]
])

ax3.set_xlabel("Time since start of interval [s]")
ax1.set_ylabel("Field [nT]")
ax2.set_ylabel("Frequency [Hz]")
ax3.set_ylabel("Amplitude")
ax1r.set_ylabel("Window amplitude")
ax3r.set_ylabel("Window amplitude")

core.colorTwinAxes(ax1, ax1r, magFieldPlotLine, lastWindowLine_ax1)
core.colorTwinAxes(ax3, ax3r, afterPlotLine, lastWindowLine_ax3)

for ax in (ax1, ax2):
    plt.setp(ax.get_xticklabels(), visible=False)

core.set_xlim(showFullDay_waveforms, showFullDay_spetrogram, (ax1, ax2, ax3), preStretchX, timesRelativeToIntervalStart)

print("Window length:", len(windowSeries))
plt.tight_layout()

magSonify.Utilities.ensureFolder("Algorithm Diagrams")
plt.savefig("Algorithm Diagrams/Paulstretch Diagram.svg")

plt.show()