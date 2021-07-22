import os, shutil
from .initialise import memory_cache_path,cdas_cache_path

def _get_directory_size(directory):
    """Returns the `directory` size in bytes and number of files"""
    totalSize = 0
    try:
        # print("[+] Getting the size of", directory)
        for entry in os.scandir(directory):
            if entry.is_file():
                # if it's a file, use stat() function
                totalSize += entry.stat().st_size
            elif entry.is_dir():
                # if it's a directory, recursively call this function
                totalSize += _get_directory_size(entry.path)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if for whatever reason we can't open the folder, return 0
        return 0
    return totalSize

def cacheDetails():
    """Prints cache details to console"""
    cdasSize = _get_directory_size(cdas_cache_path/1024**2)
    memorySize = _get_directory_size(memory_cache_path/1024**2)
    print(f"CDAS cache size: {cdasSize}")
    print(f"Memory cache size: {memorySize}")

def deleteCache():
    """Deletes the cache"""
    shutil.rmtree(cdas_cache_path)
    shutil.rmtree(memory_cache_path)
    print("The cache has been deleted")
