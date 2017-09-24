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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Anton Cupcea, Finsiel Romania


#Zope imports
import Products
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens, view
from oracle_connector import oracle_connector

manage_addOracleConnectorForm = PageTemplateFile('zpt/add', globals())
def manage_addOracleConnector(self, id, title='', user='', pwd='', tns='', REQUEST=None):
    """ Adds a new OracleConnector object """
    ob = OracleConnector(id, title, user, pwd, tns)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)


class OracleConnector(Folder, oracle_connector):
    """ Oracle Connector. Provides basic operations for Oracle database """

    meta_type = 'OracleDA'
    #product_name = 'OracleDA'

    manage_options =((Folder.manage_options[0],) +
                ({'label':'Properties',          'action':'properties_html'},)
                )

    def all_meta_types(self):
        """ What can you put inside me? """
        f = lambda x: x['name'] in ('Script (Python)')
        return [ x for x in filter(f, Products.meta_types)]

    def __init__(self, id, title, user, pwd, tns):
        """ """
        self.id = id
        self.title = title
        self.user = user
        self.pwd = pwd
        self.tns = tns
        self._p_changed = 1

    security = ClassSecurityInfo()

    #API
    security.declarePublic('openConnection')
    def openConnection(self):
        """ open a connection"""
        return self._open(self.user, self.pwd, self.tns)

    security.declarePublic('closeConnection')
    def closeConnection(self, conn):
        """ close a connection """
        self._close(conn)

    security.declarePublic('query')
    def query(self, sql, conn):
        """ execute a query against the database """
        return self._query(sql, conn)

    security.declarePublic('execute')
    def execute(self, sql):
        """ open, execute and close a database connection """
        conn = self.openConnection()
        results = self.query(sql, conn)
        self.closeConnection(conn)
        return results

    #management tabs
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', user='', pwd='',tns='', REQUEST=None):
        """ manage basic properties for NyThesaurus """
        self.title = title
        self.user = user
        self.pwd = pwd
        self.tns = tns
        self._p_changed = 1
        if REQUEST:
            return REQUEST.RESPONSE.redirect('properties_html')

    security.declareProtected(view_management_screens, 'testConnection')
    def testConnection(self, query='', REQUEST=None):
        """ test connection """
        try:
            conn = self.openConnection()
            if query:
                self.query(query, conn)
        except Exception, error:
            msg = str(error)
        else:
            self.closeConnection(conn)
            msg = 'The database connection successfully tested.'
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('properties_html?msg=%s' % msg)

    security.declareProtected(view_management_screens, 'properties_html')
    properties_html = PageTemplateFile('zpt/properties', globals())

InitializeClass(OracleConnector)