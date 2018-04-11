import logging
import sqlite3


class TmplDB(object):
    """A class to interact with the tmpl sqlite3 database."""

    INIT_FILE = 'schemas/init.sql'

    def __init__(self, file):
        self.file = file

        self._connection = None
        self._cursor = None

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

    def insertConference(self, **kwargs):
        """Inserts a conference entity into the TmplDB object. Uses .fullschema command
        to first generate the proper INSERT query and the passed in
        kwargs as fields. Must pass in the fields in the order they appear in the schema to
        ensure they get added to their appropriate columns correctly.
        """
        pass

    def getColumns(self, tableName):
        """
        Fetchs the column names for a given table.

        Args:
            tableName: table whose fields to fetch.

        Returns:
            A tuple of the column names in the order they appear in the schema (same order as in INIT_FILE).
        """
        query = 'SELECT * FROM {tablName};'.format(TmplDB.clean(tableName))
        descriptions = self.cursor.execute(query, tableName)
        return descriptions.keys()

    @staticmethod
    def clean(tableName):
        """Cleans tableName to secure against sql injection attacks. Always use
        this function when substituting table names since they cannot be parameterized
        with ?. Ensures that tableName consists only of alphanumeric chars or chars from
        the validSymbols set.
        """
        validSymbols = {'_', '-'}
        cleaned = ''
        for char in tableName:
            if char.isalnum() or char in validSymbols:
                cleaned += char
            else:
                raise TmplDB.IllegalTableNameException(
                    'Invalid tableName: {tableName}. '
                    'tableName must consist of alphanumeric characters or {validSymbols}').format(
                        tableName=tableName, validSymbols=validSymbols
                    )

    class IllegalTableNameException(Exception):
        """Exception denoting the use of an IllegalTableNameException."""
        pass


if __name__ == '__main__':
    db = TmplDB('tmpl_db.db')
    print(db.getColumns('conferences'))
