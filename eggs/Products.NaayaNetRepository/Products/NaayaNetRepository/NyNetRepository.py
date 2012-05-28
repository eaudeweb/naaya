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
from os.path import join

#Zope imports
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaCore.constants import *
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty
import NyNetSite

manage_addNyNetRepository_html = PageTemplateFile('zpt/netrepository_manage_add', globals())
def manage_addNyNetRepository(self, id='', title='', lang=None, REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYNETREPOSITORY + self.utGenRandomId(6)
    if lang is None: lang = self.gl_get_selected_language()
    ob = NyNetRepository(id, title, lang)
    self.gl_add_languages(ob)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.submitThis()
    ob.loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class NyNetRepository(LocalPropertyManager, Folder):
    """ """

    meta_type = METATYPE_NYNETREPOSITORY
    icon = 'misc_/NaayaNetRepository/NyNetRepository.gif'

    manage_options = (
        Folder.manage_options[0:2]
        +
        (
            {'label': 'Properties', 'action': 'manage_edit_html'},
        )
        +
        Folder.manage_options[3:8]
    )

    meta_types = (
        {'name': METATYPE_NYNETSITE, 'action': 'manage_addNyNetSite_html'},
    )
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'manage_addNyNetSite_html')
    manage_addNyNetSite_html = NyNetSite.manage_addNyNetSite_html

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'addNyNetSite')
    addNyNetSite = NyNetSite.addNyNetSite

    title = LocalProperty('title')

    def __init__(self, id, title, lang):
        """ """
        self.id = id
        self._setLocalPropValue('title', lang, title)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        #create some indexes in the portal catalog
        catalog = self.getCatalogTool()
        try: catalog.addIndex('language', 'FieldIndex')
        except: pass
        try: catalog.addIndex('type', 'FieldIndex')
        except: pass
        #create a portlet
        portlets_ob = self.getPortletsTool()
        portlet_id = '%s%s' % (PREFIX_PORTLET, self.id)
        portlets_ob.addPortlet(portlet_id, self.title_or_id(), 99)
        portlet_ob = portlets_ob._getOb(portlet_id)
        content = self.futRead(join(NAAYANETREPOSITORY_PRODUCT_PATH, 'data', 'portlet_netrepository.zpt'), 'r')
        content = content.replace('PORTLET_NETREPOSITORY_ID', self.id)
        portlet_ob.pt_edit(text=content, content_type='text/html')

    #overwrite handlers
    def manage_beforeDelete(self, item, container):
        """
        This method is called, when the object is deleted.
        """
        Folder.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.delete_portlet_for_object(item)

    #api
    def get_netrepository_object(self): return self
    def get_netrepository_path(self, p=0): return self.absolute_url(p)
    def get_netsites(self): return self.objectValues(METATYPE_NYNETSITE)
    def get_sites(self):
        """ """
        r = []
        ra = r.append
        for netsite in self.objectValues(METATYPE_NYNETSITE):
            ra({'url': netsite.url, 'title': netsite.title, 'langs': netsite.langs})
        return r

    def search_channels(self, q='', l='', t=''):
        #search channels
        lang = self.gl_get_selected_language()
        if q == '': q = None
        if l == '': l = None
        if t == '': t = None
        return self.query_objects_ex(meta_type=METATYPE_NYNETCHANNEL, q=q, lang=lang, path='/'.join(self.getPhysicalPath()), language=l, type=t)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', REQUEST=None):
        """ """
        lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', lang=None, REQUEST=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'deleteObjects')
    def deleteObjects(self, ids=None, REQUEST=None):
        """ """
        if ids is None: ids = []
        else: ids = self.utConvertToList(ids)
        try: self.manage_delObjects(ids)
        except: self.setSessionErrors(['Error while deleting data.'])
        else: self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/netrepository_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/netrepository_index', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/netrepository_edit', globals())

    security.declareProtected(view, 'search_html')
    search_html = PageTemplateFile('zpt/netrepository_search', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'netsite_add_html')
    netsite_add_html = PageTemplateFile('zpt/netsite_add', globals())

InitializeClass(NyNetRepository)
