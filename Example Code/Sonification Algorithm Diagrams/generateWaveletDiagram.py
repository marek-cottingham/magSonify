
import core
import context
context.get()

import magSonify
import datetime
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.axes
import numpy as np
import cmocean
from magSonify.sonificationMethods.wavelets.wavelets import Morlet

### Figure parameters ###

stretch: int = 2

event = (datetime.datetime(2008,12,7),
    datetime.datetime(2008,12,8))

scan = 200 # Allows shifting the start of the interval
interval = 45 # Number of samples in the interval

xlow = 6300+scan
xhigh = 6300+scan+interval

plotPhases = True
plotEntireDay = False

useBreakingLines = useSubplotVariedLengths = True

### End params ###

# Generate the data series needed
pol, polBefore = core.setup(
    event    
)

# Time stretch
pol.waveletPitchShift(stretch,preserveScaling=True,interpolateFactor=stretch,maxNumberSamples=100)


if useSubplotVariedLengths:
    fig = plt.figure(figsize=(16,9))

    ax1: matplotlib.axes.Axes = plt.subplot2grid((4, 16), (0, 3), rowspan=1, colspan=10)
    ax2: matplotlib.axes.Axes = plt.subplot2grid((4, 16), (1, 3), rowspan=1, colspan=10)
    ax3: matplotlib.axes.Axes = plt.subplot2grid((4, 16), (2, 0), rowspan=1, colspan=16)
    ax4: matplotlib.axes.Axes = plt.subplot2grid((4, 16), (3, 0), rowspan=1, colspan=16)
else:
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1,figsize=(16/2,9/2))

ax1r = ax1.twinx()

if plotPhases:
    phaseMagSelector = np.angle
    #cmap = 'hsv'
    #cmap = 'twilight_shifted'
    cmap = 'cmo.phase'
else:
    # Note that the log of the magnitude is being plotted
    phaseMagSelector = lambda x : np.log(np.abs(x)) 
    cmap = 'plasma'
    scan = 0

xlim1 = slice(xlow,xhigh)
xlim2 = slice(xlow*stretch-stretch//2,xhigh*stretch-stretch//2)

if plotEntireDay:
    xlim1 = xlim2 = slice(None,None)

# X axis values for before stretching
timesBefore = polBefore.timeSeries.asFloat()
preStretchX = timesBefore[xlim1] - timesBefore[xlow]

magFieldPlotLine, = ax1.plot(preStretchX,polBefore.x[xlim1])

Y = pol.scales

waveletFunction = Morlet()
exampleWaveletRelativeTimes = np.linspace(0,len(preStretchX),1000) - len(preStretchX)//2
for i in range(0,21,7):
    exampleWavelet = waveletFunction(exampleWaveletRelativeTimes,Y[i])

    waveletPlotLine, = ax1r.plot(
        np.linspace(preStretchX[0],preStretchX[-1],1000),
        -exampleWavelet,
        color='C1' #+ str(i+1)
    )

ax2.pcolormesh(
    preStretchX,
    Y,
    phaseMagSelector(pol.coefficients[:,xlim1]),
    shading='auto',
    cmap=cmap,
)

# X axis values for after stretching
times = pol.timeSeries.asFloat()
postStretchX = times[xlim2] - times[xlow*stretch]

ax3.pcolormesh(
    postStretchX,
    Y,
    phaseMagSelector(pol.coefficients_shifted[:,xlim2]),
    shading='auto',
    cmap=cmap
)

ax4.plot(postStretchX,pol.x[xlim2])

ax4.set_xlabel("Time since start of interval [s]")
ax1.set_ylabel("Field [nT]")
ax1r.set_ylabel("Wavelet amplitude")
ax4.set_ylabel("Amplitude")

core.colorTwinAxes(ax1, ax1r, magFieldPlotLine, waveletPlotLine)

if plotEntireDay:
    xhigh = -1
    xlow = 0

# Set the x-axis limits to exactly the range under consideration
for ax in (ax1, ax2, ax3, ax4):
    ax.set_xlim([
        -1,timesBefore[xhigh-1]-timesBefore[xlow]+1
    ])

for ax in (ax2, ax3):
    plt.sca(ax)
    plt.yscale('log')
    plt.ylabel("Scale [s]")

if useBreakingLines:
    bbox = ax2.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width = bbox.width
    lw = width*fig.dpi/interval * 1/10
    ax2.grid(True, which='minor', axis='x', linestyle='-', color='k',linewidth=lw)
    ax2.set_xticks(
        preStretchX + 
            (preStretchX[1]-preStretchX[0])/2, # Shifts line to edge of block
        minor=True,
    )
    ax2.tick_params(axis='x', colors='w')

    lw = 1
    ax3.grid(True, which='minor', axis='x', linestyle='-', color='k',linewidth=lw)
    ax3.set_xticks(
        postStretchX + 
            (postStretchX[1]-postStretchX[0])/2, # Shifts line to edge of block
        minor=True,
    )
    ax3.tick_params(axis='x', colors='w')

for ax in (ax1,ax2,ax3,):
    plt.setp(ax.get_xticklabels(), visible=False)

magSonify.Utilities.ensureFolder("Algorithm Diagrams")
if plotPhases:
    plt.savefig("Algorithm Diagrams/Wavelet Diagram Phases.svg")
else:
    plt.savefig("Algorithm Diagrams/Wavelet Diagram Magnitudes.svg")

plt.show()
