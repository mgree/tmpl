import logging
import sqlite3

from settings import TMPLDB_INIT_SCHEMA

class TmplDB(object):
    """A class to interact with the tmpl sqlite3 database.

    A couple of things to note when using this class or sqlite3 in general:
        1) sqlite3 dynamically casts fields. 
            If you pass in, let's say, a string for the field
            'year' which is defined as a sqlite3 INTEGER, 
            it will still add the field without error!
    """

    def __init__(self, file, parentLogger=None):
        self.file = file

        self._connection = None
        self._cursor = None

        # Cache table schemas so that we only need to query for them once.
        self.schemas = dict()

        # Create database file and necessary tables.
        self._init_db(TMPLDB_INIT_SCHEMA)

        if parentLogger:
            self.logger = parentLogger.getChild('TmplDB')
        else:
            logger = logging.getLogger('TmplDB')
            streamHandler = logging.StreamHandler()
            streamHandler.setFormatter(getLoggingFormatter())
            logger.addHandler(streamHandler)
            self.logger = logger


    @property
    def connection(self):
        """Represents the sqlite2 connection.

        Returns:
            Sqlite3 connection object.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.file)
        return self._connection

    @property
    def cursor(self):
        """Represents the sqlite3 cursor object. 
        Use to interact with database through sql queries.

        Use:
            db = TmplDB('dbfile.db')
            db.cursor.execute('SELECT * FROM table_name;')

        Returns:
            Sqlite3 cursor object.
        """
        if self._cursor is None:
            self._cursor = self.connection.cursor()
        return self._cursor

    def insertAuthors(self, *args):
        """Inserts a variable number of authors 
        into the 'author' table of this TmplDB instance.

        Args:
            *args: any number of authors to insert
        """
        query = (
            'INSERT INTO author (person_id, article_id) '
            'VALUES (?, ?);'
        )
        self._insert(query, args)

    def insertPersons(self, *args):
        """Inserts a variable number of persons 
        into the 'person' table of this TmplDB instance.

        Args:
            *args: any number of persons to insert
        """
        query = (
            'INSERT OR IGNORE INTO person (person_id, author_profile_id, ' 
            'orcid_id, affiliation, email_address, name) '
            'VALUES (?, ?, ?, ?, ?, ?);'
        )
        self._insert(query, args)

    def insertPapers(self, *args):
        """Inserts a variable number of papers 
        into the 'paper' table of this TmplDB instance.

        Args:
            *args: any number of papers to insert
        """
        query = (
            'INSERT INTO paper (article_id, title, abstract, proc_id, '
            ' article_publication_date, url, doi_number) '
            'VALUES (?, ?, ?, ?, ?, ?, ?);'
        )
        self._insert(query, args)

    def insertConferences(self, *args):
        query = (
            'INSERT INTO conference (proc_id, series_id, ' 
            'acronym, isbn13, year, proc_title, series_title, series_vol) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?);'
        )
        self._insert(query, args)

    def insertScores(self, *args):
        query = (
            'INSERT INTO score (article_id, topic_id, ' 
            'model_id, score) '
            'VALUES (?, ?, ?, ?);'
        )
        self._insert(query, args)

    def insertModel(self, *args):
        query = (
            'INSERT INTO model (model_id, model_path, run_date, num_topics, '
            'num_features, max_iter, vectorizer, model_type) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?);'
        )
        self._insert(query, args)

    def _insert(self, query, objects):
        """Internal insert method that checks the number of objects
        being inserted and either inserts a single object or batch inserts
        a list of objects.

        Args:
            query: insert query to use
            objects: list of objects to insert
        """
        if len(objects) == 1:
            self.cursor.execute(query, objects[0])
        else:
            self.cursor.executemany(query, objects)
        self.connection.commit()

    def _init_db(self, initFile):
        """Initializes database with sql script specified in 'initFile'
        Sets up all tables needed for one Tmpl topic modelling run.

        Args:
            initFile: filename of sql script to run.
        """
        with open(initFile, 'r') as f:
            self.cursor.executescript(f.read())
            self.connection.commit()


if __name__ == '__main__':
    db = TmplDB('tmpl_db.db')
    row = (51,
              'series_id_test',
              'tst',
              'isbn13_test',
              2018,
              'proc_title_test',
              'series_title_test',
              'series_vol_test')
    db.insertConference(row)

