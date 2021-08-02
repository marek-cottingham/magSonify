Dev: Multiprocessing
======================

.. warning::
    DEVELOPMENT TESTING
    MAY BE INCOMPLETE / NON FUNCTIONAL

Methods for accelerating program execution by using multiprocessing. Currently in development.
Exectution example in ``./Example Code/DEV Inter-process communication/devBufferingTest.py``.

Requires extra dependancies be installed:

.. code:: console

    pip install -e git+https://github.com/TheMuonNeutrino/magSonify#egg=magSonify[bufferingTest]

BaseProcess
--------------

.. autoclass:: magSonify.Buffering.BaseProcess
    :members:
    :show-inheritance:

.. autoclass:: magSonify.Buffering.STOPVALUE