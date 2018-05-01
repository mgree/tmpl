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
        self.init_db(TMPLDB_INIT_SCHEMA)

        if parentLogger:
            self.logger = parentLogger.getChild('TmplDB')
        else:
             self.logger = logging.getLogger('TmplDB')

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

    def init_db(self, initFile):
        """Initializes database with sql script specified in TmplDB.INIT_FILE. 
        Sets up all tables needed for one Tmpl topic modelling run.
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
        self.logger.debug(
            'insert: Query template = {query}'.format(query=query)
        )
        self.logger.debug(
            'insert: Inserting {object}'.format(object=obj)
        )

        self.cursor.execute(query, obj)
        # Exception will be raised at commit() if insert failed.
        self.connection.commit()
        self.logger.debug('insert: Insertion successfully committed.')

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
        # Exception will be raised at commit() if insert failed.
        self.connection.commit()
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
    row = (51,
              'series_id_test',
              'tst',
              'isbn13_test',
              2018,
              'proc_title_test',
              'series_title_test',
              'series_vol_test')
    db.insert('conference', row)

