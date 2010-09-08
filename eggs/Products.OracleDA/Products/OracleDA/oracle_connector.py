
#python imports
import cx_Oracle

class oracle_connector:

    _db = None

    def _open(self, user='', pwd='', tns=''):
        """Open database connection. In case of errors exceptions are thrown."""
        return cx_Oracle.connect(user, pwd, tns)

    def _close(self, conn):
        """Closes database connection. In case of errors exceptions are thrown."""
        if not conn:
            raise Exception, self._Exception['db']
        conn.close()

    def _query(self, query, conn):
        """ Query database. Results are returned as a list of dictionaries. In case of errors exceptions are throw. """
        if not conn:
            raise Exception, self._Exception['db']
        cursor = conn.cursor()
        cursor.arraysize = 50
        cursor.execute(query)
        if cursor.description is None:
            return cursor.rowcount
        return cursor.fetchall()


    _Exception={
            'db':"You must use 'open' before any other operations with the connector"
    }