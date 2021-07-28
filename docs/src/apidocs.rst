API reference
==============

Magnetometer data
-------------------------------
.. autoclass:: magSonify.MagnetometerData
   :members:
   :private-members:

THEMIS data
---------------
.. autoclass:: magSonify.THEMISdata
   :members:
   :show-inheritance:
   :exclude-members: defaultProcessing

   .. automethod:: magSonify.THEMISdata.defaultProcessing

      The processing is completed by the following code:

      ..  literalinclude:: ../../magSonify/MagnetometerData.py
         :pyobject: THEMISdata.defaultProcessing
         :lines: 11-
         :dedent: 8

DataSet
------------
.. autoclass:: magSonify.DataSet
   :members:
   :special-members: __add__, __sub__, __neg__, __getitem__
   
   .. automethod:: _iterate

      Example of how :meth:`_iterate` is used in :meth:`SimulateData.applyGaussianWhiteNoise`:

      .. literalinclude:: ../../magSonify/SimulateData.py
         :pyobject: SimulateData.applyGaussianWhiteNoise
         :dedent: 4
      
   .. automethod:: _iteratePair

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

Utilities
-----------
.. autofunction:: magSonify.Utilities.ensureFolder