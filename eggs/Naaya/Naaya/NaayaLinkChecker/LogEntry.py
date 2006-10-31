#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "LinkChecker"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania are
#Copyright (C) 2006 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: Cornel Nitu (Finsiel Romania)


#Zope imports
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
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
    index_html = PageTemplateFile('zpt/LogEntry_index', globals())

InitializeClass(LogEntry)