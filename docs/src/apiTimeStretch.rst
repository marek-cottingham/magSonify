API reference - Sonification Methods
===========================================

Wavelets based
-----------------

.. list-table:: Correpondence between variable names and equation terms in CT98
    
    * - where:
      - is nammed:
    * - :math:`x_n`
      - x
    * - :math:`N`
      - maxNumberSamples
    * - :math:`\delta t`
      - sampleSpacingTime
    * - :math:`s_j`
      - scales
    * - :math:`\delta j`
      - scaleSpacingLog
    * - :math:`\Psi_0(\eta)`
      - waveletFunction
    * - :math:`\Psi_0(0)`
      - waveletTimeFactor
    * - :math:`C_{\delta}`
      - waveletRescaleFactor
    * - :math:`W_n(s_j)`
      - coefficients

.. autofunction:: magSonify.sonificationMethods.wavelets.transform.generateCwtScales

    Based on CT98: https://psl.noaa.gov/people/gilbert.p.compo/Torrence_compo1998.pdf

    .. math::

        s_j = s_0\,  2^{j \delta j}, \ \ j = 0, 1, ... J

        J = \delta j^{-1} log_2(N \delta t / s_0)

.. autofunction:: magSonify.sonificationMethods.wavelets.transform.cwt

    Based on CT98: https://psl.noaa.gov/people/gilbert.p.compo/Torrence_compo1998.pdf

    .. math::

      W(s) = \frac{\sqrt{\delta t}}{s} \, \, \text{fftconvolve}( \, x, \, \Psi_0 \, )

.. autofunction:: magSonify.sonificationMethods.wavelets.transform.icwt

    Based on CT98: https://psl.noaa.gov/people/gilbert.p.compo/Torrence_compo1998.pdf

    .. math::

      x_n = \frac{\delta j \sqrt{\delta t}}{C_{\delta} \, \Psi_0(0)} 
      \sum\limits_{j=0}^J \mathbb{R} \! \left\{  W_n(s_j)  \right\}

.. autofunction:: magSonify.sonificationMethods.wavelets.transform.icwt_noAdmissibilityCondition

    Based on the method presented in:

      Computational implementation of the inverse continuous wavelet transform without a 
      requirement of the admissibility condition. Eugene B. Postnikov, Elena A. Lebedeva, 
      Anastasia I. Lavrova. 2015. https://arxiv.org/abs/1507.04971

.. autofunction:: magSonify.sonificationMethods.wavelets.transform.interpolateCoeffs

.. autofunction:: magSonify.sonificationMethods.wavelets.transform.interpolateCoeffsPolar

.. autoclass:: magSonify.sonificationMethods.wavelets.Morlet
  :members:

Paulstretch
--------------

.. autofunction:: magSonify.sonificationMethods.paulstretch_mono.paulstretch