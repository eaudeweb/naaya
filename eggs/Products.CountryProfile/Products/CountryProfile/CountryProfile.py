from OFS.SimpleItem import SimpleItem
from App.class_init import InitializeClass
from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from MySQLConnector import MySQLConnector


manage_add_html = PageTemplateFile('zpt/manage_add', globals())
def manage_add_object(self, id, REQUEST=None):
    """ Create new CountryProfile object from ZMI.
    """
    ob = CountryProfile(id)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return ob

from Products.NaayaCore.LayoutTool.DiskFile import allow_path
allow_path('Products.PyDigirSearch:www/css/')

class CountryProfile(SimpleItem):
    """
        CountryProfile object
    """
    meta_type = 'MedwisCountryProfile'
    icon = 'meta_type.gif'
    security = ClassSecurityInfo()

    manage_options = (
        SimpleItem.manage_options + (
            {'label' : 'Properties', 'action' :'manage_edit_html'},
        )
    )

    def __init__(self, id):
        self.id = id
        self.mysql_connection = {}
        self.mysql_connection['host'] = 'localhost'
        self.mysql_connection['name'] = 'medwis'
        self.mysql_connection['user'] = 'cornel'
        self.mysql_connection['pass'] = 'cornel'

    def open_dbconnection(self):
        """ Create and return a MySQL connection object """
        conn = MySQLConnector()
        conn.open(self.mysql_connection['host'], self.mysql_connection['name'],
                  self.mysql_connection['user'], self.mysql_connection['pass'])
        return conn

    _index = PageTemplateFile('zpt/index', globals())

    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/manage_edit', globals())

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
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
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST):
        """ """
        dbconn = self.open_dbconnection()
        records = self.get_population(dbconn)
        dbconn.close()
        return self._index(REQUEST, records=records)

    #--------QUERIES---------------#
    def get_population(self, dbconn):
        return dbconn.query(u"""SELECT * FROM COUNTRY""")


InitializeClass(CountryProfile)
