Artifact testing
====================
A series of tests have been performed on the sonification algorithms in order to explore
the artifacts present. These are outlined in IPython notebooks, which core testing code contained
in ``./Tests_Artifacts/baseMethods.py``

.. note::

    Audio examples are used in the notebooks, in order to listen to these you will need to reload
    and run all cells first, as jupiter doesn't save the audio in the notebook file.

Each algorithm was tested first on sine waves and harmonics. Subsequent testing was performed on
frequency sweeps, frequency sweeps combined with harmonics and frequency sweeps combined with
gaussian white noise. Sonifying the results of these test was found to be particularly helpful in 
quickly identify the type and severity of distortions.

Overall, testing indicated the complete insuitability of WSOLA for situations involving frequency
sweeps, particularly when noise was introduced.

The other three algorithm performed better. Below is a comparison of the 
audio for wavelets, phase vocoder and paulstretch for a x16 stretching of a frequency sweep with
gaussian white noise added. (``NOISE_MAGNITUDE = 2``, ie. the noise was scaled to have a standard 
deviation twice the magnitude of the frequency sweep)

    .. raw:: html

        <p class="audio_title">Expected audio (prediction):</p>
        <audio controls="controls">
        <source src="../_static/Audio_Tests_Artifacts/expectedFreqSweepNoise.wav" type="audio/wav">
        Your browser does not support the <code>audio</code> element. 
        </audio>

        <p class="audio_title">Actual audio - Wavelet stretch:</p>
        <audio controls="controls">
        <source src="../_static/Audio_Tests_Artifacts/waveletsFreqSweepNoise.wav" type="audio/wav">
        Your browser does not support the <code>audio</code> element. 
        </audio>

        <p class="audio_title">Actual audio - Phase vocoder stretch:</p>
        <audio controls="controls">
        <source src="../_static/Audio_Tests_Artifacts/phaseVocoderFreqSweepNoise.wav" type="audio/wav">
        Your browser does not support the <code>audio</code> element. 
        </audio>

        <p class="audio_title">Actual audio - Paulstretch:</p>
        <audio controls="controls">
        <source src="../_static/Audio_Tests_Artifacts/paulstretchFreqSweepNoise.wav" type="audio/wav">
        Your browser does not support the <code>audio</code> element. 
        </audio>

Install
------------
The artifact tests are located in ``./Tests_Artifacts``, not in the main package. Clone the github
repository in order to run them locally. You will need to have ``jupiter notebook`` installed.

Base Methods Module
------------------------
.. automodule:: baseMethods
    :members:
    :undoc-members: