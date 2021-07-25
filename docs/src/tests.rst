Tests
=======

A series of tests have been built for the library in order to identify common issues.
These should be run before making a new commit, by running ``./runStandardTests.py``

Testing files:

``./Tests_Unit/ProcessingSanityTest.py``

    Test to catch errors in processing code. Executes a broad set of import, data processing and 
    sonification functions. In particular looks for mismatch between length of 
    :attr:`magSonify.DataSet.timeSeries` and values in :attr:`magSonify.DataSet.data`, a common 
    bug which arises due to :attr:`magSonify.DataSet.timeSeries` not being updated correctly or 
    being modified while shared between multiple data sets.

``./Tests_Unit/SimulateDataTest.py``

    Testing for some methods in :class:`magSonify.SimulateData`. Incomplete.

``./Tests_Unit/TimeSeriesTest.py``

    Testing for some methods in :class:`magSonify.TimeSeries`. Incomplete.