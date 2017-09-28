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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyFeed import NyFeed
from Products.Naaya.constants import *
from Products.NaayaCore.managers.xmlrpc_tool import XMLRPCConnector
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty
import NyNetChannel

manage_addNyNetSite_html = PageTemplateFile('zpt/netsite_manage_add', globals())
def addNyNetSite(self, id='', title='', description='', url='', lang=None, REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYNETSITE + self.utGenRandomId(6)
    if url.endswith('/'): url = url[:-1]
    if lang is None: lang = self.gl_get_selected_language()
    ob = NyNetSite(id, title, description, url, lang)
    self.gl_add_languages(ob)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.submitThis()
    #update search capabilities
    ob.update_search_capabilities()
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'manage_addNyNetSite_html' or l_referer.find('manage_addNyNetSite_html') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'netsite_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.getSitePath())

class NyNetSite(NyAttributes, LocalPropertyManager, NyContainer, NyFeed):
    """ """

    meta_type = METATYPE_NYNETSITE
    icon = 'misc_/NaayaNetRepository/NyNetSite.gif'

    manage_options = (
        NyContainer.manage_options[0:2]
        +
        (
            {'label' : 'Properties', 'action' : 'manage_edit_html'},
        )
        +
        NyContainer.manage_options[3:8]
    )

    meta_types = (
        {'name': METATYPE_NYNETCHANNEL, 'action': 'manage_addNyNetChannel_html'},
    )
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'manage_addNyNetChannel_html')
    manage_addNyNetChannel_html = NyNetChannel.manage_addNyNetChannel_html

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'addNyNetChannel')
    addNyNetChannel = NyNetChannel.addNyNetChannel

    title = LocalProperty('title')
    description = LocalProperty('description')

    def __init__(self, id, title, description, url, lang):
        """ """
        self.id = id
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self.url = url
        self.langs = []
        NyFeed.__dict__['__init__'](self)

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self.getLocalProperty('title', lang),
            self.getLocalProperty('description', lang)])

    #api
    def get_netsite_object(self): return self
    def get_netsite_path(self, p=0): return self.absolute_url(p)
    def get_netchannels(self): return self.objectValues(METATYPE_NYNETCHANNEL)

    def get_netsite_langs(self):
        #returns a comma separated string with languages labels
        try: return ', '.join(map(self.gl_get_language_name, self.langs))
        except: return ''

    def get_feed_url(self):
        #method from NyFeed
        return '%s/localchannels_rdf' % self.url

    def set_new_feed_url(self, new_url):
        #method from NyFeed
        pass

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', url='', REQUEST=None):
        """ """
        if url.endswith('/'): url = url[:-1]
        lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self.url = url
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', url='', lang=None, REQUEST=None):
        """ """
        if url.endswith('/'): url = url[:-1]
        if lang is None: lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self.url = url
        self._p_changed = 1
        self.recatalogNyObject(self)
        #update search capabilities
        self.update_search_capabilities()
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'deleteObjects')
    def deleteObjects(self, ids=None, REQUEST=None):
        """ """
        if ids is None: ids = []
        else: ids = self.utConvertToList(ids)
        try: self.manage_delObjects(ids)
        except: error = 1
        else: error = 0
        if REQUEST:
            if error: self.setSessionErrors(['Error while deleting data.'])
            else: self.setSessionInfo(['Item(s) deleted.'])
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'update_netsite')
    def update_netsite(self, REQUEST=None):
        """ harvest and create channels """
        self.harvest_feed()
        if self.get_feed_bozo_exception() is not None:
            #some error occurred
            self.setSessionErrors([self.get_feed_bozo_exception()])
        else:
            #no errors
            #remove old channels
            self.deleteObjects([x.id for x in self.objectValues() if x.manual==0])
            #add channels
            for x in self.get_feed_items():
                id = PREFIX_NYNETCHANNEL + self.utGenRandomId(6)
                language, type, description, lang = None, None, '', None
                if x.has_key('dc_description'): description = x['dc_description']
                if x.has_key('language'): language = x['language'].encode('utf-8')
                elif x.has_key('dc_language'): language = x['dc_language'].encode('utf-8')
                if x.has_key('type'): type = x['type'].encode('utf-8')
                elif x.has_key('dc_type'): type = x['dc_type'].encode('utf-8')
                #choose which language for the content
                #channel language if channel language is in the list of languages
                #selected language otherwise
                if language is not None:
                    if language in self.gl_get_languages():
                        lang = language
                #create channel
                self.addNyNetChannel(id, x['title'], description, x['link'].encode('utf-8'),
                    language, type, 0, lang)
                #harvest channel
                self._getOb(id).update_netchannel()
                #update search capabilities
                self.update_search_capabilities()
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'update_search_capabilities')
    def update_search_capabilities(self, REQUEST=None):
        """ """
        msg, err, res = '', '', None
        xconn = XMLRPCConnector(self.get_http_proxy())
        res = xconn(self.url, 'external_search_capabilities')
        if res is None:
            err = 'Cannot connect to the given URL.'
            if not hasattr(self, 'langs'):
                #update script for sites that don't have yet the 'langs' property set
                self.langs = []
                self._p_changed = 1
        else:
            self.langs = res
            self._p_changed = 1
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '': self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/netsite_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/netsite_index', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/netsite_edit', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'netchannel_add_html')
    netchannel_add_html = PageTemplateFile('zpt/netchannel_add', globals())

InitializeClass(NyNetSite)
