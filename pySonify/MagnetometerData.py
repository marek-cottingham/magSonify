
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d
from scipy.interpolate import interp1d
from . import waveletsLocal as wavelets
from .waveletsLocal.transform import WaveletTransform
from .paulstretch_mono import paulstretch
from ai import cdas

import pySonify

class DataCommon():
    @staticmethod
    def writeoutAudio(audio,outputFile,sampleRate=44100,amplitudeB=1):
        """Outputs audio to file outputFile, where amplitudeB specifices the max amplitude value of 
        audio
        """
        audio = np.nan_to_num(audio)
        audio = audio / amplitudeB
        audio[audio>1] = 1
        audio[audio<-1] = -1
        #wav.write(outputFile,sampleRate,audio)
        sf.write(outputFile,audio,sampleRate)

    def getMeanSampleInterval(s):
        """Gets the mean interval between samples"""
        s.meanSampleInterval = ((s.t[-1] - s.t[0])/len(s.t))

    def meanSampleIntervalRequireFloat(s):
        """Returns the mean sample interval as a float, either the original value if is already a 
        float, or in units of seconds if it is np.timedelta64
        """
        if s.meanSampleInterval is None:
            s.getMeanSampleInterval()

        if isinstance(s.meanSampleInterval,np.timedelta64):
            dt = s.meanSampleInterval / np.timedelta64(1,'s')
        else:
            dt = s.meanSampleInterval
        return dt

    def timeToSecondsFloat(s):
        """Converts times in the form of np.datetime64 to seconds since the start of the data
        """
        s.t = (s.t-s.t[0]) / np.timedelta64(1,'s')

class DataAxis(DataCommon):
    def __init__(s,t,x):
        s.t = t
        s.x = x
        s.meanSampleInterval = s.getMeanSampleInterval()

    def waveletPitchShift(
            s,
            shift=1,
            dj=0.125,
            wavelet=wavelets.wavelets.Morlet(),
            interpolateW_n = None,
            maxNumberSamples = 1200
        ):
        """Pitch shifts the data on specified axes by {shift} times using continous wavlet transform.

        Parameters
        ----------
        shift:
            The multiple by which to shift the pitch of the input field.
        dj:
            Spacing parameter of the scales used in wavlet analysis, a lower value leads to higher
            ...TK... and more processing time.
        wavelet:
            Wavelet function to use. If none is given, the Morlet wavelet will be used by default.
        interpolateW_n:
            If not None, specifies the facator by which the density of the W_n values should be
            increased. This is used to generate additional data points so as to maintain signal
            fidelity after the pitch shift. Doing this after the forward wavelet transform rather
            than before (see DataAxis.interpolate) is much more computationally efficient.
        maxNumberSamples = 1200:
            The maximum number of samples for the largest scale in the wavelet transform, used to
            prevent computations for inaubidle frequencies.

        Returns
        --------------
        Returns a tuple of length 3, where the values corresponding to the axes operated upon 
        contain the wavelets.WaveletTransform() object.
        """

        #maxNumberSamples *= shift

        dt = s.meanSampleIntervalRequireFloat()
        
        # Cannot handle NaN so fill these values with 0
        s.fillNaN()

        # Obtain the wavelet spectrum
        wa = WaveletTransform(
            s.x,
            dt=dt,
            dj=dj,
            wavelet=wavelet,
            maxNumberSamples=maxNumberSamples
        )
        scales = wavelets.transform.generateCwtScales(maxNumberSamples,dj,dt,wavelet,len(s.x))
        W_n = wa.wavelet_transform
        # Rescale the coefficients as in
        #   A Wavelet-based Pitch-shifting Method, Alexander G. Sklar
        #   https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.70.5079&rep=rep1&type=pdf

        magnitude = np.abs(W_n)
        phase = np.unwrap(np.angle(W_n),axis=1)

        if interpolateW_n is not None:
            #W_n = wavelets.interpolateCoeffs(W_n,interpolateW_n)
            magnitude, phase = wavelets.interpolateCoeffsPolar(magnitude,phase,interpolateW_n)
            # TODO: NEED TO CORRECT s.t TO ACCOUNT FOR TIME STRETCH

        W_n_shift = magnitude * np.exp(1j * phase * shift)

        # Reconstruct the wavefuction with pitch shift applied
        #rx= wa.reconstruction(scales=scales/shift,W_n = W_n_shift)
        rx= wa.reconstruction(scales=scales,W_n = W_n_shift)

        s.x = np.real(rx)

        return wa, W_n
    
    def fillNaN(s,const=0):
        """Fills nan values in the magnetic field data with the constant const"""
        s.x = np.nan_to_num(s.x,nan=const)

    def interpolate(s,mult):
        """Interpolates the data, where the density of data points will be increased by mult
        """
        # interpolate cannot accept time values as numpy.datetime64
        if s.t.dtype == np.datetime64 or s.t.dtype == np.timedelta64:
            raise TypeError(
                (f"DataAxis must be a simple numeric type (float or int), not {s.t.dtype}",
                "\n Try calling self.timeToSecondsFloat() first!")
            )

        # create a function f which will interpolate the data.
        f = interp1d(s.t.copy(),s.x.copy(),'cubic')

        # Get the new time values for the interpolated data set. The density of these is scaled by
        # a factor of {mult} and they are evenly spaced.
        s.t = np.linspace(
            s.t[0],
            s.t[-1],
            int(len(s.t)*mult)
        )
        s.x = f(s.t)

    def genMono(s,outputFile,sampleRate=44100,amplitudeB=None,**kwargs):
        """ Generate a mono audio track from the axis data
        """
        audio = s.x.copy()
        if amplitudeB is None:
            amplitudeB = np.max(np.abs(audio))
        s.writeoutAudio(audio,outputFile,sampleRate,amplitudeB=amplitudeB,**kwargs)

    def paulStretch(s,stretch,timeWindow=0.1):
        """ Stretches the data according the paulstretch algorithm
        stretch:
            The factor by which to stretch the data
        timeWindow:
            The window size to be used by the paulstrtch algorithm. A timeWindow of 0.1 is
            equivalent to a window of 4410 data points.
        """
        s.t = np.linspace(
            s.t[0],
            s.t[-1],
            int(len(s.t)*stretch)
        )
        s.x = paulstretch(s.x,stretch,timeWindow)
        

