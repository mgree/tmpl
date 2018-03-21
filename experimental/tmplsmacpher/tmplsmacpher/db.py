import logging
import sqlite3

connection = sqlite3.connect('test.db')


class TmplDB(object):
    """A class to interact with the tmpl sqlite3 database."""

    def __init__(self, file):
        self.file = file

        self._connection = None
        self._cursor = None

    @property
    def connection(self):
        if self._connection is None:
            try:
                self._connection = sqlite3.connect(self.file)
            except Error as e:
                self._connection = None
                logging.error(e)

    def createTable(self, tableName, fields):
        query = (
            'CREATE TABLE IF NOT EXISTS {tableName}',
            '({fields})',
        ).format(tableName=tableName, fields=fields)

        try:
            c = self.connection.cursor()
            c.execute(query)
        except Error as e:
            logging.error(e)

