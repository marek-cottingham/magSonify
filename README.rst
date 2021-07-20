MagSonify
================

MagSonify enables the sonification of space magnetic field data in python.

It allows for downloading of satellite data from CDA web, processing of this data and generation of
audio. It includes time stretching methods in order to aid sonification of data at low sample rates.

Currently the project provides ready built support for THEMIS satellites only. Users can specify
imports from other satellites by defining their own subclasses.

- Docs: https://magsonify.readthedocs.io/en/latest/src/introduction.html
- Issue Tracker: https://github.com/TheMuonNeutrino/magSonify/issues
- Source Code: https://github.com/TheMuonNeutrino/magSonify


Features
------------------
* Import data from CDA web
* Interpolate datasets to standard sample spacing
* Subtract the mean field from data
* Convert magnetic field to mean field align coordinates
* Remove data below a certain altitude
* Remove data in the magnotosheath
* Removing duplicate data points in CDAS data
* Time stretch data for sonification using 4 different algorithms
   * Wavelet based stretch
   * Paulstretch
   * Phase vocoder
   * WSOLA


Installation
--------------------

.. code:: console

    pip install git+https://github.com/TheMuonNeutrino/magSonify


Usage example
--------------------

.. code:: python

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


License
----------------
The MIT License. See LICENSE.txt for details.
