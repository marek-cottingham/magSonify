import soundfile
import numpy as np

def writeoutAudio(audio,outputFile,sampleRate=44100):
        audio = np.nan_to_num(audio)
        audio[audio>1] = 1
        audio[audio<-1] = -1
        
        soundfile.write(outputFile,audio,sampleRate)