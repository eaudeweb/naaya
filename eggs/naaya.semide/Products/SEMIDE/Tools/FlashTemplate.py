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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

#Zope imports
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view, manage_users
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Naaya imports
from Products.NaayaCore.managers.utils import utils

#SEMIDE imports
from Products.SEMIDE.constants import *
from XSLTemplate import manage_addXSLTemplate

manage_addFlashTemplateForm = PageTemplateFile('zpt/flashtemplate_add', globals())
def manage_addFlashTemplate(self, id, title='', notif_type='eflash', REQUEST=None):
    """ add a flash template """
    ob = FlashTemplate(id, title)
    self._setObject(id, ob)

    ob = self._getOb(id)
    ob.loadDefaultData(self.langs, notif_type)

    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)


class FlashTemplate(Folder, utils):
    """ Flash Template class """

    meta_type = FLASHTEMPLATE_METATYPE
    icon = 'misc_/SEMIDE/FlashTemplate.gif'

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id = id
        self.title = title

    def loadDefaultData(self, langs, notif_type):
        """ load the default XSLT templates """
        for lang in self.langs:
            manage_addXSLTemplate(self, id='html_%s' % lang, type='html', lang=lang, notif_type=notif_type)
            manage_addXSLTemplate(self, id='text_%s' % lang, type='text', lang=lang, notif_type=notif_type)

InitializeClass(FlashTemplate)