Sonification of space magnetic field data in Python.
----------------------------------------
### Installation ###

```sh
pip install git+https://github.com/TheMuonNeutrino/magSonify
```

### Quick start ###
Look at the example in `processingExample.py`

### Note on DataSet_3D ###
DataSet_3D is the class most commonly used to store satellite data
This is stored in 2 attributes: timeSeries and data
The x, y and z axes can be accessed by indexing DataSet_3D.data

```python
DataSet_3D.timeSeries # class for representing a series of times
DataSet_3D.data[0] # First axis
DataSet_3D.data[1]: # Second axis
DataSet_3D.data[2]: # Third axis
DataSet_3D.data["key"]: # Additional data
```
