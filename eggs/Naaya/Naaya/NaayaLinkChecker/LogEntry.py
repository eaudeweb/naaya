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
# Portions created by EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor:
# Cornel Nitu, Finsiel Romania
#
# Thanks to Timothy O'Malley for the timeoutsocket python module.
#  
#
# $Id: LogEntry.py 864 2003-12-08 17:14:01Z finrocvs $
#

from OFS.SimpleItem import SimpleItem
from Globals import DTMLFile

from Utils import UtilsManager

def manage_addLogEntry(self, user, date_create, url_list):
    """Add a Language"""
    id = 'log_' + str(self.umGenRandomKey(8))
    logentry = LogEntry(id, user, date_create, url_list)
    self._setObject(id, logentry)

class LogEntry(SimpleItem, UtilsManager):
    """LogEntry class"""

    meta_type = 'LogEntry'
    icon = 'misc_/LinkChecker/logentry'

    manage_options = (
        {'label': 'View', 'action': 'index_html',},)

    def __init__(self, id, user, date_create, url_list):
        """Constructor"""
        self.id = id
        self.title = 'Log Entry at ' + self.umFormatDateTimeToString(date_create)
        self.user = user
        self.date_create = date_create
        self.url_list = url_list
        UtilsManager.__dict__['__init__'](self)


    ########################################
    index_html = DTMLFile('dtml/LogEntry_index', globals())