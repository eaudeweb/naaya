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
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Miruna Badescu

#Python imports

#Zope imports
from ImageFile import ImageFile

#Product imports
from constants import *
from tools.constants import *
from Products.NaayaCore.constants import *
import SMAPSite
from tools.SyncerTool import SyncerTool
from Products.NaayaCore.GeoMapTool import GeoMapTool
def initialize(context):
    """ """

    #register classes
    context.registerClass(
        SMAPSite.SMAPSite,
        permission = PERMISSION_ADD_SMAPSITE,
        constructors = (
                SMAPSite.manage_addSMAPSite_html,
                SMAPSite.manage_addSMAPSite,
                ),
        icon = 'www/Site.gif'
        )

    context.registerClass(
        SyncerTool.SyncerTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                SyncerTool.manage_addSyncerTool,
                ),
        icon = 'tools/SyncerTool/www/SyncerTool.gif'
        )

    context.registerClass(
        GeoMapTool.GeoMapTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                GeoMapTool.manage_addGeoMapTool,
                ),
        icon = '../NaayaCore/GeoMapTool/www/GeoMapTool.gif'
        )


misc_ = {
    'GeoMapTool.gif':ImageFile('../NaayaCore/GeoMapTool/www/GeoMapTool.gif', globals()),
    'dnt_rgis.swf': ImageFile('../NaayaCore/GeoMapTool/www/dnt_rgis.swf', globals()),
    'dntp_rgis.swf': ImageFile('../NaayaCore/GeoMapTool/www/dntp_rgis.swf', globals()),
    'bounding.xml': ImageFile('../NaayaCore/GeoMapTool/www/bounding.xml', globals()),
    'SyncerTool.gif':ImageFile('tools/SyncerTool/www/SyncerTool.gif', globals()),
    'Site.gif':ImageFile('www/Site.gif', globals()),
    'print.gif':ImageFile('www/print.gif', globals()),
    'sortdown.gif':ImageFile('www/sortdown.gif', globals()),
    'sortnot.gif':ImageFile('www/sortnot.gif', globals()),
    'sortup.gif':ImageFile('www/sortup.gif', globals()),
    'simpletreemenu.js':ImageFile('www/simpletreemenu.js', globals()),
    'closed.gif':ImageFile('www/closed.gif', globals()),
    'open.gif':ImageFile('www/open.gif', globals()),
}
