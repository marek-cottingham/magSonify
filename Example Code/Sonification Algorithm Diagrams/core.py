

import context
context.get()

import magSonify
import datetime
import matplotlib
import matplotlib.pyplot as plt

def setup(
    event = (
        datetime.datetime(2008,12,8),
        datetime.datetime(2008,12,9)
    )
):
    mag = magSonify.THEMISdata()
    mag.importCDAS(
        *event
    )
    mag.defaultProcessing()
    pol = mag.magneticFieldMeanFieldCoordinates.extractKey(1)

    polBefore = pol.copy()
    return pol, polBefore

def setup3axesWithTwinsForWindows(useSubplotVariedLengths):
    if useSubplotVariedLengths:
        fig = plt.figure(figsize=(8,4.5))

        ax1: matplotlib.axes.Axes = plt.subplot2grid((3, 16), (0, 3), rowspan=1, colspan=10)
        ax2: matplotlib.axes.Axes = plt.subplot2grid((3, 16), (1, 3), rowspan=1, colspan=10)
        ax3: matplotlib.axes.Axes = plt.subplot2grid((3, 16), (2, 0), rowspan=1, colspan=16)
    else:
        fig, (ax1, ax2, ax3) = plt.subplots(3,1,figsize=(8,4.5),sharex='all')
        ax1: matplotlib.axes.Axes = ax1
        ax2: matplotlib.axes.Axes = ax2
        ax3: matplotlib.axes.Axes = ax3

    ax1r = ax1.twinx()
    ax3r = ax3.twinx()
    return ax1,ax2,ax3,ax1r,ax3r

def set_xlim(showFullDay_waveforms, showFullDay_spetrogram, axes, preStretchX, timesRelativeToIntervalStart):
    for ax in axes:
        if not showFullDay_waveforms and not showFullDay_spetrogram:
            ax.set_xlim([preStretchX[0],preStretchX[-1]])
        else:
            ax.set_xlim([timesRelativeToIntervalStart[0],timesRelativeToIntervalStart[-1]])

def colorTwinAxes(ax_left, ax_right, ax_left_line, ax_right_line,):
    ax_left.set_zorder(ax_right.get_zorder()+1)
    ax_left.patch.set_visible(False)
    ax_left.yaxis.label.set_color(ax_left_line.get_color())
    ax_left.tick_params(axis='y', colors=ax_left_line.get_color())
    ax_right.yaxis.label.set_color(ax_right_line.get_color())
    ax_right.tick_params(axis='y', colors=ax_right_line.get_color())

def plotWindows(startPos, windowSeries, ax1r, xlimcoeffs, timesRelativeToIntervalStart, numberOfWindows = 4):
    for i,pos in enumerate(startPos[xlimcoeffs]):
        if i < numberOfWindows:
            color = "C1"
        
            lastWindowLine, = ax1r.plot(
            timesRelativeToIntervalStart[
                pos:pos+len(windowSeries)
            ],
            windowSeries,
            color=color,
        )
            
    return lastWindowLine