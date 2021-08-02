"""
DEVELOPMENT TESTING
MAY BE INCOMPLETE / NON FUNCTIONAL

Testing orbit identification code
"""

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from datetime import date, datetime

import context
context.get()

import magSonify
from magSonify.OrbitStore import OrbitStore, OrbitAnalysis, THEMIS_OrbitAnalysis

anyl = THEMIS_OrbitAnalysis()
anyl.importFromCdas(
    datetime(2007,3,1),
    datetime(2007,4,1)
)
anyl.smoothOrbit()
anyl.findPeriapses()
anyl.extractOrbits()
plt.plot(anyl.radius.timeSeries.asDatetime(),anyl.radius.x)
for i,orbit in enumerate(anyl.orbits):
    if i%2 == 0:
        plt.axvline(orbit.start,color='red')
    else:
        plt.axvline(orbit.start,color='orange')
plt.show()