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
# Alexandru Ghica, Finsiel Romania

#Python imports

#Zope imports

#Product imports
import Globals


#portal related
REPORT_PRODUCT_NAME =       'Report'
REPORT_PRODUCT_PATH =       Globals.package_home(globals())

PERMISSION_ADD_REPORTSITE = 'Report - Add Report Site objects'

METATYPE_REPORTSITE =       'Report Site'

#interface related
MESSAGE_EMAILSENT =         'Email sent to all subscribers'
MESSAGE_GENERATED =          'Message generated succesfully'

#content related
ID_LINKCHECKER =        'LinkChecker'
TITLE_LINKCHECKER =     'Link checker'

ID_HELPDESKAGENT =      'HelpDesk'
TITLE_HELPDESKAGENT =   'Helpdesk'

#calendar related
ID_CALENDAR =           'portal_calendar'
ID_CALENDAR_CSS =       'calendar_style'
ID_RIGHT_ARROW =        'right_arrow'
ID_LEFT_ARROW =         'left_arrow'
CALENDAR_STARTING_DAY = 'Monday'

#LDAP plugin name
LDAP_PLUGIN = 'LDAPUserFolder'