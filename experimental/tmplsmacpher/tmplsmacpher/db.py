import logging
import sqlite3


class TmplDB(object):
    """A class to interact with the tmpl sqlite3 database.

    A couple of things to note when using this class or sqlite3 in general:
        1) sqlite3 dynamically casts fields. If you pass in, let's say, a string for the field
            'year' which is defined as a sqlite3 INTEGER, it will still add the field without error!
    """
    logging.basicConfig(level=logging.INFO)

    INIT_FILE = 'schemas/init.sql'

    logger = logging.getLogger('TmplDB')

    def __init__(self, file, verbose=False):
        self.file = file
        self.verbose = verbose

        self._connection = None
        self._cursor = None

        # Cache table schemas so that we only need to query for them once.
        self.schemas = dict()

        # Create database file and necessary tables.
        self.init_db(TmplDB.INIT_FILE)

    @property
    def connection(self):
        """Represents the sqlite2 connection.

        Returns:
            Sqlite3 connection object.
        """
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(self.file)
            except Exception as e:
                self._connection = None
                logging.error(e)
        return self._connection

    @property
    def cursor(self):
        """Represents the sqlite3 cursor object. Use to interact with database through sql queries.

        Use:
            db = TmplDB('dbfile.db')
            db.cursor.execute('SELECT * FROM table_name;')

        Returns:
            Sqlite3 cursor object.
        """
        if self._cursor is None:
            try:
                self._cursor = self.connection.cursor()
            except Exception as e:
                self._cursor = None
                logging.error(e)
        return self._cursor

    def init_db(self, initFile):
        """Initializes database with sql script specified in TmplDB.INIT_FILE. Sets up
        all tables needed for one Tmpl topic modelling run.
        """
        with open(initFile, 'r') as f:
            self.cursor.executescript(f.read())
            self.connection.commit()

    def insert(self, tableName, obj):
        """Inserts item into desired table.

        Args:
            tableName: name of table to insert item into.
            obj: obj to be inserted into table; 
                of the form (column1, column2, ...)
        """
        if tableName not in self.schemas:
            self.schemas[tableName] = self.getColumns(tableName)
        columns = self.schemas[tableName]

        query = ('INSERT INTO {tableName} {columns} '
                 'VALUES ({valuePlaceholders});').format(
                    tableName=TmplDB.verifyName(tableName),
                    columns=columns,
                    valuePlaceholders=','.join(['?'] * len(columns))
                )
        self.log('insert: Query template = {query}'.format(query=query))
        self.log('insert: Inserting {object}'.format(object=obj))

        self.cursor.execute(query, obj)
        # Exception will be raised at commit() if insert failed else insert succeeded.
        self.connection.commit()
        self.log('insert: Insertion successfully committed.')

    def batchInsert(self, tableName, objects):
        """Performs a batch insert of objects into desired table.

        Args:
            tableName: table to insert objects into.
            objects: list of tuples representing objects to insert;
                of the form [(column1, column2, ...),
                             (column1, column2, ...),
                             ...
                            ]
        """
        if tableName not in self.schemas:
            self.schemas[tableName] = self.getColumns(tableName)
        columns = self.schemas[tableName]

        query = ('INSERT INTO {tableName} {columns} '
                 'VALUES ({valuePlaceholders});').format(
                    tableName=TmplDB.verifyName(tableName),
                    columns=columns,
                    valuePlaceholders=','.join(['?'] * len(columns))
                )
        self.log('batchInsert: Query template = {query}'.format(query=query))
        self.log('batchInsert: Inserting {objects}'.format(objects=objects))

        self.cursor.executemany(query, objects)
        self.cursor.commit()
        self.log('batchInsert: Insertions successfully committed.')

    def getColumns(self, tableName):
        """
        Fetchs the column names for a given table.
        Args:
            tableName: table whose fields to fetch.
        Returns:
            A tuple of the column names in the order 
                they appear in the schema (same order as in INIT_FILE).
        """
        query = 'SELECT * FROM {tableName};'.format(tableName=TmplDB.verifyName(tableName))
        self.cursor.execute(query)
        return tuple(map(lambda x: x[0], self.cursor.description))

    def log(self, msg):
        """Logs message according to verbosity instance variable.

        Args:
            msg: msg to log.
        """
        if self.verbose:
            logger.info(msg)

    @staticmethod
    def verifyName(name):
        """Verifies name (of table or column) to secure against sql injection attacks. Always use
        this function when substituting table names or columns since they cannot be parameterized
        with ?. Ensures that tableName or columns consist only of alphanumeric chars or chars from
        the validSymbols set.

        Args:
            name: sql entity name (table or column) to be verified:
        
        Raises:
            TmplDB.IllegalNameException if invalid character is found in name.
        Returns:
            Original name if name is valid.
        """
        validSymbols = {'_', '-'}
        cleaned = ''
        for char in name:
            if char.isalnum() or char in validSymbols:
                cleaned += char
            else:
                raise TmplDB.IllegalNameException(
                    'Invalid name: {name}. '
                    'name must consist of alphanumeric characters or {validSymbols}').format(
                        name=name,
                        validSymbols=validSymbols,
                    )
        return cleaned

    class IllegalNameException(Exception):
        """Exception denoting the use of an illegal name."""
        pass


if __name__ == '__main__':
    db = TmplDB('tmpl_db.db')
    kwargs = {'proc_id': 51,
              'series_id': 'series_id_test',
              'acronym': 'tst',
              'isbn13': 'isbn13_test',
              'year': 2018,
              'proc_title': 'proc_title_test',
              'series_title': 'series_title_test',
              'series_vol': 'series_vol_test'}
    db.insert('conference', **kwargs)

