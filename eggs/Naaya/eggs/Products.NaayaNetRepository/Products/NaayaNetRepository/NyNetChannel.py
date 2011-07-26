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
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyFeed import NyFeed
from Products.Naaya.constants import *
from naaya.i18n.LocalPropertyManager import LocalPropertyManager, LocalProperty

manage_addNyNetChannel_html = PageTemplateFile('zpt/netchannel_manage_add', globals())
def addNyNetChannel(self, id='', title='', description='', url='', language=None,
    type=None, manual=1, lang=None, REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYNETCHANNEL + self.utGenRandomId(6)
    try: manual = abs(int(manual))
    except: manual = 0
    if lang is None: lang = self.gl_get_selected_language()
    ob = NyNetChannel(id, title, description, url, language, type, manual, lang)
    self.gl_add_languages(ob)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.submitThis()
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'manage_addNyNetChannel_html' or l_referer.find('manage_addNyNetChannel_html') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'netchannel_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.getSitePath())

class NyNetChannel(NyAttributes, LocalPropertyManager, NyItem, NyFeed):
    """ """

    meta_type = METATYPE_NYNETCHANNEL
    icon = 'misc_/NaayaNetRepository/NyNetChannel.gif'

    manage_options = (
        (
            {'label' : 'Properties', 'action' : 'manage_edit_html'},
        )
        +
        NyItem.manage_options
    )

    security = ClassSecurityInfo()

    title = LocalProperty('title')
    description = LocalProperty('description')

    def __init__(self, id, title, description, url, language, type, manual, lang):
        """ """
        self.id = id
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self.url = url
        self.language = language
        self.type = type
        self.manual = manual
        NyFeed.__dict__['__init__'](self)

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self.getLocalProperty('title', lang),
            self.getLocalProperty('description', lang)])

    #api
    def get_netchannel_object(self): return self
    def get_netchannel_path(self, p=0): return self.absolute_url(p)

    def get_feed_url(self):
        #method from NyFeed
        return self.url

    def set_new_feed_url(self, new_url):
        #method from NyFeed
        self.url = new_url
        self._p_changed = 1

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', url='', language=None,
        type=None, REQUEST=None):
        """ """
        lang = self.gl_get_selected_language()
        if language is None: language = lang
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self.url = url
        self.language = language
        self.type = type
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', url='', language=None, type=None,
        lang=None, REQUEST=None):
        """ """
        if lang is None: lang = self.gl_get_selected_language()
        if language is None: language = lang
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self.url = url
        self.language = language
        self.type = type
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'update_netchannel')
    def update_netchannel(self, REQUEST=None):
        """ """
        self.harvest_feed()
        if REQUEST:
            if self.get_feed_bozo_exception() is not None: self.setSessionErrors([self.get_feed_bozo_exception()])
            else: self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/netchannel_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/netchannel_index', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/netchannel_edit', globals())

InitializeClass(NyNetChannel)
