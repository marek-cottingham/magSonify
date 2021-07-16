# WARNING: Delete cache before package uninstall by calling cacheControl.deleteCache()
CACHING_ENABLED = True

from ai import cdas

if CACHING_ENABLED:
    from .initialise import ensurePath,local_app_path,cdas_cache_path,memory_cache_path
    ensurePath(local_app_path)
    ensurePath(cdas_cache_path)
    ensurePath(memory_cache_path)
    cdas.set_cache("True",cdas_cache_path)

from .MagnetometerData import MagnetometerData, THEMISdata
from .SimulateData import SimulateData
from .TimeSeries import TimeSeries, generateTimeSeries
from .DataSet import DataSet, DataSet_3D, DataSet_Placeholder, DataSet_3D_Placeholder
from .DataSet_1D import DataSet_1D, DataSet_1D_placeholder



