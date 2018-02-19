import functools
import logging


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


def diskCache(fn):
    """Decorator that caches the result of the last run of the function, fn,
    on disk.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if (args, kwargs)

