import json
import logging
import os

from datetime import datetime

from utils import getFileLogger
from utils import makeDir

from utils import LOG_DIR


class JsonFileReader(object):
    """A utility class for reading json objects from files.
    """
    # Make log directory if it doesn't exist.
    makeDir(LOG_DIR)

    MISSING_FIELDS_LOGFILE_NAME = 'JsonFileReader_missingFields'
    DUP_DOCS_LOGFILE_NAME = 'JsonFileReader_dupDocuments'

    missingFieldsLogger = getFileLogger(
        os.path.join(LOG_DIR, MISSING_FIELDS_LOGFILE_NAME)
    )

    dupDocsLogger = getFileLogger(
        os.path.join(LOG_DIR, DUP_DOCS_LOGFILE_NAME)
    )

    # logger = getFileLogger()
    # logger = logging.getLogger(LOGGER_NAME)
    # fh = logging.FileHandler(LOGFILE_NAME)
    # logger.addHandler(fh)

    # duplogger = logging.getLogger(DUPLOGGER_NAME)
    # dupFh = logging.FileHandler(DUPFILE_NAME)
    # duplogger.addHandler(dupFh)

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
                objs.append(
                    (JsonFileReader.loadFile(childPath), # Document json obj.
                    os.path.basename(os.path.dirname(childPath)), # Conference.
                    childPath, # Filepath.
                    )
                )

            # Only recursive if recursive flag is set to True.
            elif recursive:
                objs += JsonFileReader.loadAllFiles(childPath, recursive)
        return objs

    @staticmethod
    def loadAllAbstracts(dirPath, recursive=True):
        """Loads all abstracts and their respective metadata from a directory.

        Args:
            dirPath: full path of directory to load abstracts from.
            recursive: if True, will recurse down subdirectories to load 
                abstracts.

        Returns:
            A zipped list of abstracts and their respective metadata.
        """
        objs = JsonFileReader.loadAllFiles(dirPath, recursive)
        abstracts = []
        metas = []
        seen = dict()
        for obj in objs:
            (doc, conference, filepath) = obj
            abstract = doc.get('abs')

            if abstract is None: # Document didn't have an 'abs' field.
                JsonFileReader.missingFieldsLogger.info(
                    '{conference}: {doc} does not have an "abs" field.'
                    .format(conference=conference, doc=doc)
                )
                abstract = ''
            abstracts.append(abstract)

            # Fetch metadata.
            meta = JsonFileReader.buildMeta(doc, conference)
            title = meta['title']
            if title in seen: # Already have seen this title before.
                JsonFileReader.dupDocsLogger.info(
                    "'{title}' from {conference} at {dup_filepath} already seen at {seen_filepath}".format(
                    title=title, 
                    conference=conference, 
                    dup_filepath=filepath, 
                    seen_filepath=seen[title],
                    )
                )
            else: # Haven't seen this title before, but add it to seen with its filepath to keep track of it.
                seen[title] = filepath
            metas.append(meta)

        return (abstracts, metas)

    @staticmethod
    def loadAllFullTexts(dirPath, recursive=True):
        """Loads all full-texts and their respective metadata from a directory.

        Args:
            dirPath: full path of directory to load full-texts from.
            recursive: if True, will recurse down subdirectories to load 
                abstracts.

        Returns:
            A zipped list of full-texts and their respective metadata.
        """
        objs = JsonFileReader.loadAllFiles(dirPath, recursive)
        fullTexts = []
        metas = []
        for obj in objs:
            (doc, conference) = obj

            # This will return 'None' if 'full-text' field is not present.
            fullText = doc.get('abs')

            if fullText is not None:
                fullTexts.append(fullText)
            else:
                JsonFileReader.missingFieldsLogger.info(
                    '{doc} does not have a "full-text" field.'.format(doc=doc)
                )
                fullTexts.append(None)

            # Fetch metadata.
            metas.append(JsonFileReader.buildMeta(doc, conference))

        return (fullTexts, metas)

    @staticmethod
    def buildMeta(doc, conference, fields=['title', 'authors']):
        meta = dict()

        # Add conference.
        meta['conf'] = conference

        # Add rest of field.
        for field in fields:
            value = doc.get(field)
            meta[field] = value
        return meta


if __name__ == '__main__':
    pathToAbstracts = '/Users/smacpher/clones/tmpl_venv/tmpl-data/abs/top4/'
    pathToFulltexts = '/Users/smacpher/clones/tmpl_venv/tmpl-data/full/fulltext'
    documents = JsonFileReader.loadAllAbstracts(pathToAbstracts, recursive=True)
    print(documents[-1])

