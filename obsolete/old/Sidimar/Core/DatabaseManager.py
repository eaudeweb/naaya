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
#$Id: DatabaseManager.py 3049 2005-02-10 09:50:03Z ghicaale $

__version__='$Revision: 1.7 $'[11:-2]


# python imports
from MySQLdb import escape_string

# product imports
from MySQLConnector import MySQLConnector


_DEBUG_MODE = 0

class DatabaseManager(MySQLConnector):
    """ Layer over the MySQLConnector. Handles all the operations made against the database """

    def __init__(self):
        """ """
        pass

    def __debug(self, msg):
        #print message in console
        if _DEBUG_MODE > 0: print msg

    def escape_string(self, p_value):
        #escapes the given value
        return escape_string(p_value)

    def testConnection(self, db_host, db_user, db_password, db_name, db_port):
        #tests the connection with the database
        try:
            self._open(host=db_host, user=db_user, passwd=db_password, db=db_name, port=db_port)
        except Exception, error:
            return str(error)
        else:
            self._close()
            return ''

    def openConnection(self, connector):
        #open database connection
        self._open(host=connector.db_host, user=connector.db_user, passwd=connector.db_password, db=connector.db_name, port=connector.db_port)

    def closeConnection(self):
        #close databse connection
        self._close()

    def beginTransaction(self):
        #begin a transaction; in case of errors exceptions are throw
        self._beginTransaction()

    def commitTransaction(self):
        #commit a transaction; in case of errors exceptions are throw
        self._commitTransaction()

    def rollbackTransaction(self):
        #rollback a transaction; in case of errors exceptions are throw
        self._rollbackTransaction()

    def query(self, sql):
        #executes a SQL query (select/insert/update/delete) without transaction
        try:
            self.__debug(sql)
            self._query('SET NAMES utf8')
            self._query('SET CHARACTER SET utf8')
            res = self._query(sql)
        except Exception, error:
            return (1, None, error)
        else:
            return (0, res, '')

    def rpc_query(self, sql):
        #executes a SQL query (select/insert/update/delete) without transaction
        try:
            self.__debug(sql)
            self._rpc_query('SET NAMES utf8')
            self._rpc_query('SET CHARACTER SET utf8')
            res = self._rpc_query(sql)
        except Exception, error:
            return (1, None, error)
        else:
            return (0, res, '')

    def execute(self, sql):
        #executes a SQL query (select/insert/update/delete) using a transaction
        self._beginTransaction()
        try:
            self.__debug(sql)
            res = self._query(sql)
        except Exception, error:
            self._rollbackTransaction()
            return (1, None, error)
        else:
            self._commitTransaction()
            return (0, res, '')