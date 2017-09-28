#Zope imports
from OFS.SimpleItem import SimpleItem
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Globals import InitializeClass
from AccessControl.Permissions import view
from AccessControl import ClassSecurityInfo

#Product's related imports
from Products.NaayaLinkChecker.Utils import UtilsManager

def manage_addLogEntry(self, user, date_create, url_list):
    """Add a Language"""
    id = 'log_%s' % self.umGenRandomKey(8)
    logentry = LogEntry(id, user, date_create, url_list)
    self._setObject(id, logentry)

class LogEntry(SimpleItem, UtilsManager):
    """LogEntry class"""

    meta_type = 'LogEntry'
    icon = 'misc_/NaayaLinkChecker/logentry'

    manage_options = (
        {'label': 'View', 'action': 'index_html',},)

    security = ClassSecurityInfo()

    def __init__(self, id, user, date_create, url_list):
        """Constructor"""
        self.id = id
        self.title = 'Log Entry at %s' % self.umFormatDateTimeToString(date_create)
        self.user = user
        self.date_create = date_create
        self.url_list = url_list
        UtilsManager.__dict__['__init__'](self)

    security.declareProtected(view, 'index_html')
    index_html = NaayaPageTemplateFile('zpt/LogEntry_index', globals(),
                                       'linkchecker_log_index')

InitializeClass(LogEntry)
