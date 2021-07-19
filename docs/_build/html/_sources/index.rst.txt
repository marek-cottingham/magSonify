.. magSonify documentation master file, created by
   sphinx-quickstart on Mon Jul 19 11:21:19 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

magSonify
===============

magSonify enables the sonification of space magnetic field data in python.

It allows for downloading of satellite data from CDA web, processing of this data and generation of
audio. It includes time stretching methods in order to aid sonification of data at low sample rates.

Currently the project provides ready built support for THEMIS satellites only. Users can specify
imports from other satellietes by defining their own subclasses.

Index
==================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Features
--------------
* Import data from CDA web
* Interpolate datasets to standard sample spacing
* Subtract the mean field from data
* Convert magnetic field to mean field align coordinates
* Remove data below a certain altitude
* Remove data in the magnotosheath
* Removing duplicate data points in CDAS data
* Time stretch data for sonification using 4 different algorithms:
   * Wavelet based stretch
   * Paulstretch
   * Phase vocoder
   * WSOLA


Installation
----------------

    pip install git+https://github.com/TheMuonNeutrino/magSonify


Usage example
----------------

::

   import magSonify
   from datetime import datetime

   start = datetime(2008,12,7)
   end = datetime(2008,12,10)
   myTHEMISdata = magSonify.THEMISdata()
   myTHEMISdata.importCdasAsync(
      start,end,satellite='D'
   )
   myTHEMISdata.defaultProcessing(removeMagnetosheath=True,minRadius=4)

   pol = myTHEMISdata.magneticFieldMeanFieldCorrdinates.extractKey(1)
   pol.phaseVocoderStretch(16)
   pol.normalise()
   pol.genMonoAudio("Example of pol x16 with phase vocoder.wav")


Contribute
---------------

- Issue Tracker: github.com/TheMuonNeutrino/magSonify/issues
- Source Code: github.com/TheMuonNeutrino/magSonify

License
----------------
The MIT License. See LICENSE.txt for details.

===============================

API docs
==============
Magnetometer data
-----------------
.. autoclass:: magSonify.MagnetometerData
   :members:

THEMIS data
---------------
.. autoclass:: magSonify.THEMISdata
   :members:

DataSet
------------
.. autoclass:: magSonify.DataSet
   :members:

DataSet_3D
--------------
.. autoclass:: magSonify.DataSet_3D
   :members:

DataSet_1D
------------
.. autoclass:: magSonify.DataSet_1D
   :members:
