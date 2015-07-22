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
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
from managers.portlets_templates import *
from Portlet import manage_addPortlet_html, addPortlet
from HTMLPortlet import manage_addHTMLPortlet_html, addHTMLPortlet
from LinksList import manage_addLinksListForm, manage_addLinksList
from RefList import manage_addRefListForm, manage_addRefList
from RefTree import manage_addRefTreeForm, manage_addRefTree

def manage_addPortletsTool(self, REQUEST=None):
    """ """
    ob = PortletsTool(ID_PORTLETSTOOL, TITLE_PORTLETSTOOL)
    self._setObject(ID_PORTLETSTOOL, ob)
    self._getOb(ID_PORTLETSTOOL).loadDefaultData()
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class PortletsTool(Folder, utils):
    """ """

    meta_type = METATYPE_PORTLETSTOOL
    icon = 'misc_/NaayaCore/PortletsTool.gif'

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Left portlets', 'action': 'manage_left_portlets_html'},
            {'label': 'Center portlets', 'action': 'manage_center_portlets_html'},
            {'label': 'Right portlets', 'action': 'manage_right_portlets_html'},
        )
        +
        Folder.manage_options[2:]
    )

    security = ClassSecurityInfo()

    meta_types = (
        {'name': METATYPE_PORTLET, 'action': 'manage_addPortlet_html'},
        {'name': METATYPE_HTMLPORTLET, 'action': 'manage_addHTMLPortlet_html'},
        {'name': METATYPE_LINKSLIST, 'action': 'manage_addLinksListForm'},
        {'name': METATYPE_REFLIST, 'action': 'manage_addRefListForm'},
        {'name': METATYPE_REFTREE, 'action': 'manage_addRefTreeForm'},
    )
    all_meta_types = meta_types

    #constructors
    manage_addPortlet_html = manage_addPortlet_html
    addPortlet = addPortlet
    manage_addHTMLPortlet_html = manage_addHTMLPortlet_html
    addHTMLPortlet = addHTMLPortlet
    manage_addLinksListForm = manage_addLinksListForm
    manage_addLinksList = manage_addLinksList
    manage_addRefListForm = manage_addRefListForm
    manage_addRefList = manage_addRefList
    manage_addRefTreeForm = manage_addRefTreeForm
    manage_addRefTree = manage_addRefTree

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        #load default stuff
        pass

    #api
    def getPortletsTypes(self): return PORTLETS_TYPES
    def getPortlets(self): return self.objectValues([METATYPE_PORTLET, METATYPE_HTMLPORTLET])
    def getLinksLists(self): return self.objectValues(METATYPE_LINKSLIST)
    def getRefLists(self): return self.objectValues(METATYPE_REFLIST)
    def getRefTrees(self): return self.objectValues(METATYPE_REFTREE)
    def getPortletsIds(self): return self.objectIds([METATYPE_PORTLET, METATYPE_HTMLPORTLET])

    def get_html_portlets(self):
        return [x for x in self.objectValues(METATYPE_HTMLPORTLET) if x.portlettype==0]
    def get_linkslists_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==1]
    def get_remotechannels_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==2]
    def get_remotechannelsfacade_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==6]
    def get_localchannels_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==3]
    def get_folders_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==4]
    def get_special_portlets(self):
        return [x for x in self.objectValues(METATYPE_PORTLET) if x.portlettype==100]

    def getPortletById(self, p_id):
        #return the portlet with the given id
        try: ob = self._getOb(p_id)
        except: ob = None
        if ob is not None:
            if ob.meta_type not in [METATYPE_PORTLET, METATYPE_HTMLPORTLET]: ob = None
        return ob

    def getLinksListById(self, p_id):
        #return the links list with the given id
        try: ob = self._getOb(p_id)
        except: ob = None
        if ob is not None:
            if ob.meta_type != METATYPE_LINKSLIST: ob = None
        return ob

    def getRefListById(self, p_id):
        #return the selection list with the given id
        try: ob = self._getOb(p_id)
        except: ob = None
        if ob is not None:
            if ob.meta_type != METATYPE_REFLIST: ob = None
        return ob

    def getRefTreeById(self, p_id):
        #return the selection tree with the given id
        try: ob = self._getOb(p_id)
        except: ob = None
        if ob is not None:
            if ob.meta_type != METATYPE_REFTREE: ob = None
        return ob

    #zmi actions
    security.declareProtected(view_management_screens, 'manage_left_portlets')
    def manage_left_portlets(self, portlets=[], REQUEST=None):
        """ """
        self.getSite().set_left_portlets_ids(self.utConvertToList(portlets))
        if REQUEST: REQUEST.RESPONSE.redirect('manage_left_portlets_html')

    security.declareProtected(view_management_screens, 'manage_center_portlets')
    def manage_center_portlets(self, portlets=[], REQUEST=None):
        """ """
        self.getSite().set_center_portlets_ids(self.utConvertToList(portlets))
        if REQUEST: REQUEST.RESPONSE.redirect('manage_center_portlets_html')

    security.declareProtected(view_management_screens, 'manage_set_right_portlets')
    def manage_set_right_portlets(self, portlets=[], folder='', REQUEST=None):
        """ """
        self.getSite().set_right_portlets_locations(folder, self.utConvertToList(portlets))
        if REQUEST: REQUEST.RESPONSE.redirect('manage_right_portlets_html')

    security.declareProtected(view_management_screens, 'manage_delete_right_portlets')
    def manage_delete_right_portlets(self, ids=[], REQUEST=None):
        """ """
        ids = self.utConvertToList(ids)
        ob = self.getSite()
        for pair in ids:
            location, id = pair.split('||')
            ob.delete_right_portlets_locations(location, id)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_right_portlets_html')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_left_portlets_html')
    manage_left_portlets_html = PageTemplateFile('zpt/manage_left_portlets', globals())

    security.declareProtected(view_management_screens, 'manage_center_portlets_html')
    manage_center_portlets_html = PageTemplateFile('zpt/manage_center_portlets', globals())

    security.declareProtected(view_management_screens, 'manage_right_portlets_html')
    manage_right_portlets_html = PageTemplateFile('zpt/manage_right_portlets', globals())

InitializeClass(PortletsTool)
