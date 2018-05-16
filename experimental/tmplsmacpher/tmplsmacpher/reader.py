import json
import logging
import os

from copy import deepcopy
from datetime import datetime
from tqdm import tqdm

from settings import LOG_DIR
from utils import getLoggingFormatter
from utils import makeDir


class Reader(object):
    """
    A class to read in and insert important corpus data into a TmplDB
    instance along the way.

    Usage:
        There are two ways to instantiate a Reader which then dictates
        how the reader will read in the DL.

            1) instantiate a Reader object by specifying the 'directory'
            keyword argument as a path to the pre-parsed corpus (parsed using
            the Parser's 'parseToDisk()' method):

                reader = Reader(directory='~/datasets/parsed')

            2) instantiate a Reader object by specifying the 'parser' keyword
            argument as a Parser object. You can do this :
                parser = Parser('~/datasets/acm-dl/proceedings')
                reader = Reader(parser=parser)

        Now once you've instantiated your Reader object, calling read()
        will return a generator that iterates over the corpus,
        pairing fulltext of every paper to their respective metas
        in the form (fulltext, meta):

            gen = reader.read()
            for (fulltext, meta) in gen:
                print(fulltext)
                print(meta)

        Note: either a directory OR a parser (not neither and not both) must
        be defined in a Reader or else the read() method will complain
        (because it has nothing to read...).

    Args:
        parser: Parser object to use to parse DL and thus read its output.
        directory: path to pre-parsed DL corpus to read from.
        db: TmplDB instance to use for this reader. As of now, the current
            implementation of TopicModel
            will set this for you so don't worry about passing it in.
            See 'main.py' for the flow of things.
        parentLogger: logger to use in the Parser instance.
            If None, a new Parser object will
            be instantiated for the Parser instance.
    """

    def __init__(self, parser=None, directory=None, db=None, parentLogger=None):
        if ((parser is None and directory is None) or 
                (parser is not None and directory is not None)):
            raise AttributeError('Please specify a parser OR directory.')

        self.parser = parser
        self.directory = directory
        self.db = db

        if parentLogger:
            self.logger = parentLogger.getChild('Reader')
        else:
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger('Reader')
            self.logger = logger

    def setDB(self, db):
        if self.db is None:
            self.db = db
        else:
            raise AttributeError("DB already set.")

    def read(self):
        if self.parser is not None:
            self.logger.info('Reading from parser.')
            for obj in self._readFromParser():
                yield obj
        elif self.directory is not None:
            self.logger.info('Reading from disk.')
            for obj in self._readFromDisk():
                yield obj
        else:
            raise AttributeError('Please specify a parser OR directory.')

    def _readFromParser(self):
        """Reads all paper json objects from a passed in parser."""
        if self.parser is None:
            raise AttributeError(
                'Parser is None. Perhaps you meant to call readFromDisk?'
            )

        curConference = None
        confSeen = set()
        for (conference, paper) in self.parser.parse():
            # First conference or found a new conference. 
            # Update TmplDB with conference data.
            if (curConference is None or 
                    conference.get('proc_id') not in confSeen):
                curConference = conference
                conferenceData = (
                    int(conference.get('proc_id')),
                    conference.get('series_id'),
                    conference.get('acronym'),
                    conference.get('isbn13'),
                    conference.get('year'),
                    conference.get('proc_title'),
                    conference.get('series_title'),
                    conference.get('series_vol'),
                )
                self.db.insertConferences(conferenceData)
                confSeen.add(conference.get('proc_id'))

            # Add person and author to database.
            for author in paper.get('authors'):
                # Need to cast certain fields to match sqlite datatypes.
                if (author['author_profile_id'] != '' and 
                        author['author_profile_id'] is not None):
                    author['author_profile_id'] = int(
                        author['author_profile_id']
                    )
                else:
                    author['author_profile_id'] = -1

                if (author['orcid_id'] != '' and
                        author['orcid_id'] is not None):
                    author['orcid_id'] = int(author['orcid_id'])

                if author['person_id'] is None:
                    continue

                authorData = (
                    author['person_id'],
                    int(paper.get('article_id')),
                )

                if self.db is not None:
                    self.db.insertAuthors(authorData)

                if author['author_profile_id'] and self.db is not None:
                    personData = (
                        author['person_id'],
                        author['author_profile_id'],
                        author['orcid_id'],
                        author['affiliation'],
                        author['email_address'],
                        author['name'],
                    )
                    self.db.insertPersons(personData)

            # Output title so user can see progress.
            self.logger.debug('Reading \'{title}\' in {conference}.'.format(
                title=paper.get('title').encode('utf-8'),
                conference=conference.get('acronym').encode('utf-8'),
                )
            )

            fulltext = paper.get('fulltext')
            meta = deepcopy(paper)
            meta.pop('fulltext', None)

            # Finally, insert paper into db.
            if self.db is not None:
                paperData = (
                    int(meta.get('article_id')),
                    meta.get('title'),
                    meta.get('abstract'),
                    int(meta.get('proc_id')),
                    meta.get('article_publication_date'),
                    meta.get('url'),
                    meta.get('doi_number'),
                )
                self.db.insertPapers(paperData)

            yield (fulltext, meta)

    def _readFromDisk(self):
        """Reads all paper json objects from disk.
        Also writes papers and conference metadata to sqlite3 db.

        Args:
            dirPath: full path of directory to load abstracts from.
            writeToDB: whether to write loaded data to db.

        Returns:
            A tuple of fulltexts and their respective metadata.
        """
        if self.directory is None:
            raise AttributeError(
                'Directory is None. '
                'Perhaps you meant to call readFromParser?'
            )

        for tup in tqdm(Reader.loadAllJsonFiles(self.directory)):
            (obj, conference, filepath) = tup

            # Check for 'metadata.txt' file that contains conference metadata
            # and insert it into database.
            if 'series_id' in obj and self.db is not None:
                conferenceData = (
                    int(obj.get('proc_id')),
                    obj.get('series_id'),
                    obj.get('acronym'),
                    obj.get('isbn13'),
                    obj.get('year'),
                    obj.get('proc_title'),
                    obj.get('series_title'),
                    obj.get('series_vol'),
                )
                self.db.insertConferences(conferenceData)
                continue

            # Add person and author to database.
            for author in obj.get('authors'):
                # Need to cast certain fields to match sqlite datatypes.
                if (author['author_profile_id'] != '' and
                        author['author_profile_id'] is not None):
                    author['author_profile_id'] = int(
                        author['author_profile_id']
                    )
                else:
                    author['author_profile_id'] = -1
                author['author_profile_id'] = int(author['author_profile_id'])

                if (author['orcid_id'] != '' and
                        author['orcid_id'] is not None):
                    author['orcid_id'] = int(author['orcid_id'])

                # Note: there isn't a field that every author entry in 
                # the proceedings is guaranteed to have so we're just 
                # sticking with person_id.
                if author['person_id'] is None:
                    continue

                authorData = (
                    author['person_id'],
                    int(obj.get('article_id')),
                )

                if self.db is not None:
                    self.db.insertAuthors(authorData)

                if self.db is not None:
                    personData = (
                        author['person_id'],
                        author['author_profile_id'],
                        author['orcid_id'],
                        author['affiliation'],
                        author['email_address'],
                        author['name'],
                    )
                    self.db.insertPersons(personData)

            # Output title so user can see progress.
            self.logger.debug('Reading \'{title}\' in {conference}.'.format(
                title=obj.get('title').encode('utf-8'),
                conference=conference.encode('utf-8'),
                )
            )

            fulltext = obj.get('fulltext')
            meta = deepcopy(obj)
            meta.pop('fulltext', None)

            # Finally, insert paper into db.
            if self.db is not None:
                paperData = (
                    int(meta.get('article_id')),
                    meta.get('title'),
                    meta.get('abstract'),
                    int(meta.get('proc_id')),
                    meta.get('article_publication_date'),
                    meta.get('url'),
                    meta.get('doi_number'),
                )
                self.db.insertPapers(paperData)

            yield (fulltext, meta)

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
    def loadAllJsonFiles(dirPath):
        """Generator that lazy loads all of the files from a directory.

        Args:
            dirPath: full path of the directory to load files from.

        Returns:
            A generator that yields each paper in the following form:
                (paper json object, conference acronym, path).
        """
        for child in os.listdir(dirPath):
            childPath = os.path.join(dirPath, child)
            if not os.path.isdir(childPath):
                yield (
                    (Reader.loadJsonFile(childPath),  # Document json obj.
                     os.path.basename(os.path.dirname(childPath)),  # Conf.
                     childPath)  # File path.
                )
            else:
                for obj in Reader.loadAllJsonFiles(childPath):
                    yield obj
