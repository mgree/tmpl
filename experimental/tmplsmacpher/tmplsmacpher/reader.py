import json
import logging
import os

from datetime import datetime

from settings import LOG_DIR
from utils import getLoggingFormatter
from utils import makeDir


class JsonFileReader(object):
    """A utility class for reading json objects from files.
    """
    logging.basicConfig(level=logging.INFO)
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

    def __init__(self, dirPath, db=None):
        self.dirPath = dirPath
        self.db = db

    def setDB(self, db):
        if self.db is None:
            self.db = db
        else:
            raise AttributeError("DB already set.")

    def readAll(self):
        """Loads all fulltexts and their respective metadata from a directory. If writeToDB is set to True,
        will also write papers and conference metadata to sqlite3 db for this run.

        Args:
            dirPath: full path of directory to load abstracts from.
            writeToDB: whether to write loaded data to db.

        Returns:
            A tuple of fulltexts and their respective metadata.
        """
        objs = JsonFileReader.loadAllJsonFiles(self.dirPath, recursive=True)
        fulltexts = []
        metas = []

        # keep track of the people that we've seen so that we don't try to add them twice in the 'person' table.
        personIDSeen = set()
        seen = dict()

        for obj in objs:
            (doc, conference, filepath) = obj

            # Check for 'metadata.txt' file and insert it into database.
            if 'series_id' in doc and self.db is not None:
                # Ensure you're fetching the same fields in init.sql.
                conferenceData = {
                    'proc_id': int(doc.get('proc_id')),
                    'series_id': doc.get('series_id'),
                    'acronym': doc.get('acronym'),
                    'isbn13': doc.get('isbn13'),
                    'year': doc.get('year'),
                    'proc_title': doc.get('proc_title'),
                    'series_title': doc.get('series_title'),
                    'series_vol': doc.get('series_vol'),
                }
                self.db.insert(tableName='conference', **conferenceData)
                logging.info('DB: Wrote {conference} to {db}'.format(conference=conferenceData['series_title'],
                                                                     db=self.db))
                continue

            abstract = doc.get('abstract')
            fulltext = doc.get('fulltext')

            # Remove fulltext and use doc as metadata for current paper.
            doc.pop('fulltext', None)
            meta = doc
            title = meta['title']

            # Add person and author to database.
            for author in meta['authors']:
                # Need to cast certain fields to match sqlite datatypes.
                author['author_profile_id'] = int(author['author_profile_id']) if author['author_profile_id'] != '' and\
                    author['author_profile_id'] is not None else ''
                author['orcid_id'] = int(author['orcid_id']) if author['orcid_id'] != '' and \
                    author['orcid_id'] is not None else ''

                # There are sometimes author entries for some reason. Ignore them.
                if author['person_id'] is None:
                    continue

                self.db.insert(tableName='author', **{'person_id': author['person_id'],
                                      'article_id': int(meta['article_id'])})

                if author['person_id'] not in personIDSeen:
                    personIDSeen.add(author['person_id'])
                    self.db.insert(tableName='person', **author)

            if abstract is None:
                JsonFileReader.missingFieldsLogger.debug(
                    '{conference}: {title} does not have an "abs" field.'
                    .format(conference=conference, title=title)
                )
                abstract = ''

            if fulltext is None:
                JsonFileReader.missingFieldsLogger.debug(
                    '{conference}: {title} does not have an "fulltext" field.'
                    .format(conference=conference, title=title)
                )
                fulltext = ''

            # Output title so user can see progress.
            logging.info('Found \'{title}\' in {conference}.'.format(title=title.encode('utf-8'),
                                                                     conference=conference.encode('utf-8')))

            # Already have seen this title before.
            if title in seen:
                JsonFileReader.dupDocsLogger.debug(
                    "'{title}' from {conference} at {dupFilepath} already seen at {seenFilepath}".format(
                        title=title,
                        conference=conference,
                        dupFilepath=filepath,
                        seenFilepath=seen[title],
                    )
                )
            else:
                # Haven't seen this title before, but add it to seen
                # with its filepath to keep track of it.
                seen[title] = filepath

            fulltexts.append(fulltext)
            metas.append(meta)

            # Finally, insert paper into db.
            if self.db is not None:
                paperData = {
                    'article_id': int(doc.get('article_id')),
                    'title': doc.get('title'),
                    'abstract': doc.get('abstract'),
                    'proc_id': int(doc.get('proc_id')),
                    'article_publication_date': doc.get('article_publication_date'),
                    'url': doc.get('url'),
                    'doi_number': doc.get('doi_number'),
                }
                self.db.insert('paper', **paperData)
                logging.info('DB: Wrote {paper} to {db}'.format(paper=paperData['title'], db=self.db))

        # Make sure that we processed the same number of fulltexts and metadatas.
        if len(fulltexts) != len(metas):
            raise ValueError(
                'Found unequal numbers of fulltexts and metas: {numFulltexts} fulltexts, {numMetas} metas'.format(
                    numFulltexts=len(fulltexts),
                    numMetas=len(metas),
                )
            )

        self.db.connection.commit()
        return fulltexts, metas

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
        objs = []  # List of json objects found in the specified directory.
        for child in os.listdir(dirPath):
            childPath = os.path.join(dirPath, child)
            if not os.path.isdir(childPath):
                objs.append(
                    (JsonFileReader.loadJsonFile(childPath),  # Document json obj.
                     os.path.basename(os.path.dirname(childPath)),  # Conference.
                     childPath)  # File path.
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

            # Fetch metadata.
            meta = JsonFileReader.buildMeta(doc, conference)
            title = meta['title']

            if abstract is None:  # Document didn't have an 'abs' field.
                JsonFileReader.missingFieldsLogger.debug(
                    "{conference}: '{title}' does not have an 'abs' field."
                    .format(conference=conference, title=title)
                )
                abstract = ''

            # Output title so user can see progress.
            logging.info('Found \'{title}\' in {conference}.'.format(title=title.encode('utf-8'),
                                                                     conference=conference.encode('utf-8')))

            # Already have seen this title before.
            if title in seen:
                JsonFileReader.dupDocsLogger.debug(
                    "{conference}: '{title}' at {dupFilepath} already seen at {seenFilepath}".format(
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
        
        if len(abstracts) != len(metas):
            raise ValueError(
                'Found unequal numbers of abstracts and metas: {numAbs} abstracts, {numMetas} metas'.format(
                    numAbs=len(abstracts),
                    numMetas=len(metas),
                )
            )
        return abstracts, metas

    @staticmethod
    def loadAllFullTextsLegacy(dirPath):
        """Loads all of the fulltext files and returns list of 
        (fullTexts, metas).

        Note: this is used with the legacy tmpl-data format of storing the corpus
            in which the fulltexts and metadata of each paper is stored in the form
            0.txt 0-fulltext.txt.

        Args:
            dirPath: full path of the directory to load files from.

        Returns:
            A tuple of (fullTexts, metas) where 
            metas[i] corresponds to fullTexts of [i].
        """
        return JsonFileReader._loadAllFullTextsLegacy(dirPath,
                                                      recursive=True, 
                                                      fullTexts=None, 
                                                      metas=None, 
                                                      seen=None)

    @staticmethod
    def _loadAllFullTextsLegacy(dirPath, recursive=True, fullTexts=None, metas=None, seen=None):
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
            seen = dict()

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
                        JsonFileReader.missingFileLogger.debug(
                            'Missing {file}'.format(file=metaFilepath)
                        )
                        continue

                    metaJsonObj = JsonFileReader.loadJsonFile(metaFilepath)

                    fullText = JsonFileReader.loadFile(childPath)
                    meta = JsonFileReader.buildMeta(metaJsonObj, conference)

                    title = meta['title']

                    # Output title so user can see progress.
                    logging.info('Found \'{title}\' in {conference}.'.format(title=title.encode('utf-8'),
                                                                             conference=conference.encode('utf-8')))

                    # Already have seen this title before.
                    if title in seen:
                        JsonFileReader.dupDocsLogger.debug(
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
                JsonFileReader._loadAllFullTextsLegacy(childPath,
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
    from db import TmplDB
    pathToFulltexts = '/Users/smacpher/clones/tmpl_venv/acm-data/parsed'
    db = TmplDB('testReader.db')
    reader = JsonFileReader(pathToFulltexts, db)
    documents = reader.readAll()
