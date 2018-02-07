import json
import os


class JsonFileReader(object):
    """A utility class for reading json objects from files.
    """

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
        found = []
        for child in os.listdir(dirPath):
            childPath = os.path.join(dirPath, child)
            if not os.path.isdir(childPath):
                found.append(JsonFileReader.loadFile(childPath))
            elif recursive: # only recursive if recursive flag is set to True.
                found += JsonFileReader.loadAllFiles(childPath, recursive)
        return found

    