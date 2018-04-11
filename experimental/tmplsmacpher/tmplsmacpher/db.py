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

    def insert(self, tableName, **kwargs):
        """Inserts a row into the table <tableName>. Fetches the columns from the desired
        table dynamically to first generate the proper INSERT query and then passes in
        kwargs as fields to query.
        All columns from table must be passed in as kwargs.
        """
        columns = self.getColumns(tableName)
        query = ('INSERT INTO {tableName} {columns} '
                 'VALUES ({valuePlaceholders});').format(
                    tableName=TmplDB.verifyName(tableName),
                    columns=columns,
                    valuePlaceholders=','.join(['?'] * len(columns))
                )
        TmplDB.logger.info('Insert: Query template = {query}'.format(query=query))

        # First check that the number of kwargs (fields) that the user passed in matches
        # the number of columns in the table.
        if len(kwargs) != len(columns):
            raise TmplDB.IllegalColumnException(
                'Passed in fields: {fields} do not match with columns: {columns} from table: {tableName}'.format(
                    fields=kwargs.keys(),
                    columns=columns,
                    tableName=tableName,
                )
            )

        # Next, order the passed in kwargs according to the order defined by the getColumns method
        # to ensure that fields are being added to the correct columns.
        values = []
        for key in columns:
            if key not in kwargs:
                raise TmplDB.IllegalColumnException(
                    'Column: {key} not present in kwargs. Must pass in fields for all columns: {columns}'.format(
                        key=key,
                        columns=columns,
                    )
                )
            else:
                values.append(kwargs[key])

        values = tuple(values)
        TmplDB.logger.info('Insert: Inserting {values}'.format(values=values))

        self.cursor.execute(query, values)
        self.connection.commit()  # Exception will be raised at commit() if insert failed else insert succeeded.
        TmplDB.logger.info('Insert: Insertion successfully committed.')

    def getColumns(self, tableName):
        """
        Fetchs the column names for a given table.

        Args:
            tableName: table whose fields to fetch.

        Returns:
            A tuple of the column names in the order they appear in the schema (same order as in INIT_FILE).
        """
        query = 'SELECT * FROM {tableName};'.format(tableName=TmplDB.verifyName(tableName))
        self.cursor.execute(query)
        return tuple(map(lambda x: x[0], self.cursor.description))  # Fetch the name only.

    @staticmethod
    def verifyName(name):
        """Verifies name (of table or column) to secure against sql injection attacks. Always use
        this function when substituting table names or columns since they cannot be parameterized
        with ?. Ensures that tableName or columns consist only of alphanumeric chars or chars from
        the validSymbols set.
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

    class IllegalColumnException(Exception):
        """Exception denoting the use of an illegal column."""
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

