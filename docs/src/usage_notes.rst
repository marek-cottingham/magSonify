Usage notes
===============

Note on DataSet_3D
---------------------
:class:`magSonify.DataSet_3D` is the class most commonly used to store satellite data.
This is stored in 2 attributes: :attr:`magSonify.DataSet.timeSeries` and 
:attr:`magSonify.DataSet.data`.
The x, y and z axes can be accessed by indexing ``DataSet_3D.data``.

::

    myDataSet_3D.timeSeries  # class for representing a series of times
    myDataSet_3D.data[0]     # First axis
    myDataSet_3D.data[1]     # Second axis
    myDataSet_3D.data[2]     # Third axis
    myDataSet_3D.data["key"] # Additional data

    myDataSet_1D = myDataSet_3D.extractKey(0) # First axis extracted into a seperate data set

Notes on devCaching module
----------------------------
MagSonify includes a basic form of caching through the caching functionality of ``ai.cdas``.
As there is no functionality to limit the size of this cache or automatically delete it, it
is only suitable for development purposes. 

The cache is disabled by default. To enable it, create
the file ``magSonify/devCaching/config.py`` containing the line::

    CACHING_ENABLED = True

.. warning::

    The cache size is unlimited and there is no automatic deletion of the cache. Ensure cache
    deletion before uninstalling the package.

.. note::

    The default cache path is ``%localappdata%/magSonify``. This is only available on windows
    systems. To change the cache path, modify ``magSonify/devCaching/initialise.py``.

The following cache management methods are available:

.. autofunction:: magSonify.devCaching.cacheControl.cacheDetails

.. autofunction:: magSonify.devCaching.cacheControl.deleteCache

    ::

        >>> from magSonify.devCaching.cacheControl import deleteCache
        >>> deleteCache()
        The cache has been deleted