# WARNING: Delete cache before package uninstall by calling cacheControl.deleteCache()

from ai import cdas
from .Utilities import ensureFolder

try:
    from .devCaching.config import CACHING_ENABLED
except ImportError:
    CACHING_ENABLED = False

def enableCaching():
    from .devCaching.initialise import local_app_path,cdas_cache_path
    if local_app_path is not None:
        ensureFolder(local_app_path)
        ensureFolder(cdas_cache_path)
        cdas.set_cache("True",cdas_cache_path)

if CACHING_ENABLED:
    enableCaching()

from .MagnetometerData import MagnetometerData, THEMISdata
from .SimulateData import SimulateData
from .TimeSeries import TimeSeries, generateTimeSeries
from .DataSet import DataSet, DataSet_3D
from .DataSet_1D import DataSet_1D



