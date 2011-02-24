# -*- coding: utf-8 -*-
"""Using an existing MySQL database display some graphs and statistics. Also
perform searchs on the data
"""

from OFS.SimpleItem import SimpleItem
from App.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.LayoutTool.DiskFile import allow_path

from MySQLConnector import MySQLConnector
import queries

allow_path('Products.PyDigirSearch:www/css/')

manage_add_html = PageTemplateFile('zpt/manage_add', globals())
def manage_add_object(self, id, REQUEST=None):
    """ Create new CountryProfile object from ZMI"""

    ob = CountryProfile(id)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return ob

class CountryProfile(SimpleItem):
    """CountryProfile"""

    meta_type = 'MedwisCountryProfile'
    icon = 'meta_type.gif'
    security = ClassSecurityInfo()

    manage_options = (
        SimpleItem.manage_options + (
            {'label' : 'Properties', 'action' :'manage_edit_html'},
        )
    )
    _v_conn = None
    index_html = PageTemplateFile('zpt/index', globals())

    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/manage_edit', globals())

    def __init__(self, id):
        self.id = id
        self.mysql_connection = {}
        self.mysql_connection['host'] = 'localhost'
        self.mysql_connection['name'] = 'medwis'
        self.mysql_connection['user'] = 'cornel'
        self.mysql_connection['pass'] = 'cornel'

    @property
    def dbconn(self):
        """Create and return a MySQL connection object"""

        if self._v_conn is not None:
            return self._v_conn
        else:
            self._v_conn = MySQLConnector()
            self._v_conn.open(self.mysql_connection['host'],
                              self.mysql_connection['name'],
                              self.mysql_connection['user'],
                              self.mysql_connection['pass'])
            return self._v_conn

    def __del__(self):
        """Close db connection"""
        if self._v_conn is not None:
            self._v_conn.close()

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """Save mysql connection data"""

        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            params = dict(REQUEST.form)
        else:
            params = kwargs

        self.mysql_connection = {}
        self.mysql_connection['host'] = params.pop('mysql_host')
        self.mysql_connection['name'] = params.pop('mysql_name')
        self.mysql_connection['user'] = params.pop('mysql_user')
        self.mysql_connection['pass'] = params.pop('mysql_pass')
        self._p_changed = True

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    def query(self, name, **kw):
        """Execute some query and return the data"""
        if hasattr(queries, name):
            result = getattr(queries, name)(self.dbconn, **kw)

InitializeClass(CountryProfile)
