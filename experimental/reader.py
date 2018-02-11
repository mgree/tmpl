import json
import logging
import os

from utils import getFileLogger





# class AbstractCorpus(object):
#     """A streaming corpus of abstracts.
#     """
#     def __iter__(self):


class JsonFileReader(object):
    """A utility class for reading json objects from files.
    """

    LOGGER_NAME = 'JsonFileReader'
    LOGFILE_NAME = '.JsonFileReaderLog'
    # logger = getFileLogger(LOGGER_NAME, LOGFILE_NAME)
    logger = logging.getLogger(LOGGER_NAME)
    fh = logging.FileHandler(LOGFILE_NAME)
    logger.addHandler(fh)

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
        objs = [] # List of json objects found in the specified directory.
        for child in os.listdir(dirPath):
            childPath = os.path.join(dirPath, child)
            if not os.path.isdir(childPath):
                objs.append((JsonFileReader.loadFile(childPath), os.path.basename(os.path.dirname(childPath))))
            # Only recursive if recursive flag is set to True.
            elif recursive:
                objs += JsonFileReader.loadAllFiles(childPath, recursive)
        return objs

    @staticmethod
    def loadAllAbstracts(dirPath, recursive=False):
        objs = JsonFileReader.loadAllFiles(dirPath, recursive)
        abstracts = []
        metas = []
        for obj in objs:
            (doc, conf) = obj
            print(conf)
            # This will return 'None' if 'abs' field is not present.
            abstract = doc.get('abs')

            if abstract is not None:
                abstracts.append(abstract)
            else:
                JsonFileReader.logger.info(
                    '{doc} does not have an "abs" field.'.format(doc=doc)
                )
                abstracts.append(None)

            # Fetch metadata.
            curMeta = dict()
            curMeta['conf'] = conf
            for field in ['title', 'authors']:
                value = doc.get(field)
                if value is not None:
                    curMeta[field] = value
                else:
                    curMeta[field] = None

            metas.append(curMeta)

        return zip(abstracts, metas)


if __name__ == '__main__':
    path_to_abstracts = '/Users/smacpher/clones/tmpl_venv/tmpl-data/abs/top4/'
    reader = JsonFileReader()
    documents = reader.loadAllAbstracts(path_to_abstracts, recursive=True)
    print(documents[0])



