import logging
import os


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

