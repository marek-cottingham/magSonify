import os

localappdata = os.getenv("LOCALAPPDATA")

if localappdata is not None:
    local_app_path = os.path.join(
        localappdata,
        "magSonify"
    )
    cdas_cache_path = os.path.join(
        local_app_path,
        "CDAScache"
    )
else:
    print("Failed to get cache path, do not use cache operations")
    local_app_path = None
    cdas_cache_path = None