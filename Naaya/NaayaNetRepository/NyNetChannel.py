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
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from Products.Localizer.LanguageManager import LanguageManager
from Products.EWPublisher.constants import *
from Products.EWPublisher.EWBase.EWAttributes import EWAttributes
from Products.EWPublisher.EWBase.EWItem import EWItem
from Products.EWPublisher.EWBase.EWFeed import EWFeed
from constants import *

manage_addEWNetChannel_html = PageTemplateFile('zpt/EWNetChannel_manage_add', globals())
def addEWNetChannel(self, id='', title='', description='', url='', language=None, type=None, manual=1, REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NETCHANNEL + self.utGenRandomId(6)
    try: manual = abs(int(manual))
    except: manual = 0
    lang = self.get_default_language()
    ob = EWNetChannel(id, title, description, url, language, type, manual, lang)
    for lang_rec in self.get_languages_mapping():
        ob.add_language(lang_rec['code'])
        if lang_rec['default']: ob.manage_changeDefaultLang(lang_rec['code'])
    self._setObject(id, ob)
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'manage_addEWNetChannel_html' or l_referer.find('manage_addEWNetChannel_html') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'netchannel_add_html':
            REQUEST.RESPONSE.redirect('%s/index_html' % self.get_netsite_path())

class EWNetChannel(EWAttributes, LocalPropertyManager, EWItem, EWFeed):
    """ """

    meta_type = METATYPE_EWNETCHANNEL
    icon = 'misc_/EWNetRepository/EWNetChannel.gif'

    manage_options = (
        (
            {'label' : 'Properties', 'action' : 'manage_edit_html'},
        )
        +
        LanguageManager.manage_options
        +
        EWItem.manage_options
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
        EWFeed.__dict__['__init__'](self)

    def objectkeywords(self, lang):
        l_values = [self.getLocalProperty('title', lang), self.getLocalProperty('description', lang)]
        return ' '.join([x.encode('utf-8') for x in l_values])

    #api
    def get_netchannel_object(self): return self
    def get_netchannel_path(self, p=0): return self.absolute_url(p)

    def get_feed_url(self):
        #method from EWFeed
        return self.url

    def set_new_feed_url(self, new_url):
        #method from EWFeed
        self.url = new_url
        self._p_changed = 1

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', url='', language=None, type=None, REQUEST=None):
        """ """
        lang = self.get_default_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self.url = url
        self.language = language
        self.type = type
        self._p_changed = 1
        self.recatalogEWObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    def saveProperties(self, title='', description='', url='', language=None, type=None, lang=None, REQUEST=None):
        """ """
        if lang is None: lang = self.get_default_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self.url = url
        self.language = language
        self.type = type
        self._p_changed = 1
        self.recatalogEWObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    def update_netchannel(self, REQUEST=None):
        """ """
        self.harvest_feed()
        if REQUEST:
            if self.get_feed_bozo_exception() is not None: self.setSessionErrors([self.get_feed_bozo_exception()])
            else: self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/EWNetChannel_manage_edit', globals())

    #site pages
    index_html = PageTemplateFile('zpt/EWNetChannel_index', globals())
    edit_html = PageTemplateFile('zpt/EWNetChannel_edit', globals())

InitializeClass(EWNetChannel)
