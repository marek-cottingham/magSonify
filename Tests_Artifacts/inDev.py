import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from datetime import datetime
import os
import importlib

import baseMethods

import context
context.get()

import magSonify
from magSonify import SimulateData

before, expect = baseMethods.getBeforeAndExpectation_Sweep(4000,50,0.2)
actual = before.copy()
actual.waveletStretch(16)

fig, axs = plt.subplots(2,1)
s1, f1, t1, _ = axs[0].specgram(expect.x,Fs=44100)
s2, f2, t2, _ = axs[1].specgram(actual.x,Fs=44100)
s = s2-s1[:,:s2.shape[1]]
plt.close()
plt.imshow(s,extent=(t1[0],t1[-1],f1[0],f1[-1]),origin='lower',aspect='auto')
plt.show()