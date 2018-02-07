import json
import logging
import os

from utils import getFileLogger


class JsonFileReader(object):
    """A utility class for reading json objects from files.
    """

    LOGGER_NAME = 'JsonFileReader'
    LOGFILE_NAME = '.JsonFileReaderLog'
    logger = getFileLogger(LOGGER_NAME, LOGFILE_NAME)

    def __init__(self):
        pass

    @staticmethod
    def loadFile(filepath):
        """Loads the json object from a single file.

        Args:
            path: full path of the file to load.

        Returns:
            A json object representing the contents of the file.
        """
        with open(filepath, 'r') as f:
            return json.load(f)

    @staticmethod
    def loadAllFiles(dirPath, recursive=False):
        """Loads all of the files from a directory. 

        Args:
            dirPath: full path of the directory to load files from.
            recursive: If True, will recurse down file tree. 
                Otherwise, only loads files from next level down.
        
        Returns:
            A list of json objects representing the contents of the files.
        """
        objs = [] # json objects found. One object for each file.
        for child in os.listdir(dirPath):
            childPath = os.path.join(dirPath, child)
            if not os.path.isdir(childPath):
                objs.append(JsonFileReader.loadFile(childPath))
            elif recursive: # only recursive if recursive flag is set to True.
                objs += JsonFileReader.loadAllFiles(childPath, recursive)
        return objs

    @staticmethod
    def loadAllAbstracts(dirPath, recursive=False):
        objs = JsonFileReader.loadAllFiles(dirPath, recursive)
        abstracts = []
        for obj in objs:
            # This will return 'None' if 'abs' field is not present.
            abstract = obj.get('abs')
            if abstract is not None:
                abstracts.append(abstract)
            else:
                JsonFileReader.logger.info(
                    '{obj} does not have an "abs" field.'.format(obj=obj)
                )
        return abstracts







