Sonification of space magnetic field data in Python.
----------------------------------------
### Installation ###

```sh
pip install git+https://github.com/TheMuonNeutrino/pyMagnetoSonify
```

### Quick start ###
Look at the example in processingExample.py

### Note on DataSet_3D ###
DataSet_3D is the class most commonly used to store satellite data
This is stored in 2 attributes: timeSeries and data
The x, y and z axes can be accessed by indexing DataSet_3D.data

```python
DataSet_3D.timeSeries # class for representing a series of times
DataSet_3d.data[0] # First axis
DataSet_3d.data[1]: # Second axis
DataSet_3d.data[2]: # Third axis
DataSet_3d.data["key"]: # Additional data
```

### Requirements ###

- Python 3.6+
- Numpy (developed with 1.21.0)
- Scipy (developed with 1.7.0)
- SoundFile
- ai.cdas (developed with 1.2.3)
- audiotsm (developed with 0.1.2)
