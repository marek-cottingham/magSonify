
from .TimeSeries import TimeSeries
from .DataSet_1D import DataSet_1D, DataSet_1D_placeholder
from typing import List
import numpy as np
import operator
from ai import cdas

class Orbit():
    def __init__(self,start,end,periodOfInterest=None):
        self.start = np.datetime64(start)
        self.end = np.datetime64(end)
        self.previous = None
        self.next = None
        if periodOfInterest is None:
            self.periodOfInterest = (self.start,self.end)
        else:
            self.periodOfInterest = periodOfInterest

    def __repr__(self):
        return f"Orbit({self.start},{self.end},periodOfInterest={self.periodOfInterest}"

class OrbitStore():
    def __init__(self,orbits=[]):
        self.len = 0
        self.orbits = orbits

    def __len__(self):
        return len(self.orbits)

    def addOrbit(self, orbit: Orbit) -> None:
        self.orbits.append(orbit)

    def getOnDate(self, date) -> List[Orbit]:
        date = np.datetime64(date)
        dateStart = date
        dateEnd = date + np.timedelta64(1,'D')
        dateOrbits = []
        for orbit in self.orbits:
            if orbit.end >= dateStart and orbit.start <= dateEnd:
                dateOrbits.append(orbit)
        dateOrbits.sort(key=operator.attrgetter('start'))
        return dateOrbits

class OrbitAnalysis():
    def importFromCdas(self):
        self.radius = DataSet_1D_placeholder
        raise NotImplementedError

    def smoothOrbit(self):
        self.radius = self.radius.runningAverage(samples=10)

    def findPeriapses(self):
        delta_r = self.radius.x[1:] - self.radius.x[:-1]
        sign_delta_r = delta_r
        sign_delta_r[sign_delta_r >= 0] = 1
        sign_delta_r[sign_delta_r < 0] = -1
        mask_transitions = sign_delta_r[1:] - sign_delta_r[:-1] # -2 is apoapsis, 2 is periapsis
        periapsisIndexes = mask_transitions == 2
        periapsisTimes = self.radius.timeSeries.asDatetime()[1:-1][periapsisIndexes]
        self.periapsisIndicies = periapsisIndexes
        self.periapsisTimes = periapsisTimes

    def extractOrbits(self):
        self.orbits = []
        for istart, iend, start, end in zip(
            self.periapsisIndicies[:-1],
            self.periapsisIndicies[1:],
            self.periapsisTimes[:-1],
            self.periapsisTimes[1:]
        ):
            self.orbits.append(
                Orbit(start,end)
            )

class THEMIS_OrbitAnalysis(OrbitAnalysis):
    def importFromCdas(self,startDate,endDate,satellite='d'):
        data = cdas.get_data(
            'sp_phys',
            f'TH{satellite.upper()}_OR_SSC',
            startDate,
            endDate,
            ['RADIUS'],
        )
        self.radius = DataSet_1D(
            TimeSeries(data["EPOCH"]),
            data["RADIUS"]
        )