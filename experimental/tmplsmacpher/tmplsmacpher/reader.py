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

    def __init__(self, dirPath, db=None, parentLogger=None):
        self.dirPath = dirPath
        self.db = db

        if parentLogger:
            self.logger = parentLogger.getChild('JsonFileReader')
        else:
             self.logger = logging.getLogger('JsonFileReader')

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
                # Note: comments indicate column name in db table.
                conferenceData = (
                    int(doc.get('proc_id')), # proc_id
                    doc.get('series_id'), # series_id
                    doc.get('acronym'), # acronym
                    doc.get('isbn13'), # isbn13
                    doc.get('year'), # year
                    doc.get('proc_title'), # proc_title
                    doc.get('series_title'), # series_title
                    doc.get('series_vol'), # series_vol
                )
                self.db.insert('conference', conferenceData)
                self.logger.debug('DB: Wrote {conference} to {db}'.format(
                    conference=doc.get('series_title'),
                    db=self.db)
                )
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

                if author['person_id'] is None:
                    continue

                authorData = (
                    author['person_id'], # person_id
                    int(meta['article_id']), # article_id
                )
                self.db.insert('author', authorData)

                # Insert person object if this person was not already inserted.
                if author['person_id'] not in personIDSeen:
                    personIDSeen.add(author['person_id'])
                    personData = (
                        author['person_id'], # person_id,
                        author['author_profile_id'], # author_profile_id
                        author['orcid_id'], # orcid_id
                        author['affiliation'], # affiliation
                        author['email_address'], # email_address
                        author['name'], # name
                    )
                    self.db.insert('person', personData)

            if abstract is None:
                self.logger.debug(
                    '{conference}: {title} does not have an "abs" field.'
                    .format(conference=conference, title=title)
                )
                abstract = ''

            if fulltext is None:
                self.logger.debug(
                    '{conference}: {title} does not have an "fulltext" field.'
                    .format(conference=conference, title=title)
                )
                fulltext = ''

            # Output title so user can see progress.
            self.logger.debug('Found \'{title}\' in {conference}.'.format(
                title=title.encode('utf-8'),
                conference=conference.encode('utf-8'),
                )
            )

            # Already have seen this title before.
            if title in seen:
                self.logger.debug(
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
                paperData = (
                    int(doc.get('article_id')), # article_id
                    doc.get('title'), # title
                    doc.get('abstract'), # abstract
                    int(doc.get('proc_id')), # proc_id
                    doc.get('article_publication_date'), # article_publication_date
                    doc.get('url'), # url
                    doc.get('doi_number'), # doi_number
                )
                self.db.insert('paper', paperData)
                self.logger.debug('readAll: Wrote {paper} to {db}'.format(
                    paper=doc.get('title'), 
                    db=self.db,
                    )
                )

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
