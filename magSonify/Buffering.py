
from threading import local

from numpy.lib.shape_base import apply_along_axis
from magSonify.DataSet_1D import DataSet_1D
from magSonify.MagnetometerData import MagnetometerData, THEMISdata
import multiprocessing as mp
import sounddevice
from timeit import default_timer as timer
import sys, os
import numpy as np
from time import sleep

class STOPVALUE:
    """
    Indicates that a queue has finished, no new values will be put. eg.
    
    ::

        def myWorker():
            while True:
                # Does some processing, breaks out of the loop when done
                myQueue.put(val)
                break
            myQueue.put(STOPVALUE())
    """
    pass

class BaseProcess(mp.Process):
    """Base process for multiprocessing"""

    def __init__(self, task, taskArgs, queues, name=None):
        if name is None:
            name = task
        super().__init__(
            target = getattr(self,task),
            args = taskArgs,
            name = name,
        )
        self.importedQueue = queues[0]
        self.processedQueue = queues[1]
        self.sonifiedQueue = queues[2]
        self.startTime = timer()

    def importer(self, events: tuple, dataClass = THEMISdata):
        """ Multiprocessing wrapper of CDAS import.

        :param dataClass:
            The high level class for satellite data, subclassed from 
            :class:`MagnetometerData`. eg. :class:`THEMISdata`.
            Should implement method ``.importCDAS(startDatetime,endDateTime,[*args])``
            Should implement method ``.defaultProcessing([*args])``
        :param events: 
            Tuple, each value contain a tuple with args for importCDAS in the form
            (startDatetime,endDatetime,*args)
        """

        for event in events:
            try:
                mag: THEMISdata = dataClass()
                mag.importCDAS(*event)
                self.importedQueue.put(mag)
            except Exception as e:
                print(f"Exception importing interval starting on {event[0]}, skipping")
                print(e)
                pass
            #print(f"Imported {event[0]} @ {timer() - self.startTime} s")
        self.importedQueue.put(STOPVALUE())

    def processing(self, processingArgs: tuple = ()):
        """Multiprocessing wrapper of default processing.

        :param processingArgs:
            Args for ``dataClass.defaultProcessing``
            (See for example: :meth:`THEMISdata.defaultProcessing`)
        """
        try:
            while True:
                mag: THEMISdata = self.importedQueue.get()
                if isinstance(mag, STOPVALUE):
                    break
                mag.defaultProcessing(*processingArgs)
                self.processedQueue.put(mag)
                #print(f"Processed {mag.magneticField.timeSeries.getStart()} @ {timer() - self.startTime} s")
            self.processedQueue.put(STOPVALUE())
        except Exception:
            self.processedQueue.put(STOPVALUE())
            print("Exception processing interval starting at:",mag.position.timeSeries.getStart())
            raise

    def sonification(self,axis: int = 1, algorithm: str = "waveletStretch", algArgs: tuple = (16, 0.5, 16)):
        """Multiprocessing wrapper of time stretching signal for sonification.

        :param int axis:
            The axis along which to extract sound audio. Can be ``int`` ``0``, ``1`` or ``2``.
        :param algorithm:
            String referencing the time stretching algorithm to use. Can be ``'waveletStretch'``, 
            ``'paulStretch'``, ``'phaseVocoderStretch'`` or ``'wsolaStretch'``.
        :param Tuple algArgs:
            The arguments to be passed to time stretching function.
        """
        try:
            while True:
                mag: THEMISdata = self.processedQueue.get()
                if isinstance(mag, STOPVALUE):
                    break
                ax = mag.magneticFieldMeanFieldCoordinates.extractKey(axis)
                getattr(ax,algorithm)(*algArgs)
                ax.normalise()
                self.sonifiedQueue.put(ax)
                #print(f"Sonified {mag.magneticField.timeSeries.getStart()} @ {timer() - self.startTime} s")
            self.sonifiedQueue.put(STOPVALUE())
        except Exception:
            self.processedQueue.put(STOPVALUE())
            print("Exception sonifying interval starting at:",ax.timeSeries.getStart())
            raise

    def playback(self,sampleRate=44100//2):
        """Multiprocessing method for playing audio as a continous output stream"""

        availableAudio = np.zeros(1,dtype=np.float64)
        audioLock = mp.Lock()
        finishAudioProcessingEvent = mp.Event()
        donePlayingEvent = mp.Event()
        i = 0

        def audioCallback(outdata,frames,time,status):
            nonlocal availableAudio
            nonlocal i
            if status:
                print(status)
            with audioLock:
                if len(availableAudio) < frames:
                    outdata[:len(availableAudio),0] = availableAudio[:]
                    outdata[len(availableAudio):].fill(0)
                    availableAudio = np.zeros(2,dtype=np.float64)
                    if finishAudioProcessingEvent.is_set():
                        raise sounddevice.CallbackStop
                    print("    Waiting on audio...")
                else:
                    outdata[:,0] = availableAudio[0:frames]
                    availableAudio = availableAudio[frames:]
                print("Audio left: ", round(len(availableAudio)/44100,1),"s       ",end='\r',flush=True)
            i += 1

        myStream = sounddevice.OutputStream(
            samplerate=sampleRate//2,
            blocksize=44100//10,
            callback=audioCallback,
            finished_callback=donePlayingEvent.set,
            channels = 1,
        )

        while True:
            if len(availableAudio) > 44100 * 30:
                sleep(0.01)
                continue
            ax: DataSet_1D = self.sonifiedQueue.get()
            if isinstance(ax, STOPVALUE):
                finishAudioProcessingEvent.set()
                break
            #print(f"Playing {ax.timeSeries.getStart()} @ {timer() - self.startTime})")
            
            with audioLock:
                availableAudio = np.concatenate((availableAudio,ax.x))

            if myStream.stopped:
                myStream.start()
        donePlayingEvent.wait()
            
