import cPickle
import errno
import functools
import logging
import os

from datetime import datetime

# Set universal format for log messages across entire package.
formatter = logging.Formatter(
    '%(asctime)s : %(name)s - %(levelname)s : %(message)s'
)


def getStdoutLogger(name, level=logging.INFO):
    """Returns a simple logger that logs to stdout.

    Args:
        name: string name of the logger.
        level: log level.

    Returns:
        A simple logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(level)
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    return logger


def getFileLogger(name, logfileName=None, level=logging.INFO):
    """Returns a logger with a file handler.

    Args:
        name: string name of the logger.
        logfileName: name of the logfile. Defaults the .<name>-log (param name).
        level: log level.

    Returns:
        A logger thatlogs to a file.
    """
    if logfileName is None:
        logfileName = '.{name}-log'.format(name=name)
    logger = logging.getLogger(name)
    fileHandler = logging.FileHandler(logfileName)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger


class DiskCache(object):
    """Decorator that caches the result of the last run of the function, fn,
    on disk.
    """

    DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(__file__), '.cache')
    DEFAULT_FORCE_RERUN = False

    def __init__(self,
                 forceRerun=DEFAULT_FORCE_RERUN, 
                 cacheDir=DEFAULT_CACHE_DIR):
        self.forceRerun = forceRerun
        self.cacheDir = cacheDir

    def __call__(self, fn, *args, **kwargs):
        # Make cache directory if doesn't already exist.
        DiskCache._checkCacheDir(self.cacheDir)
        cacheFilename = DiskCache._buildCacheFilename(fn)
        cacheFilepath = os.path.join(self.cacheDir, cacheFilename)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if (self.forceRerun or 
                not os.path.exists(cacheFilepath) or
                os.stat(cacheFilepath).st_size == 0):

                result = fn(*args, **kwargs)
                logging.warning(result)
                # Create new file or truncate existing file completely.
                with open(cacheFilepath, 'wb') as f:
                    cPickle.dump(result, f)
            else: # Retrieve cached results.
                with open(cacheFilepath, 'rb') as f:
                    result = cPickle.load(f)
            return result

        return wrapper

    @staticmethod
    def _checkCacheDir(path):
        """Ensures that cache directory exists. If it doesn't, creates it.
        """
        # Check that directory doesn't already exist 
        try:
            os.makedirs(path)
        # Could be a permissions, or disk capacity error.
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    @staticmethod
    def _buildCacheFilename(fn):
        """Builds a filename to represent function call and date.
        """
        return fn.__name__


