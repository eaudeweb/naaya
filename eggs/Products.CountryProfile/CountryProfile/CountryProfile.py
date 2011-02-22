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

    def __init__(self, id):
        self.id = id

    def open_dbconnection(self):
        """ Create and return a MySQL connection object """
        conn = MySQLConnector()
        conn.open('localhost', 'medwis', 'cornel', 'cornel')
        return conn

    _index = PageTemplateFile('zpt/index', globals())

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