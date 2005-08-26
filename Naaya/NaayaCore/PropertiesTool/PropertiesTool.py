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
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaCore.managers.search_tool import search_tool

def manage_addPropertiesTool(self, REQUEST=None):
    """ """
    ob = PropertiesTool(ID_PROPERTIESTOOL, TITLE_PROPERTIESTOOL)
    self._setObject(ID_PROPERTIESTOOL, ob)
    self._getOb(ID_PROPERTIESTOOL).loadDefaultData()
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class PropertiesTool(SimpleItem, utils, search_tool):
    """ """

    meta_type = METATYPE_PROPERTIESTOOL
    icon = 'misc_/NaayaCore/PropertiesTool.gif'

    manage_options = (
        (
            {'label': 'Settings', 'action': 'manage_settings_html'},
            {'label': 'Main topics', 'action': 'manage_maintopics_html'},
            {'label': 'Subobjects', 'action': 'manage_subobjects_html'},
            {'label': 'Event types', 'action': 'manage_eventtypes_html'},
            {'label': 'File types', 'action': 'manage_contenttypes_html'},
            {'label': 'Languages', 'action': 'manage_languages_html'},
            {'label': 'Search', 'action': 'manage_search_html'},
        )
        +
        SimpleItem.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        #load default stuff
        pass

    #Internal search
    security.declareProtected(view_management_screens, 'manageInternalSearch')
    def manageInternalSearch(self, search_age=0, results_number=10, REQUEST=None):
        """ Manage the properties for internal search"""
        self.setItemsAge(search_age)
        self.setNumberOfResults(results_number)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_search_html?save=ok')

    def setSearchedItems(self, items):
        """ set the searcheble items list """
        self.searched_items.append(items)

    def getSearchedItems(self):
        """ get the searcheble items list """
        return self.searched_items

    def delSearchedItems(self, item):
        """ delete a searcheble item from the list """
        try: self.searched_items.remove(item)
        except ValueError: pass

    #Main topics
    security.declareProtected(view_management_screens, 'manageMainTopics')
    def manageMainTopics(self, maintopics=None, REQUEST=None):
        """ Update main topics """
        site = self.getSite()
        if maintopics is None: maintopics = []
        else: maintopics = self.utConvertToList(maintopics)
        site.maintopics = maintopics
        site._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_maintopics_html?save=ok')

    #Event types
    security.declareProtected(view_management_screens, 'manageAddEventType')
    def manageAddEventType(self, id='', title='', REQUEST=None):
        """ """
        self.createEventType(id, title)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_eventtypes_html?save=ok')

    security.declareProtected(view_management_screens, 'manageUpdateEventType')
    def manageUpdateEventType(self, id='', title='', REQUEST=None):
        """ """
        self.modifyEventType(id, title)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_eventtypes_html?save=ok')

    security.declareProtected(view_management_screens, 'manageDeleteEventTypes')
    def manageDeleteEventTypes(self, id=[], REQUEST=None):
        """ """
        self.deleteEventType(self.utConvertToList(id))
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_eventtypes_html?save=ok')

    #Content types
    security.declareProtected(view_management_screens, 'manageAddContentType')
    def manageAddContentType(self, id='', title='', picture='', REQUEST=None):
        """ """
        self.createContentType(id, title, picture)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_contenttypes_html?save=ok')

    security.declareProtected(view_management_screens, 'manageUpdateContentType')
    def manageUpdateContentType(self, id='', title='', picture='', REQUEST=None):
        """ """
        self.modifyContentType(id, title, picture)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_contenttypes_html?save=ok')

    security.declareProtected(view_management_screens, 'manageDeleteContentTypes')
    def manageDeleteContentTypes(self, id=[], REQUEST=None):
        """ """
        self.deleteContentType(self.utConvertToList(id))
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_contenttypes_html?save=ok')

    #Subobjects
    security.declareProtected(view_management_screens, 'manageSubobjects')
    def manageSubobjects(self, subobjects=None, ny_subobjects=None, REQUEST=None):
        """ Update the additional meta types for all objects """
        if subobjects is None: subobjects = []
        else: subobjects = self.utConvertToList(subobjects)
        if ny_subobjects is None: ny_subobjects = []
        else: ny_subobjects = self.utConvertToList(ny_subobjects)
        site = self.getSite()
        site.adt_meta_types = subobjects
        site.adt_meta_types.extend(ny_subobjects)
        site._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_subobjects_html?save=ok')

    #Languages
    security.declareProtected(view_management_screens, 'manage_addLanguage')
    def manage_addLanguage(self, language, REQUEST=None):
        """ """
        self.getSite().gl_add_site_language(language)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_languages_html?save=ok')

    security.declareProtected(view_management_screens, 'manage_delLanguages')
    def manage_delLanguages(self, languages, REQUEST=None):
        """ """
        self.getSite().gl_del_site_languages(languages)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_languages_html?save=ok')

    security.declareProtected(view_management_screens, 'manage_changeDefaultLang')
    def manage_changeDefaultLang(self, language, REQUEST=None):
        """ """
        self.getSite().gl_change_site_defaultlang(language)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_languages_html?save=ok')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_subobjects_html')
    manage_subobjects_html = PageTemplateFile('zpt/properties_subobjects', globals())

    security.declareProtected(view_management_screens, 'manage_settings_html')
    manage_settings_html = PageTemplateFile('zpt/properties_settings', globals())

    security.declareProtected(view_management_screens, 'manage_maintopics_html')
    manage_maintopics_html = PageTemplateFile('zpt/properties_maintopics', globals())

    security.declareProtected(view_management_screens, 'manage_eventtypes_html')
    manage_eventtypes_html = PageTemplateFile('zpt/properties_eventtypes', globals())

    security.declareProtected(view_management_screens, 'manage_contenttypes_html')
    manage_contenttypes_html = PageTemplateFile('zpt/properties_contenttypes', globals())

    security.declareProtected(view_management_screens, 'manage_languages_html')
    manage_languages_html = PageTemplateFile('zpt/properties_languages', globals())

    security.declareProtected(view_management_screens, 'manage_search_html')
    manage_search_html = PageTemplateFile('zpt/properties_search', globals())

InitializeClass(PropertiesTool)
