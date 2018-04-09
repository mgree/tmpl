import logging
import sqlite3

connection = sqlite3.connect('test.db')


class TmplDB(object):
    """A class to interact with the tmpl sqlite3 database."""

    INIT_FILE = 'schemas/init.sql'

    def __init__(self, file):
        self.file = file

        self._connection = None
        self._cursor = None

    def init_db(self):
        with open(TmplDB.INIT_FILE, 'r') as f:
            self.cursor.executescript(f.read())
            self.connection.commit()

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


if __name__ == '__main__':
    db = TmplDB('tmpl_db.db')
    db.init_db()