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
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from ImageFile import ImageFile
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from constants import *
import SidimarSite

def initialize(context):
    """ """

    #register classes
    context.registerClass(
        SidimarSite.SidimarSite,
        permission = PERMISSION_ADD_SIDIMARSITE,
        constructors = (
                SidimarSite.manage_addSidimarSite_html,
                SidimarSite.manage_addSidimarSite,
                ),
        icon = 'www/Site.gif'
        )

misc_ = {
    'Site.gif':ImageFile('www/Site.gif', globals()),
    'MySQL.gif':ImageFile('www/MySQL.gif', globals()),
    'map.gif':ImageFile('www/map.gif', globals()),
    'posidonia.gif':ImageFile('www/posidonia.gif', globals()),
    'SIDIFLASH1.swf':ImageFile('www/SIDIFLASH1.swf', globals()),
    'SIDIFLASH2.swf':ImageFile('www/SIDIFLASH2.swf', globals()),
    'legenda.gif':ImageFile('www/legenda.gif', globals()),
    's-21-0.gif':ImageFile('www/s-21-0.gif', globals()),
    's-21-1.gif':ImageFile('www/s-21-1.gif', globals()),
    's-21-2.gif':ImageFile('www/s-21-2.gif', globals()),
    's-21-3.gif':ImageFile('www/s-21-3.gif', globals()),
    's-22-0.gif':ImageFile('www/s-22-0.gif', globals()),
    's-22-1.gif':ImageFile('www/s-22-1.gif', globals()),
    's-22-2.gif':ImageFile('www/s-22-2.gif', globals()),
    's-22-3.gif':ImageFile('www/s-22-3.gif', globals()),
    's-23-0.gif':ImageFile('www/s-23-0.gif', globals()),
    's-23-1.gif':ImageFile('www/s-23-1.gif', globals()),
    's-23-2.gif':ImageFile('www/s-23-2.gif', globals()),
    's-23-3.gif':ImageFile('www/s-23-3.gif', globals()),
    'error.gif':ImageFile('www/error.gif', globals()),
    'cam.gif':ImageFile('www/cam.gif', globals()),
    }