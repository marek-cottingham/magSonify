
import context
context.get()

from timeit import default_timer as timer
import os, sys

STRETCH = 16

class encloseTimer():
    times = {}
    def __init__(self,name):
        self.name = name
    def __enter__(self):
        self.start = timer()
        return None
    def __exit__(self,_1,_2,_3):
        self.end = timer()
        if not self.name in self.times:
            self.times[self.name] = []
        self.times[self.name].append(self.end-self.start)
    def printout(self):
        numberDays = 1
        for name, times in self.times.items():
            if name == "Import":
                print(f"{name}: {round(np.mean(times)/numberDays,2)} seconds")
            else:
                print(f"{name}: {round(np.mean(times)/numberDays,2)}" 
                    " seconds per day of themis data")

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

with encloseTimer("Import"):
    from datetime import datetime
    import numpy as np
    import magSonify

sonificationAlgorithms = {
    "waveletStretch": [0.5,STRETCH],
    "paulStretch": [],
    "phaseVocoderStretch": [],
    "wsolaStretch": []
}

X = range(3,10)
#X = (4,)
Xlen = len(X)
for i,day in enumerate(X):

    with HiddenPrints():
        with encloseTimer("Pre-Processing"):
            mag = magSonify.THEMISdata()
            mag.importCDAS(
                datetime(2007,9,day),
                datetime(2007,9,day+1),
            )
            mag.defaultProcessing(removeMagnetosheath= False)
            pol = mag.magneticFieldMeanFieldCoordinates.extractKey(1)

    for algName, args in sonificationAlgorithms.items():
        _pol = pol.copy()
        with encloseTimer(algName):
            getattr(_pol,algName)(STRETCH,*args)
            _pol.normalise()
        if algName == "waveletStretch":
            _pol.genMonoAudio(f"Audio Time Compare\{algName}-half-res x{STRETCH}_{day}.wav",sampleRate=44100//2)
        else:
            _pol.genMonoAudio(f"Audio Time Compare\{algName} x{STRETCH}_{day}.wav")

    print(f"  {round((i+1)/Xlen*100,1)} % complete",end="\r",flush=True)

encloseTimer(None).printout()
sys.stdout = open("Audio Time Compare\\_TimingsLog.txt","w+")
encloseTimer(None).printout()