MagSonify
================
.. image:: https://readthedocs.org/projects/magsonify/badge/?version=latest
   :target: https://magsonify.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

MagSonify enables the sonification of space magnetic field data in python.

It allows for downloading of satellite data from CDA web, processing of this data and generation of
audio. It includes time stretching methods in order to aid sonification of data at low sample rates.

Currently the project provides ready built support for THEMIS satellites only. Users can specify
imports from other satellites by defining their own subclasses.

Example of sonification of magnetic field data:

<iframe width="380" height="216" src="https://www.youtube.com/embed/wmAwFIXWMvY" title="YouTube video player" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

- Docs: https://magsonify.readthedocs.io/en/latest/src/introduction.html
- Issue Tracker: https://github.com/marek-cottingham/magSonify/issues
- Source Code: https://github.com/marek-cottingham/magSonify/


Features
------------------
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
--------------------

.. code:: console

    pip install git+https://github.com/marek-cottingham/magSonify/


Usage example
--------------------

.. code:: python

   import magSonify
   from datetime import datetime

   start = datetime(2008,12,7)
   end = datetime(2008,12,10)
   myTHEMISdata = magSonify.THEMISdata()
   myTHEMISdata.importCDAS(
      start,end,satellite='D'
   )
   myTHEMISdata.defaultProcessing(removeMagnetosheath=True,minRadius=4)

   pol = myTHEMISdata.magneticFieldMeanFieldCorrdinates.extractKey(1)
   pol.phaseVocoderStretch(16)
   pol.normalise()
   pol.genMonoAudio("Example of pol x16 with phase vocoder.wav")


License
----------------
Copyright (c) 2021 Marek Cottingham (mc3219@ic.ac.uk)
The MIT License. See LICENSE.txt for details.

Includes modified versions or sections of 
`paulstretch_python <https://github.com/paulnasca/paulstretch_python>`_,
`aaren/wavelets <https://github.com/aaren/wavelets>`_ and `audiotsm <https://github.com/Muges/audiotsm>`_
