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
    """A class to read in the parsed DL files. Updates the given TmplDB.
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

    def readFromParser(self):
        """Reads all paper json objects from a passed in parser."""
        if self.parser is None:
            raise AttributeError('Parser is None. Perhaps you meant to call readFromDisk?')

        fulltexts = []
        metas = []
        curConference = None

        for (conference, paper) in self.parser.parse():
            # First conference or found a new conference. Update TmplDB with conference data.
            if curConference is None or conference['proc_id'] != curConference['proc_id']:
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
                    author['person_id'], # person_id
                    int(paper.get('article_id')), # article_id
                )

                if self.db is not None:
                    self.db.insertAuthors(authorData)

                if author['person_id'] and self.db is not None:
                    personData = (
                        author['person_id'], # person_id,
                        author['author_profile_id'], # author_profile_id
                        author['orcid_id'], # orcid_id
                        author['affiliation'], # affiliation
                        author['email_address'], # email_address
                        author['name'], # name
                    )
                    self.db.insertPersons(personData)

            # Output title so user can see progress.
            self.logger.debug('Reading \'{title}\' in {conference}.'.format(
                title=paper.get('title').encode('utf-8'),
                conference=conference.get('acronym').encode('utf-8'),
                )
            )

            fulltexts.append(paper.get('fulltext'))
            meta = deepcopy(paper)
            meta.pop('fulltext', None)
            metas.append(meta)

            # Finally, insert paper into db.
            if self.db is not None:
                paperData = (
                    int(meta.get('article_id')), # article_id
                    meta.get('title'), # title
                    meta.get('abstract'), # abstract
                    int(meta.get('proc_id')), # proc_id
                    meta.get('article_publication_date'), # article_publication_date
                    meta.get('url'), # url
                    meta.get('doi_number'), # doi_number
                )
                self.db.insertPapers(paperData)

        # Make sure that we processed the same number of fulltexts and metadatas.
        if len(fulltexts) != len(metas):
            raise ValueError(
                'Read in an unequal numbers of fulltexts and metas: {numFulltexts} fulltexts, {numMetas} metas'.format(
                    numFulltexts=len(fulltexts),
                    numMetas=len(metas),
                )
            )

        return fulltexts, metas

    def readFromDisk(self):
        """Reads all paper json objects from disk.
        Also writes papers and conference metadata to sqlite3 db.

        Args:
            dirPath: full path of directory to load abstracts from.
            writeToDB: whether to write loaded data to db.

        Returns:
            A tuple of fulltexts and their respective metadata.
        """
        if self.directory is None:
            raise AttributeError('Directory is None. Perhaps you meant to call readFromParser?')

        fulltexts = []
        metas = []

        for obj in tqdm(Reader.loadAllJsonFiles(self.directory)):
            (paper, conference, filepath) = obj

            # Check for 'metadata.txt' file that contains conference metadata
            # and insert it into database.
            if 'series_id' in paper and self.db is not None:
                # Note: comments indicate column name in db table.
                conferenceData = (
                    int(paper.get('proc_id')), # proc_id
                    paper.get('series_id'), # series_id
                    paper.get('acronym'), # acronym
                    paper.get('isbn13'), # isbn13
                    paper.get('year'), # year
                    paper.get('proc_title'), # proc_title
                    paper.get('series_title'), # series_title
                    paper.get('series_vol'), # series_vol
                )
                self.db.insertConferences(conferenceData)
                continue

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
                    author['person_id'], # person_id
                    int(paper.get('article_id')), # article_id
                )

                if self.db is not None:
                    self.db.insertAuthors(authorData)

                if author['person_id'] and self.db is not None:
                    personData = (
                        author['person_id'], # person_id,
                        author['author_profile_id'], # author_profile_id
                        author['orcid_id'], # orcid_id
                        author['affiliation'], # affiliation
                        author['email_address'], # email_address
                        author['name'], # name
                    )
                    self.db.insertPersons(personData)

            # Output title so user can see progress.
            self.logger.debug('Reading \'{title}\' in {conference}.'.format(
                title=meta.get('title').encode('utf-8'),
                conference=conference.encode('utf-8'),
                )
            )

            fulltexts.append(paper.get('fulltext'))
            meta = deepcopy(paper)
            meta.pop('fulltext', None)
            metas.append(meta)

            # Finally, insert paper into db.
            if self.db is not None:
                paperData = (
                    int(meta.get('article_id')), # article_id
                    meta.get('title'), # title
                    meta.get('abstract'), # abstract
                    int(meta.get('proc_id')), # proc_id
                    meta.get('article_publication_date'), # article_publication_date
                    meta.get('url'), # url
                    meta.get('doi_number'), # doi_number
                )
                self.db.insertPapers(paperData)

        # Make sure that we processed the same number of fulltexts and metadatas.
        if len(fulltexts) != len(metas):
            raise ValueError(
                'Read in an unequal numbers of fulltexts and metas: {numFulltexts} fulltexts, {numMetas} metas'.format(
                    numFulltexts=len(fulltexts),
                    numMetas=len(metas),
                )
            )

        return fulltexts, metas

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
                    (Reader.loadJsonFile(childPath),  # Document json obj.
                     os.path.basename(os.path.dirname(childPath)),  # Conference.
                     childPath)  # File path.
                )
            else:
                objs += Reader.loadAllJsonFiles(childPath)
        return objs


if __name__ == '__main__':
    from db import TmplDB
    from parser import Parser

    path = './parsed'
    db = TmplDB('testReader.db')
    parser = Parser(dlDir='/Users/smacpher/clones/tmpl_venv/acm-data/proceedings')
    reader = Reader(parser=parser, db=db)
    documents = reader.readFromParser()
