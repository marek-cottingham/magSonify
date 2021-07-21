API reference
==============

Magnetometer data
-------------------------------
.. autoclass:: magSonify.MagnetometerData
   :members:

THEMIS data
---------------
.. autoclass:: magSonify.THEMISdata
   :members:
   :show-inheritance:

DataSet
------------
.. autoclass:: magSonify.DataSet
   :members:
   :private-members: _iterate, _iteratePair
   :special-members: __add__, __sub__, __neg__, __getitem__

DataSet_3D
--------------
.. autoclass:: magSonify.DataSet_3D
   :members:
   :show-inheritance:

DataSet_1D
------------
.. autoclass:: magSonify.DataSet_1D
   :members:
   :show-inheritance:

TimeSeries
---------------
.. autoclass:: magSonify.TimeSeries
    :members:
    :undoc-members:
    :special-members: __eq__, __getitem__

generateTimeSeries
*******************
.. autofunction:: magSonify.generateTimeSeries

Simulate Data
-----------------
.. autoclass:: magSonify.SimulateData
   :members:
   :undoc-members: