import logging
import os
import pickle


def getLoggingFormatter():
    """
    Returns a formatter to apply to loggers througout package.
    """
    return logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def makeDir(path):
    """Checks if directory exists. If it doesn't, creates it.

    Args:
        path: desired path of directory to create
    """
    try:
        os.mkdir(path)
    except OSError:
        if not os.path.isdir(path):
            raise


def stringToFile(string, path):
    """Writes a string to a text file at the given path.
    
    Args:
        string: string to write to file
        path: path of file to write string to
    """
    with open(path, 'w') as f:
        f.write(string.encode('utf8'))


def saveObject(obj, path):
    """Saves object to disk.

    Args
        obj: obj to pickle and save to disk.
        path: path to save obj to.
    """
    with open(path, 'wb') as f:  # Overwrites any existing file.
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def loadObject(path):
    """Loads object from disk.

    Args:
        path: path of obj to load.
    """
    with open(path, 'rb') as f:
        return pickle.load(f)

