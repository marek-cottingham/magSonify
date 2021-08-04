from datetime import datetime

import context
context.get()

from magSonify.OrbitStore import Orbit, OrbitStore
import unittest

class OrbitTestCase(unittest.TestCase):
    def _genStartEndOrbit(self):
        myOrbit = Orbit(
            start=datetime(
                2007,2,18,5
            ),
            end = datetime(
                2007,2,19,23
            )
        )
        return myOrbit

    def test_canInitAndRecallStartAndEndDatetime(self):
        myOrbit = self._genStartEndOrbit()
        self.assertEqual(myOrbit.start,datetime(2007,2,18,5))
        self.assertEqual(myOrbit.end,datetime(2007,2,19,23))

    def test_ifNoPreviousOrbit_ReturnsNone(self):
        myOrbit = self._genStartEndOrbit()
        self.assertEqual(myOrbit.previous,None)

    def test_ifNoNextOrbit_ReturnsNone(self):
        myOrbit = self._genStartEndOrbit()
        self.assertEqual(myOrbit.next,None)

    def test_ifNotSpecified_interestIntervalCoversAll(self):
        myOrbit = self._genStartEndOrbit()
        poi = myOrbit.periodOfInterest
        self.assertEqual(poi[0],datetime(2007,2,18,5))
        self.assertEqual(poi[1],datetime(2007,2,19,23))

class OrbitStoreTestCase(unittest.TestCase):
    def test_ifIsEmpty_lengthIsZero(self):
        myOrbitStore = OrbitStore()
        self.assertEqual(len(myOrbitStore),0)

    def test_ifTwoAdded_lengthIsTwo(self):
        myOrbitStore = self._initWithTwoOrbits()
        self.assertEqual(len(myOrbitStore),2)

    def _initWithTwoOrbits(self):
        myOrbitStore = OrbitStore()
        myOrbitStore.addOrbit(Orbit(datetime(2007,2,19,5),datetime(2007,2,20,5)))
        myOrbitStore.addOrbit(Orbit(datetime(2007,2,20,5),datetime(2007,2,21,5)))
        return myOrbitStore

    def test_canFindByDateSingle(self):
        myOrbitStore = self._initWithTwoOrbits()
        res = myOrbitStore.getOnDate(datetime(2007,2,19))
        self.assertEqual(len(res),1)
        res = res[0]
        self.assertEqual(res.start,datetime(2007,2,19,5))
        self.assertEqual(res.end,datetime(2007,2,20,5))

    def test_canFindByDatePair(self):
        myOrbitStore = self._initWithTwoOrbits()
        res = myOrbitStore.getOnDate(datetime(2007,2,20))
        self.assertEqual(len(res),2)
        self.assertEqual(res[0].start,datetime(2007,2,19,5))
        self.assertEqual(res[0].end,datetime(2007,2,20,5))
        self.assertEqual(res[1].start,datetime(2007,2,20,5))
        self.assertEqual(res[1].end,datetime(2007,2,21,5))

    def test_getOnDate_returnsSortedInOrder(self):
        myOrbitStore = OrbitStore()
        myOrbitStore.addOrbit(Orbit(datetime(2007,2,20,5),datetime(2007,2,21,5)))
        myOrbitStore.addOrbit(Orbit(datetime(2007,2,19,5),datetime(2007,2,20,5)))

        res = myOrbitStore.getOnDate(datetime(2007,2,20))
        self.assertEqual(len(res),2)
        self.assertEqual(res[0].start,datetime(2007,2,19,5))
        self.assertEqual(res[0].end,datetime(2007,2,20,5))
        self.assertEqual(res[1].start,datetime(2007,2,20,5))
        self.assertEqual(res[1].end,datetime(2007,2,21,5))
        

    
if __name__ == '__main__':
    unittest.main()
