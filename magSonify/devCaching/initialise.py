import os

local_app_path = os.path.join(
    os.getenv("LOCALAPPDATA"),
    "magSonify"
)

if local_app_path is not None:
    cdas_cache_path = os.path.join(
        local_app_path,
        "CDAScache"
    )
else:
    print("Failed to get cache path, do not use cache operations")
    cdas_cache_path = None

def ensurePath(directory):
    """Checks that a directory is present, creating if it is not
    """
    if not os.path.exists(directory):
        os.mkdir(directory)