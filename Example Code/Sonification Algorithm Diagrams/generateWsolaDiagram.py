
import core
import context
context.get()

import magSonify
import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.axes
import numpy as np
from audiotsmWithDebugOutput import wsola
from audiotsmWithDebugOutput.io.array import ArrayReader, ArrayWriter

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
### End Params ###

pol, polBefore = core.setup(event)

frameLength = 512
synthesisHop = frameLength//8
reader = ArrayReader(np.array((pol.x,)))
writer = ArrayWriter(reader.channels)
timeSeriesModification = wsola(
    reader.channels,
    speed = 1/stretch,
    frame_length=frameLength,
    synthesis_hop=synthesisHop,
)
timeSeriesModification.run(reader, writer)
pol.x = writer.data.flatten()
pol._stretchTimeseries(stretch)
pol._correctTimeseries()

startPos = np.arange(
    0, len(polBefore.x), timeSeriesModification._analysis_hop
)
windowSeriesAnalysis = np.ones(timeSeriesModification._frame_length)
windowSeriesSynthesis = timeSeriesModification._synthesis_window
#Array of zeros equal to the number of windows generated
coefficients = np.array(timeSeriesModification.STFT_DEBUG)

if useSubplotVariedLengths:
    fig = plt.figure(figsize=(8,4.5))

    ax1: matplotlib.axes.Axes = plt.subplot2grid((2, 16), (0, 3), rowspan=1, colspan=10)
    ax3: matplotlib.axes.Axes = plt.subplot2grid((2, 16), (1, 0), rowspan=1, colspan=16)
else:
    fig, (ax1, ax2, ax3) = plt.subplots(2,1,figsize=(8,4.5),sharex='all')
    ax1: matplotlib.axes.Axes = ax1
    ax3: matplotlib.axes.Axes = ax3

ax1r = ax1.twinx()
ax3r = ax3.twinx()

xlim1 = slice(xlow,xhigh)
xlim2 = slice(xlow*stretch,xhigh*stretch)

timesBefore = polBefore.timeSeries.asFloat()
times = pol.timeSeries.asFloat()

N = coefficients.shape[0]/len(polBefore.x)
xlimcoeffs = slice(int(xlow*N)+1,int(xhigh*N)+5)

# Disable the use of range restriction
if showFullDay_waveforms: 
    xlim1 = xlim2 = slice(None,None)


cmap = 'plasma'

preStretchX = timesBefore[xlim1] - timesBefore[xlow]

timesRelativeToIntervalStart = timesBefore - timesBefore[xlow]

# Plot the analysis windows
for i,pos in enumerate(startPos[xlimcoeffs]):
    if i < 8:
        color = "C1"
    
        lastWindowLine_ax1, = ax1r.plot(
        timesRelativeToIntervalStart[
            pos:pos+len(windowSeriesAnalysis)
        ],
        windowSeriesAnalysis-i,
        color=color,
    )

magFieldPlotLine, = ax1.plot(preStretchX,polBefore.x[xlim1])

# Get the central time of each window in order to plot the coefficients
coefficientsTimes = timesRelativeToIntervalStart[startPos]
coefficientsTimes = coefficientsTimes + (timesRelativeToIntervalStart[1]-timesRelativeToIntervalStart[0])/2

coefficients = coefficients[xlimcoeffs]
coefficients = np.log(coefficients)

coefficientsTimes = coefficientsTimes[xlimcoeffs]

# Get frequencies
freqs = np.fft.rfftfreq(len(windowSeriesSynthesis),3)

# Plot after time stretch
postStretchX = pol.timeSeries.asFloat()[xlim2] - pol.timeSeries.asFloat()[xlow*stretch]

lastWindowLine_ax3 = core.plotWindows(
    startPos, windowSeriesSynthesis, ax3r, xlimcoeffs, timesRelativeToIntervalStart, numberOfWindows=8
)

afterPlotLine, = ax3.plot(postStretchX,pol.x[xlim2])


ax3.set_xlabel("Time since start of interval [s]")
ax1.set_ylabel("Field [nT]")
ax3.set_ylabel("Amplitude")

#ax1r.set_ylabel("Window span")
ax3r.set_ylabel("Window amplitude")

ax1r.set_ylim([-12,1])
plt.setp(ax1r.get_yticklabels(), visible=False)


core.colorTwinAxes(ax1, ax1r, magFieldPlotLine, lastWindowLine_ax1)
core.colorTwinAxes(ax3, ax3r, afterPlotLine, lastWindowLine_ax3)

for ax in (ax1, ):
    plt.setp(ax.get_xticklabels(), visible=False)

core.set_xlim(showFullDay_waveforms, False, (ax1, ax3), preStretchX, timesRelativeToIntervalStart)
ax1r.tick_params(axis='y', colors='w', which='both')

print("Window length:", len(windowSeriesSynthesis))
plt.tight_layout()

magSonify.Utilities.ensureFolder("Algorithm Diagrams")
plt.savefig("Algorithm Diagrams/WSOLA Diagram.svg")


plt.show()