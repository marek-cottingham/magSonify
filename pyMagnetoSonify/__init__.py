import os
from ai import cdas

from .initialise import ensurePath,local_app_path,cdas_cache_path,memory_cache_path

ensurePath(local_app_path)
ensurePath(cdas_cache_path)
ensurePath(memory_cache_path)
cdas.set_cache("True",cdas_cache_path)

from .MagnetometerData import MagnetometerData, THEMISdata, DataAxis
from .SimulateData import SimulateData

__all__ = ["MagnetometerData", "THEMISdata","SimulateData","DataAxis",]

