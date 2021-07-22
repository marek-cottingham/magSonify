from magSonify.DataSet_1D import DataSet_1D
import numpy as np
import scipy as sp
from scipy.signal import stft
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import magSonify
import os
import subprocess
import shutil

OVERRIDE_FRAME_RATE = 25
videoDir = 'Audio & Video 2021 07 21'
#algname = "Wavelet"
algname = "Phase_Vocoder"

if not os.path.exists(videoDir):
        os.mkdir(videoDir)
if not os.path.exists(os.path.join(videoDir,"frames")):
        os.mkdir(os.path.join(videoDir,"frames"))

start_time = datetime(2008, 12, 7)
end_time = datetime(2008, 12, 10)

mag = magSonify.THEMISdata()
mag.importCDAS(
    start_time, end_time
)
mag.defaultProcessing()

component_n = 0

component = mag.magneticFieldMeanFieldCoordinates.extractKey(component_n)
audio: DataSet_1D = component.copy()
if algname == "Wavelet":
    audio.waveletStretch(16,interpolateBefore=0.5,interpolateAfter=16)
    audio.genMonoAudio(os.path.join(videoDir, f"{algname}_audio_axis={component_n}.wav"),sampleRate=44100//2)
    n_frames = len(audio.x) * OVERRIDE_FRAME_RATE // (44100//2)
if algname == "Phase_Vocoder":
    audio.phaseVocoderStretch(16)
    audio.genMonoAudio(os.path.join(videoDir, f"{algname}_audio_axis={component_n}.wav"),sampleRate=44100)
    n_frames = len(audio.x) * OVERRIDE_FRAME_RATE // (44100)

#Compute the Short Time Fourier Transform (STFT)
nperseg = 1024//2
f, t, Zxx_dBdt = stft(component.x, fs=1/3.0, nperseg=nperseg, noverlap=nperseg//4*3)
dt_list = [start_time+timedelta(seconds=ii) for ii in t]

myFmt = mdates.DateFormatter('%H:%M')
xlim=[start_time,end_time]


argframes = np.floor(np.linspace(0,len(component.x),n_frames)).astype(np.int32)
argframes = argframes[:-1]

print("Writing output frames")

#plot pol
fig = plt.figure(figsize=(16,9))

ax1: matplotlib.axes.Axes = plt.subplot2grid((4, 5*9), (0, 0), rowspan=2, colspan=3*9)
ax2: matplotlib.axes.Axes = plt.subplot2grid((4, 5*9), (2, 0), rowspan=2, colspan=3*9, sharex=ax1)
ax3: matplotlib.axes.Axes = plt.subplot2grid((4, 5*9), (1, 3*9), rowspan=2, colspan=2*7)

ax1.plot(component.timeSeries.asDatetime(), component.x, 'b')
ax1.set_ylabel('pol [nT]',fontsize=10)
ax1.set_xlim(xlim)
ax1.set_ylim([-5,5])

# #plot spectra
cmap=plt.get_cmap('inferno')
im=ax2.pcolormesh(dt_list, f*1000., np.abs(Zxx_dBdt), vmin=0, vmax=0.04, shading='auto', cmap=cmap)
ax2.set(ylim=[0,25])
ax2.xaxis.set_major_formatter(myFmt)
#ax2.set_title('STFT Magnitude')
ax2.set_ylabel('Frequency [mHz]',fontsize=10)
ax2.set_xlabel('Time [UT]',fontsize=10)

ax3.yaxis.tick_right()
ax3.plot(mag.position.data[0],mag.position.data[1])
ax3.plot(0,0,marker='.',color='b')
ax3.set(xlim=[-6,6])
ax3.set_title("Radius: n RE")

plt.setp(ax1.get_xticklabels(), visible=False)

for i,frameArg in enumerate(argframes):
    if i>=1000: #Used to skip frames if continuing aftor crash
        try:
            temp1 = ax1.axvline(component.timeSeries.asDatetime()[frameArg],color='r')
            temp2 = ax2.axvline(component.timeSeries.asDatetime()[frameArg],color='r')
            temp3 = ax3.plot(mag.position.data[0][frameArg],mag.position.data[1][frameArg],color='r',marker=".")
            ax3.set_title(
                "Radius: {0:.1f} Earth radii".format(mag.position.data['radius'][frameArg])
            )

            plt.savefig(os.path.join(videoDir,"frames",f'frame_{("000"+str(i))[-4:]}.png'))
            
            temp1.remove()
            temp2.remove()
            for j in temp3: j.remove()

            print(f"  {round(i*100/n_frames,1)} % complete",end='\r',flush=True)

        except IndexError:
            break

os.chdir(os.path.join(videoDir,"frames"))

subprocess.call(['ffmpeg', '-framerate',str(OVERRIDE_FRAME_RATE),'-i', 'frame_%04d.png', 
    f'Animated_plot_axis={component_n}.mp4']
)
os.chdir("..")
shutil.move( os.path.join("frames",f'Animated_plot_axis={component_n}.mp4'),f'Animated_plot_axis={component_n}.mp4')

subprocess.call(["ffmpeg", "-i", f"Animated_plot_axis={component_n}.mp4", "-i", f"{algname}_audio_axis={component_n}.wav", 
    "-c", "copy", f"{algname}_video_axis={component_n}.mkv"])