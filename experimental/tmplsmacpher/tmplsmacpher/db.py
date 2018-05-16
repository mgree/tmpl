import logging
import sqlite3

from settings import TMPLDB_INIT_SCHEMA


class TmplDB(object):
    """A wrapper class around sqlite3 to store intermediate data and output
    of Tmpl topic models.

    Usage:
        As of now, each TopicModel instance instantiates its own
        TmplDB instance to store all of the data from a training run
        (which includes reading in the data).

        If you did want to instantiate a standalone TmplDB (with the current
        design of the Tmpl model training and data storage pipeline,
        you wouldn't have to but here's how anyways):

            db = TmplDB('dbfilename.sqlite3')
            personData = (
                AB123456789,  # person_id
                98647,  # author_profile_id
                834191243,  # orc_id
                'Pomona College',  # affiliation
                'bilbo@pomona.edu',  # email_address
                'Bilbo Baggins',  # name
            )
            db.insertPersons(personData)

    Args:
        path: absolute or relative path of where you want the database to live.
            eg. 'mydb.sqlite3'
        parentLogger: logger to use in the Parser instance.
            If None, a new Parser object will be instantiated for the
            Parser instance.

    """

    def __init__(self, path, parentLogger=None):
        self.path = path

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
            self.logger = logger

    @property
    def connection(self):
        """
        Represents the sqlite2 connection.

        Returns:
            Sqlite3 connection object.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.path)
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
        Ignores duplicate entries since we will likely encounter
        the same people multiple times when we extract authors from
        papers during the read step of a model pipeline.

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
            *args: any number of papers to insert.
        """
        query = (
            'INSERT INTO paper (article_id, title, abstract, proc_id, '
            ' article_publication_date, url, doi_number) '
            'VALUES (?, ?, ?, ?, ?, ?, ?);'
        )
        self._insert(query, args)

    def insertConferences(self, *args):
        """Inserts a variable number of conferences into the 'conference' table
        of this TmplDB instance.

        Args:
            *args: any number of conferences to insert.
        """
        query = (
            'INSERT INTO conference (proc_id, series_id, ' 
            'acronym, isbn13, year, proc_title, series_title, series_vol) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?);'
        )
        self._insert(query, args)

    def insertScores(self, *args):
        """Inserts a variable number of scores into the 'score' table
        of this TmplDB instance.

        Args:
            *args: any number of scores to insert.
        """
        query = (
            'INSERT INTO score (article_id, topic_id, ' 
            'model_id, score) '
            'VALUES (?, ?, ?, ?);'
        )
        self._insert(query, args)

    def insertModels(self, *args):
        """Inserts a variable number of models into the 'conference' table
        of this TmplDB instance.

        Args:
            *args: any number of models to insert.
        """
        query = (
            'INSERT INTO model (model_id, model_path, timestamp, num_topics, '
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

