import MySQLdb

class MySQLConnector(object):
    """ Provides basic operations for MySQL Database. """

    _db = None

    def open(self, host='', db='', user='', passwd='', port=3306):
        """
        Open database connection. In case of errors exceptions are thrown.
        """
        self._db = MySQLdb.connect(host, user, passwd, db, port, connect_timeout = 30, init_command='SET NAMES utf8')

    def close(self):
        """
        Closes database connection. In case of errors exceptions are thrown.
        """

        if not self._db:
            raise Exception, self._Exception['db']
        self._db.close()

    def query(self, q, debug=False):
        """Query database; results are returned as a list of dictionaries.
        In case of errors exceptions are throw.

        """
        if debug:
            print q
        if not self._db:
            raise Exception, self._Exception['db']
        cursor = self._db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(q)
        if cursor.description == None:
            return cursor.rowcount
        return cursor.fetchall()

    _Exception={
            'db':"You must use 'open' before any other operations with the connector"
    }
