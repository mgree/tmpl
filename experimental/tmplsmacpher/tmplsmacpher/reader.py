import json
import logging
import os

from datetime import datetime

from utils import getLoggingFormatter
from utils import makeDir
from utils import LOG_DIR


class JsonFileReader(object):
    """A utility class for reading json objects from files.
    """
    # Make log directory if it doesn't exist.
    makeDir(LOG_DIR)

    # Instantiate a couple of file loggers to keep track of different things.
    # For logging json objects with missing fields.
    MISSING_FIELDS_LOGGER_NAME = 'JsonFileReader_missingFields'
    MISSING_FIELDS_LOGFILE_NAME = ('JsonFileReader_missingFields_{datetime}'.format(
            datetime=datetime.now().isoformat()
        )
    )

    # For logging when we find duplicate json objects.
    DUP_DOCS_LOGGER_NAME = 'JsonFileReader_dupDocuments'
    DUP_DOCS_LOGFILE_NAME = ('JsonFileReader_dupDocuments_{datetime}'.format(
            datetime=datetime.now().isoformat()
        )
    )

    # For logging missing files (eg. 1-fulltext.txt doesn't have 1.txt meta
    # file to go along with it).
    MISSING_FILE_LOGGER_NAME = 'JsonFileReader_missingFiles'
    MISSING_FILE_LOGFILE_NAME = ('JsonFileReader_missingFiles_{datetime}'.format(
            datetime=datetime.now().isoformat()
        )
    )

    missingFieldsLogger = logging.getLogger(MISSING_FIELDS_LOGGER_NAME)
    fh0 = logging.FileHandler(
        os.path.join(LOG_DIR, MISSING_FIELDS_LOGFILE_NAME)
    )
    fh0.setFormatter(getLoggingFormatter())
    missingFieldsLogger.addHandler(fh0)
    missingFieldsLogger.setLevel(logging.DEBUG)

    dupDocsLogger = logging.getLogger(DUP_DOCS_LOGGER_NAME)
    fh1 = logging.FileHandler(os.path.join(LOG_DIR, DUP_DOCS_LOGFILE_NAME))
    fh1.setFormatter(getLoggingFormatter())
    dupDocsLogger.addHandler(fh1)
    dupDocsLogger.setLevel(logging.DEBUG)

    missingFileLogger = logging.getLogger(MISSING_FILE_LOGGER_NAME)
    fh2 = logging.FileHandler(os.path.join(LOG_DIR, MISSING_FILE_LOGGER_NAME))
    fh2.setFormatter(getLoggingFormatter())
    missingFileLogger.addHandler(fh2)
    missingFileLogger.setLevel(logging.DEBUG)

    @staticmethod
    def loadFile(filepath):
        """Loads the json object from a single file.

        Args:
            filepath: full path of the file to load.

        Returns:
            A string representing the contents of the file.
        """
        with open(filepath, 'r') as f:
            return f.read()

    @staticmethod
    def loadJsonFile(filepath):
        """Loads the json object from a single file.

        Args:
            filepath: full path of the file to load.

        Returns:
            A json object representing the contents of the file.
        """
        with open(filepath, 'r') as f:
            return json.load(f)

    @staticmethod
    def loadAllJsonFiles(dirPath, recursive=True):
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
                    (JsonFileReader.loadJsonFile(childPath),  # Document json obj.
                    os.path.basename(os.path.dirname(childPath)),  # Conference.
                    childPath,  # Filepath.
                    )
                )
            elif recursive:
                objs += JsonFileReader.loadAllJsonFiles(childPath, recursive)
        return objs

    @staticmethod
    def loadAllAbstracts(dirPath):
        """Loads all abstracts and their respective metadata from a directory.

        Args:
            dirPath: full path of directory to load abstracts from.

        Returns:
            A zipped list of abstracts and their respective metadata.
        """
        objs = JsonFileReader.loadAllJsonFiles(dirPath, recursive=True)
        abstracts = []
        metas = []
        seen = dict()
        for obj in objs:
            (doc, conference, filepath) = obj
            abstract = doc.get('abs')

            if abstract is None:  # Document didn't have an 'abs' field.
                JsonFileReader.missingFieldsLogger.info(
                    '{conference}: {doc} does not have an "abs" field.'
                    .format(conference=conference, doc=doc)
                )
                abstract = ''

            # Fetch metadata.
            meta = JsonFileReader.buildMeta(doc, conference)
            title = meta['title']
            if title in seen:  # Already have seen this title before.
                JsonFileReader.dupDocsLogger.info(
                    "'{title}' from {conference} at {dupFilepath} already seen at {seenFilepath}".format(
                        title=title,
                        conference=conference,
                        dupFilepath=filepath,
                        seenFilepath=seen[title],
                    )
                )
            # Haven't seen this title before, but add it to seen 
            # with its filepath to keep track of it.
            else:
                seen[title] = filepath

            abstracts.append(abstract)
            metas.append(meta)

        return abstracts, metas

    @staticmethod
    def loadAllFullTexts(dirPath):
        """Loads all of the fulltext files and returns list of 
        (fullTexts, metas).

        Args:
            dirPath: full path of the directory to load files from.

        Returns:
            A tuple of (fullTexts, metas) where 
            metas[i] corresponds to fullTexts of [i].
        """
        return JsonFileReader._loadAllFullTexts(dirPath, 
                                                recursive=True, 
                                                fullTexts=None, 
                                                metas=None, 
                                                seen=None)

    @staticmethod
    def _loadAllFullTexts(dirPath, recursive=True, fullTexts=None, metas=None, seen=None):
        """Recursive helper method for loadAllFullTexts.
        Loads all of the fulltext files and returns list of 
        (fullTexts, metas).

        Args:
            dirPath: full path of the directory to load files from.
            recursive: If True, will recurse down file tree.
                Otherwise, only loads files from next level down.

            Note: fullTexts, metas, and seen are aggregators to be used
                internally; do not change their default values.
        
        Returns:
            A tuple of (fullTexts, metas) where 
            metas[i] corresponds to fullTexts of [i].
        """
        # Initialize fullTexts and metas on first call.
        if fullTexts is None:
            fullTexts = []
        if metas is None:
            metas = []
        if seen is None:
            seen = set()

        for child in os.listdir(dirPath):
            childPath = os.path.join(dirPath, child)

            # Found file.
            if not os.path.isdir(childPath):

                # Only care about fulltext files; we'll find their
                # corresponding meta files ourselves.
                if 'fulltext' in child:
                    # Get conference for current paper.
                    conference = os.path.basename(os.path.dirname(childPath))

                    # Metafile path for current fulltext.
                    metaFilepath = os.path.join(
                        dirPath, child.replace('-fulltext', '')
                    )

                    # If we are missing a meta file to go along with the 
                    # full-text file, 1) log it, and 2) skip to the next 
                    # iteration so we avoid off-by-one errors by adding a 
                    # fulltext without its respective meta.
                    if not os.path.exists(metaFilepath):
                        JsonFileReader.missingFileLogger.info(
                            'Missing {file}'.format(metaFilepath)
                        )
                        continue

                    metaJsonObj = JsonFileReader.loadJsonFile(metaFilepath)

                    fullText = JsonFileReader.loadFile(childPath)
                    meta = JsonFileReader.buildMeta(metaJsonObj, conference)

                    title = meta['title']
                    if title in seen: # Already have seen this title before.
                        JsonFileReader.dupDocsLogger.info(
                            "'{title}' from {conference} at {dupFilepath} already seen at {seenFilepath}".format(
                                title=title,
                                conference=conference,
                                dupFilepath=childPath,
                                seenFilepath=seen[title],
                            )
                        )
                    # Haven't seen this title before, but add it to seen 
                    # with its filepath to keep track of it.
                    else:
                        seen[title] = childPath

                    fullTexts.append(fullText)
                    metas.append(meta)

            elif recursive:
                JsonFileReader._loadAllFullTexts(childPath, 
                                                 recursive, 
                                                 fullTexts, 
                                                 metas)
        return fullTexts, metas

    @staticmethod
    def buildMeta(doc, conference, fields={'title', 'authors'}):
        """Builds a dictionary representing the meta data from a json doc.

        Args:
            doc: json object to build meta from.
            conference: conference data to add to meta dictionary (with the
                current setup, this is parsed from the directory that the 
                doc lives in).
            fields: fields in the json doc that we want to extract and add
                to our meta dictionary.

        Returns:
            A dictionary representing the meta data from doc.
        """
        meta = dict()

        # Add conference.
        meta['conf'] = conference

        # Add the rest of the fields.
        for field in fields:
            value = doc.get(field)
            meta[field] = value
        return meta


if __name__ == '__main__':
    pathToAbstracts = '/Users/smacpher/clones/tmpl_venv/tmpl-data/abs/top4/'
    pathToFulltexts = '/Users/smacpher/clones/tmpl_venv/tmpl-data/full/fulltext'
    documents = JsonFileReader.loadAllFullTexts(pathToFulltexts)
    print(documents)
