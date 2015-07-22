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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#   Alin Voinea, Eau de Web
""" 
This module contains the class that implements the Naaya Gadfly Container.
Usefull for counters.
"""
import os
from OFS.Folder import Folder
from OFS.Folder import manage_addFolder
from Products.ZGadflyDA.DA import manage_addZGadflyConnection
from AccessControl.Permissions import view_management_screens
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from zLOG import LOG, ERROR
from Products.ZGadflyDA.db import data_dir

CONNECTION_ID = 'connection'
CONNECTION_STRING = 'demo'
LOG_KEY = 'NaayaBase.NyGadflyContainer'

def manage_addNyGadflyContainer(self, id='.container', REQUEST=None, **kwargs):
    """ """
    ob = NyGadflyContainer(id)
    self._setObject(id, ob)
    ob = self._getOb(id)
    
    # Avoid crashing if gadfly is not initialized
    dir=os.path.join(data_dir, CONNECTION_STRING)
    if not os.path.isdir(dir):
        try:
            os.makedirs(dir)
        except OSError, error:
            LOG(LOG_KEY, ERROR, error)
            raise
    # Add gadfly connection
    manage_addZGadflyConnection(ob, id=CONNECTION_ID, title='', 
                                connection=CONNECTION_STRING, check=True)
    ob._init_table(**kwargs)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return ob

class NyGadflyContainer(Folder):
    """ Class that implements the Naaya Gadfly Container.
    
    >>> ob = NyGadflyContainer()
    >>> ob._init_table(page='VARCHAR', hits='FLOAT')
    >>> ob.add(hits=0, page='path/to/mypage')
    >>> ob.get(hits, page='path/to/mypage')
    [{'HITS': 0}]
    >>> ob.get(hits=0)
    [{'HITS': 0, 'PAGE': 'path/to/mypage'}]
    """
    
    meta_type = 'Naaya Gadfly Container'
    icon = 'misc_/Naaya/gadfly_container.gif'
    
    security = ClassSecurityInfo()
    
    def __init__(self, id='.container'):
        self._table_name = ''
        Folder.__init__(self, id)
    
    security.declarePrivate('_exec_query')
    def _exec_query(self, query='', **kwargs):
        """ Execute given query with kwargs as params
        """
        query = query % kwargs
        conn = self._getOb(CONNECTION_ID)
        try:
            res = conn.manage_test(query)
        except Exception, err:
            LOG(LOG_KEY, ERROR, err)
            res = ''
        return res
    
    security.declarePrivate('_init_table')
    def _init_table(self, **kwargs):
        """ CREATE TABLE table (kwargs[key1] = kwargs[value1], ..., 
                                kwargs[keyN] = kwargs[valueN])
        """
        path = self.absolute_url(1)
        self._table_name = path.replace('.', '').replace('-', '').replace('/', '_')

        attrs = []
        for key, value in kwargs.items():
            attrs.append("%s %s" % (key, value))
        attrs = ", ".join(attrs)
        
        query = "CREATE TABLE %(table)s (%(attrs)s)"
        return self._exec_query(query, table=self._table_name, attrs=attrs)
    
    security.declareProtected(view_management_screens, 'add')
    def add(self, **kwargs):
        """ INSERT INTO TABLE (kwargs.keys()) VALUES (kwargs.values())
        """
        keys = kwargs.keys()
        values = kwargs.values()
        for index, value in enumerate(values):
            if isinstance(value, str):
                values[index] = "'%s'" % value
            else:
                values[index] = "%s" % value
        
        keys = ', '.join(keys)
        values = ', '.join(values)
        
        query = "INSERT INTO %(table)s (%(keys)s) VALUES (%(values)s)"
        self._exec_query(query, table=self._table_name, keys=keys, values=values)
    
    security.declareProtected(view_management_screens, 'get')
    def get(self, *columns, **conditions):
        """ SELECT columns FROM table WHERE conditions
        """
        # Process columns
        if not columns:
            columns = "*"
        else:
            columns = ','.join(columns)

        # Process condition
        where = []
        for key, value in conditions.items():
            if isinstance(value, str):
                value = "'%s'" % value
            where.append("%s=%s" % (key, value))
        conditions = where and ' AND '.join(where) or '1=1'

        # Query
        query = "SELECT %(columns)s FROM %(table)s WHERE %(conditions)s"
        res = self._exec_query(query, table=self._table_name,
                               columns=columns, conditions=conditions)

        # Return
        if res:
            return res.dictionaries()
        return []

    security.declareProtected(view_management_screens, 'set')
    def set(self, key, value, **conditions):
        """ UPDATE TABLE SET key = value WHERE conditions
        """
        where = []
        for ckey, cvalue in conditions.items():
            if isinstance(cvalue, str):
                cvalue = "'%s'" % cvalue
            where.append("%s=%s" % (ckey, cvalue))
        
        # If not conditions, set nothing
        conditions = where and ' AND '.join(where) or '1 <> 1'
        
        query = "UPDATE %(table)s SET %(key)s = %(value)s WHERE %(conditions)s"
        self._exec_query(query, table=self._table_name, key=key, value=value,
                         conditions=conditions)
    
    security.declareProtected(view_management_screens, 'delete')
    def delete(self, **conditions):
        """ DELETE FROM table WHERE conditions
        """
        where = []
        for key, value in conditions.items():
            if isinstance(value, str):
                value = "'%s'" % value
            where.append("%s=%s" % (key, value))
        
        # If not conditions, remove nothing
        conditions = where and ' AND '.join(where) or '1 <> 1'
        
        query = "DELETE FROM %(table)s WHERE %(conditions)s"
        self._exec_query(query, table=self._table_name, conditions=conditions)

InitializeClass(NyGadflyContainer)
