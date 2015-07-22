# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Ghica, Finsiel Romania
# Cornel Nitu, Finsiel Romania
#
#$Id: MySQLConnector.py 3238 2005-03-28 09:09:56Z nituacor $

__version__='$Revision: 1.1 $'[11:-2]

# python imports
import MySQLdb

DB_TIMEOUT = 30

class MySQLConnector:
    """ MySQL Connector. Provides basic operations for MySQL Database """

    _db = None

    def _open(self, conv='', host='', user='', passwd='', db='', port=0):
        """Open database connection. In case of errors exceptions are thrown."""
        if conv=='':
            self._db = MySQLdb.connect(host, user, passwd, db, port, connect_timeout = DB_TIMEOUT)
        else:
            self._db = MySQLdb.connect(conv=conv, host=host, user=user, passwd=passwd, db=db, port=port, connect_timeout = DB_TIMEOUT)

    def _close(self):
        """Closes database connection. In case of errors exceptions are thrown."""
        if not self._db:
            raise Exception, self._Exception['db']
        self._db.close()

    def _beginTransaction(self):
        """ Begin a transaction. In case of errors exceptions are throw."""
        if not self._db:
            raise Exception, self._Exception['db']
        self._db.begin()

    def _commitTransaction(self):
        """ Commit a transaction. In case of errors exceptions are throw."""
        if not self._db:
            raise Exception, self._Exception['db']
        self._db.commit()

    def _rollbackTransaction(self):
        """ Rollback a transaction. In case of errors exceptions are throw."""
        if not self._db:
            raise Exception, self._Exception['db']
            self._db.rollback()

    def _rpc_query(self, queryString):
        """ Query database. Results are returned as a list of dictionaries. In case of errors exceptions are throw. """
        if not self._db:
            raise Exception, self._Exception['db']
        l_cursor = self._db.cursor(MySQLdb.cursors.Cursor)
        l_cursor.execute(queryString)
        if l_cursor.description == None:
            return l_cursor.rowcount
        return l_cursor.fetchall()

    def _query(self, queryString):
        """ Query database. Results are returned as a list of dictionaries. In case of errors exceptions are throw. """
        if not self._db:
            raise Exception, self._Exception['db']
        l_cursor = self._db.cursor(MySQLdb.cursors.DictCursor)
        l_cursor.execute(queryString)
        if l_cursor.description == None:
            return l_cursor.rowcount
        return l_cursor.fetchall()

    _Exception={
            'db':"You must use 'open' before any other operations with the connector"
    }