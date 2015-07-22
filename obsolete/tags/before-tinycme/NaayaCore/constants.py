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
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

"""
This module contains global constants.
"""

#Python imports

#Zope imports
import Globals

#Product imports

NAAYACORE_PRODUCT_NAME = 'NaayaCore'
NAAYACORE_PRODUCT_PATH = Globals.package_home(globals())


METATYPE_FOLDER = 'Naaya Folder'


PERMISSION_ADD_NAAYACORE_TOOL = 'Add NaayaCore Tool'

METATYPE_CATALOGTOOL = 'Naaya Catalog Tool'
METATYPE_GEOMAPTOOL = 'Naaya GeoMap Tool'
METATYPE_EMAILTOOL = 'Naaya Email Tool'
METATYPE_EMAILTEMPLATE = 'Naaya Email Template'
METATYPE_TRANSLATIONSTOOL = 'Naaya Translations Tool'
METATYPE_SYNDICATIONTOOL = 'Naaya Syndication Tool'
METATYPE_LOCALCHANNEL = 'Naaya Local Channel'
METATYPE_SCRIPTCHANNEL = 'Naaya Script Channel'
METATYPE_REMOTECHANNEL = 'Naaya Remote Channel'
METATYPE_REMOTECHANNELFACADE = 'Naaya Remote Channel Facade'
METATYPE_AUTHENTICATIONTOOL = 'Naaya User Folder'
METATYPE_PROPERTIESTOOL = 'Naaya Properties Tool'
METATYPE_DYNAMICPROPERTIESTOOL = 'Naaya Dynamic Properties Tool'
METATYPE_DYNAMICPROPERTIESITEM = 'Naaya Dynamic Properties Item'
METATYPE_PORTLETSTOOL = 'Naaya Portlets Tool'
METATYPE_PORTLET = 'Naaya Portlet'
METATYPE_HTMLPORTLET = 'Naaya HTML Portlet'
METATYPE_LINKSLIST = 'Naaya Links List'
METATYPE_REFLIST = 'Naaya Ref List'
METATYPE_REFTREE = 'Naaya Ref Tree'
METATYPE_REFTREENODE = 'Naaya Ref Tree Node'
METATYPE_FORMSTOOL = 'Naaya Forms Tool'
METATYPE_LAYOUTTOOL = 'Naaya Layout Tool'
METATYPE_TEMPLATE = 'Naaya Template'
METATYPE_SKIN = 'Naaya Skin'
METATYPE_SCHEME = 'Naaya Scheme'
METATYPE_STYLE = 'Naaya Style'
METATYPE_NOTIFICATIONTOOL = 'Naaya Notification Tool'
METATYPE_PROFILESTOOL = 'Naaya Profiles Tool'
METATYPE_PROFILE = 'Naaya Profile'
METATYPE_PROFILESHEET = 'Naaya Profile Sheet'

ID_CATALOGTOOL = 'portal_catalog'
TITLE_CATALOGTOOL = 'Portal catalog'
ID_GEOMAPTOOL = 'portal_map'
TITLE_GEOMAPTOOL = 'Portal Geo Map'
ID_EMAILTOOL = 'portal_email'
TITLE_EMAILTOOL = 'Portal email tool'
ID_TRANSLATIONSTOOL = 'portal_translations'
TITLE_TRANSLATIONSTOOL = 'Portal translations'
ID_SYNDICATIONTOOL = 'portal_syndication'
TITLE_SYNDICATIONTOOL = 'Portal syndication'
ID_AUTHENTICATIONTOOL = 'acl_users'
TITLE_AUTHENTICATIONTOOL = 'Portal user folder'
ID_PROPERTIESTOOL = 'portal_properties'
TITLE_PROPERTIESTOOL = 'Portal properties'
ID_DYNAMICPROPERTIESTOOL = 'portal_dynamicproperties'
TITLE_DYNAMICPROPERTIESTOOL = 'Portal dynamic properties'
ID_FORMSTOOL = 'portal_forms'
TITLE_FORMSTOOL = 'Portal forms tool'
ID_LAYOUTTOOL = 'portal_layout'
TITLE_LAYOUTTOOL = 'Portal layout tool'
ID_DEFAULTSTYLE = 'style_css'
ID_PORTLETSTOOL = 'portal_portlets'
TITLE_PORTLETSTOOL = 'Portal portlets'
TITLE_LOCALIZER = 'Localizer'
ID_NOTIFICATIONTOOL = 'portal_notification'
TITLE_NOTIFICATIONTOOL = 'Portal notification'
ID_PROFILESTOOL = 'portal_profiles'
TITLE_PROFILESTOOL = 'Portal profiles'

PREFIX_PORTLET = 'portlet_'
PREFIX_SUFIX_LOCALCHANNEL = 'lc%s_%s_rdf'
PREFIX_SUFIX_SCRIPTCHANNEL = 'sc%s_%s_rdf'
PREFIX_SUFIX_REMOTECHANNEL = 'rc%s'
PREFIX_SUFIX_REMOTECHANNELFACADE = 'rcf%s'
PREFIX_SUFIX_REFLIST = 'rl%s'
PREFIX_SUFIX_REFLISTITEM = 'rli%s'
PREFIX_SUFIX_REFTREE = 'rt%s'
PREFIX_SUFIX_LINKSLIST = 'll%s'
