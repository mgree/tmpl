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
            except Exception as e:
                self._connection = None
                logging.error(e)
        return self._connection

    @property
    def cursor(self):
        if self._cursor is None:
            try:
                self._cursor = self.connection.cursor()
            except Exception as e:
                self._cursor = None
                logging.error(e)
        return self._cursor

    def execute(self, query):
        c = self.cursor
        if c is not None:
            c.execute(query)
        raise Exception('Cursor is None.')


if __name__ == '__main__':
    query = (
        'CREATE TABLE IF NOT EXISTS projects ('
        'id integer PRIMARY KEY,'
        'name text NOT NULL,'
        'begin_date text,'
        'end_date text'
        ');'
    )
    db = TmplDB('test.db')
    cursor = db.cursor
    cursor.execute(query)