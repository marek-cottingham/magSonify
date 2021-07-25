import os

def ensureFolder(directory):
    """Checks that a directory is present, creating if it is not.
    Cannot handle cases where the parent directory doesn't exist either.
    """
    if not os.path.exists(directory):
        os.mkdir(directory) 