import cPickle
import errno
import functools
import logging
import os

from datetime import datetime


LOG_DIR = 'logs'


def getLoggingFormatter():
    return logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def makeDir(path):
    """Checks if directory exists. If it doesn't, creates it.
    """
    # Check that directory doesn't already exist 
    try:
        os.makedirs(path)
    # Could be a permissions, or disk capacity error.
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


class DiskCache(object):
    """Decorator that caches the result of the last run of the function, fn,
    on disk.
    """

    DEFAULT_CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
    DEFAULT_FORCE_RERUN = False

    def __init__(self,
                 forceRerun=DEFAULT_FORCE_RERUN, 
                 cacheDir=DEFAULT_CACHE_DIR):
        self.forceRerun = forceRerun
        self.cacheDir = cacheDir

    def __call__(self, fn, *args, **kwargs):
        # Make cache directory if doesn't already exist.
        makeDir(self.cacheDir)
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
    def _buildCacheFilename(fn):
        """Builds a filename to represent function call and date.
        """
        return fn.__name__


