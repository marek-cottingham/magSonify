import os

local_app_path = os.path.join(
    os.getenv("LOCALAPPDATA"),
    "pyMagnetoSonify"
)

cdas_cache_path = os.path.join(
    local_app_path,
    "CDAScache"
)

memory_cache_path = os.path.join(
    local_app_path,
    "memoryCache"
)

def ensurePath(directory):
    """Checks that a directory is present, creating if it is not
    """
    if not os.path.exists(directory):
        os.mkdir(directory)