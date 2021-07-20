Usage notes
===============

Note on DataSet_3D
---------------------
:class:`magSonify.DataSet_3D` is the class most commonly used to store satellite data.
This is stored in 2 attributes: :attr:`magSonify.DataSet.timeSeries` and 
:attr:`magSonify.DataSet.data`.
The x, y and z axes can be accessed by indexing ``DataSet_3D.data``.

::

    DataSet_3D.timeSeries # class for representing a series of times
    DataSet_3D.data[0] # First axis
    DataSet_3D.data[1]: # Second axis
    DataSet_3D.data[2]: # Third axis
    DataSet_3D.data["key"]: # Additional data