class MagnetometerData(DataCommon):
    def __init__(
        s,
        meanSampleInterval = None
    ):
        """
        Parameters
        ----------
        meanSampleInterval:
            Optional. The mean sample interval in float [s] or timedelta.
        """
        s.meanSampleInterval = meanSampleInterval
        # s.t should be specified either as an array of floats or an array of np.timedelta64
        s.t = [] 
        s.b = [None,None,None]
        s.tPosData = []
        s.pos = [None,None,None]
        s.radius = []
        s.dfChunks = []

    def genMono(s,outputFile,axis=0,sampleRate=44100,**kwargs):
        """Generate a mono audio track from one of the field components
        
        axis: int 0, 1 or 2
        """
        audio = s.b[axis].copy()
        s.writeoutAudio(audio,outputFile,sampleRate,**kwargs)
        
    def genStereo(s,outputFile,sampleRate=44100,**kwargs):
        """Generates a stereo track with all three componets, bx and bz are panned left and right
        """
        audio = np.array([
            s.b[0] + 0.5 * s.b[1],
            0.5 * s.b[1] + s.b[2],
        ])
        s.writeoutAudio(audio.T,outputFile,sampleRate,**kwargs)

    def fillNaN(s,const=0):
        """Fills nan values in the magnetic field data with the constant const"""
        for i,bi in enumerate(s.b):
            s.b[i] = np.nan_to_num(bi,nan=const)

    def runningAverage(s,samples):
        """Generates a running average of the b field, storing it in s.meanB
        """
        if samples == 0:
            raise ValueError("Cannot generate a running average for an interval of 0 samples.")
        s.meanB = [None,None,None]
        for i,bi in enumerate(s.b):
            #s.meanB[i] = np.convolve(bi, np.ones(samples), 'same') / samples
            s.meanB[i] = uniform_filter1d(
                bi,samples,mode='constant',cval=0, origin=0
            )
            # First samples/2 values are distorted by edge effects, so we set them to np.nan
            s.meanB[i][0:samples//2] = np.nan
            s.meanB[i][-samples//2+1:] = np.nan

    def runningAverageWindow(s,timeWindow):
        """Generates a running average for a given time window

        timeWindow:
            If s.t is in np.datetime64:
                The time window for the running average in milliseconds(ms) or timedelta.
            If s.t is in float:
                The time window for the running average in float
        """
        if isinstance(s.meanSampleInterval,np.timedelta64):
            timeWindow = np.timedelta64(timeWindow,'ms')
        n = timeWindow//s.meanSampleInterval
        s.runningAverage(n)
        return n

    def subtractRunningAverage(s,samples=None,timeWindow=None):
        """Subtract the running average from the magnetometer data
        
        Either samples or timeWindow should be specified, or, s.runningAverage() or 
        s.runningAverageWindow() should have already been called
        """
        # Cannot handle NaN
        s.fillNaN()

        if samples is not None:
            s.runningAverage(samples)
        if timeWindow is not None:
            s.runningAverageWindow(timeWindow)
        for i,(bi,meanB) in enumerate(zip(s.b,s.meanB)):
            s.b[i] = bi - meanB

    def readCSV(s,fileName,fileDir="",finalise=True):
        """Reads a CSV file
        
        Derived classes should implement readCSV: should append a data frame to s.dfChunks, before
        calling this method

        finalise: 
            indicates whether the imported pandas data should be merged and coverted to np.array
        """
        if finalise:
            data = pd.concat(s.dfChunks)
            s.t = data.index.to_numpy()
            for i,name in zip((0,1,2),("bx","by","bz")):
                s.b[i] = data[name].to_numpy()

    def readFolder(s,fileDir,**kwargs):
        """Reads in a set of csv files from the folder fileDir
        kwargs:
            parameters passed to readCSV() for each file
        """
        startTime = datetime.now()
        fileNames = os.listdir(fileDir)
        for name in fileNames:
            s.readCSV(name,fileDir,**kwargs)
            # Log to console
            print("Imported",name)
            print("Elapsed time",datetime.now()-startTime)
        # Finalise the data import
        MagnetometerData.readCSV(s,None,None,True)

    def constrainAbsoluteValueB(s,max=400):
        """Limits the data to within bounds of -max to +max, values outside are set to -max or +max
        """
        for bi in s.b:
            bi[bi>max] = max
            bi[bi<-max] = -max
    
    def plotB(s,axes=(0,1,2)):
        """Plots the magnetic field data against time
        """
        if isinstance(axes,int):
            axes = (axes,)
        for i in axes:
            plt.plot(s.t,s.b[i])

    def fillDateTimeRange(s,start=None,end=None,const=0):
        """Fills data between dateTime(start) and dateTime(end) with constant value const
        The endpoints can be given either as absolute datetimes (dateTime or np.datatime64) or as
        relative times to the start of the data (timeDelta or np.timedelta64)
        """
        indicies = [0,None]
        for i,endpoint in enumerate((start,end)):
            if isinstance(endpoint,timedelta) or isinstance(endpoint,np.timedelta64):
                endpoint = s.t[0] + np.timedelta64(endpoint)
            if isinstance(endpoint,datetime) or isinstance(endpoint,np.datetime64):
                indicies[i] = np.argmax(s.t>np.datetime64(endpoint))
        for i,bi in enumerate(s.b):
            bi[indicies[0]:indicies[1]] = const

    def fillLessThanRadius(s,radius=5,const=0):
        """ Fills data at altitudes less than radius with constant value const.
        Radius should be given in Earth Radii
        """
        radiusMask = np.array( s.radius < radius, dtype=np.int8 )
        radiusTransitions = radiusMask[0:-1] - radiusMask[1:] # -1: Start const period, 1 stop period
        transitionNonZero = radiusTransitions[radiusTransitions != 0]
        
        dateTimes = s.tPosData[1:][radiusTransitions != 0]
        dateTimes = list(dateTimes)
        if len(transitionNonZero) != 0:
            if transitionNonZero[0] == 1:
                dateTimes = [None,] + dateTimes
            if transitionNonZero[-1] == -1:
                dateTimes.append(None)

        if len(dateTimes)%2 == 1:
            raise ValueError(
                ("Something went wrong, the length of dateTimes should be even,"
                f" but its {len(dateTimes)}. \r\n Datetimes: {dateTimes}")
            )
        
        timeSlicePairs = []
        for i, x in enumerate(dateTimes):
            if i % 2 == 0:
                timeSlicePairs.append(
                    ( dateTimes[i],dateTimes[i+1] )
                )
        for start, end in timeSlicePairs:
            s.fillDateTimeRange(start,end,const)

    def extractAxis(s,axis):
        return DataAxis(s.t.copy(),s.b[axis].copy())
    
class THEMISdata(MagnetometerData):
    def readCSV(s,fileName,fileDir="",skiprows=65,finalise=True):
        """ Reads in magnetic field data only from a CSV file
        """
        filePath = os.path.join(fileDir,fileName)
        df = pd.read_fwf(
            filePath,
            skiprows=skiprows,
            comment="#",
            skip_blank_lines=True,
            na_values="-1.00000E+30",
            names=("t","-",'bx',"by","bz"),
            widths=(23,14,14,14,14),
            index_col="t",
            skipinitialspace = True,
            parse_dates=[0]
        )
        s.dfChunks.append(df)
        super().readCSV(fileName,fileDir,finalise)
        
    def importCDAS(s,startDate,endDate,satellite="D"):
        """ Imports magnetic field, satellite and radial distance data for the designated THEMIS
            satelliet and given date range.
            The possible satellite letters are: "A", "B", "C", "D" or "E"
        """
        data = cdas.get_data(
            'sp_phys',
            f'TH{satellite.upper()}_L2_FGM',
            startDate,
            endDate,
            [f'th{satellite.lower()}_fgs_gsmQ']
        )
        s.b[0] = data[f"BX_FGS-{satellite}"]
        s.b[1] = data[f"BY_FGS-{satellite}"]
        s.b[2] = data[f"BZ_FGS-{satellite}"]
        s.t = np.array(data["UT"],dtype=np.datetime64)

        data = cdas.get_data(
            'sp_phys',
            f'TH{satellite.upper()}_OR_SSC',
            startDate,
            endDate,
            ['XYZ_GSM','RADIUS'],
        )
        s.pos[0] = data["X"]
        s.pos[1] = data["Y"]
        s.pos[2] = data["Z"]
        s.radius = data["RADIUS"]
        s.tPosData = np.array(data["EPOCH"],dtype=np.datetime64)

    def process(s):
        """ Compact call for the default set of initial processing operations
        """
        s.getMeanSampleInterval()
        s.constrainAbsoluteValueB()
        s.subtractRunningAverage(timeWindow=np.timedelta64(35,'m'))
        s.fillLessThanRadius(6)
        s.fillNaN()