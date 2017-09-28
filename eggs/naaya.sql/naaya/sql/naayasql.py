# Python imports
import os.path
from os import remove, mkdir
try:
    import sqlite3
except ImportError:
    from pysqlite2 import dbapi2 as sqlite3
import sha
import string
from random import choice

# Zope imports
from Globals import Persistent

# CLIENT_HOME is a Zope2 specific constant
# usually referring to var/zope-instance, we want to create
# a similar directory sibling to it
DBS_FOLDER_PATH = os.path.join(CLIENT_HOME, "..", "naaya.sql")

class DbMissing(Exception):
    pass

class NaayaSqlDb(Persistent):

    def __init__(self, db_id):
        self.db_id = db_id

    def _get_path(self):
        """Used by the other methods"""
        return os.path.join(DBS_FOLDER_PATH, self.db_id)

    def cursor(self, isolation_level=None):
        """
        Returns a cursor to a connection to your sqlite database.
        Useful methods:
          * `execute`
          * `executescript`
          * `fetchone`
          * `fetchall`
        More info here:
        http://docs.python.org/library/sqlite3.html#cursor-objects

        """
        if not os.path.exists(self._get_path()):
            raise DbMissing
        connection = sqlite3.connect(self._get_path(),
                                     isolation_level=isolation_level)
        return connection.cursor()

    def drop(self):
        """Drop database, delete it from disk"""
        remove(self._get_path())

    def __repr__(self):
        return '<NaayaSqlDb id: %s>' % self.db_id

def new_db():
    exists = lambda x: (os.path.exists(os.path.join(DBS_FOLDER_PATH, x))
                        or os.path.exists(os.path.join(DBS_FOLDER_PATH,
                                                       x + '-journal')))
    unique = False
    while not unique:
        id = ''.join([choice(string.letters) for i in range(10)])
        unique = not exists(id)
    if not os.path.exists(DBS_FOLDER_PATH):
        mkdir(DBS_FOLDER_PATH, 0755)
    path = os.path.join(DBS_FOLDER_PATH, id)
    connection = sqlite3.connect(path)
    connection.close()
    return NaayaSqlDb(id)

