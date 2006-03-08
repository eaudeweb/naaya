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

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from RemoteChannel import RemoteChannel

manage_addRemoteChannelFacadeForm = PageTemplateFile('zpt/remotechannelfacade_manage_add', globals())
def manage_addRemoteChannelFacade(self, id='', title='', url='', providername='',
    location='', numbershownitems='', portlet='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_SUFIX_REMOTECHANNELFACADE % self.utGenRandomId(6)
    try: numbershownitems = abs(int(numbershownitems))
    except: numbershownitems = 0
    ob = RemoteChannelFacade(id, title, url, providername, location, numbershownitems)
    self._setObject(id, ob)
    if portlet:
        self.create_portlet_for_remotechannelfacade(self._getOb(id))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class RemoteChannelFacade(RemoteChannel):
    """ """

    meta_type = METATYPE_REMOTECHANNELFACADE
    icon = 'misc_/NaayaCore/RemoteChannelFacade.gif'

    manage_options = (
        RemoteChannel.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, url, providername, location, numbershownitems):
        """ """
        RemoteChannel.__dict__['__init__'](self, id, title, url, numbershownitems)
        self.providername = providername
        self.location = location

    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        RemoteChannelFacade.inheritedAttribute('manage_beforeDelete')(self, item, container)

    #api

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', url='', providername='', location='',
        numbershownitems='', REQUEST=None):
        """ """
        try: numbershownitems = abs(int(numbershownitems))
        except: numbershownitems = self.numbershownitems
        self.title = title
        self.url = url
        self.providername = providername
        self.location = location
        self.numbershownitems = numbershownitems
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html')

    #zmi forms
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/remotechannelfacade_properties', globals())

InitializeClass(RemoteChannelFacade)
