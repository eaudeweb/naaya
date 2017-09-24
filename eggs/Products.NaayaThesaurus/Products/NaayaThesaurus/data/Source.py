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
# Ghica Alexandru, Finsiel Romania


# python imports
import string

# Zope imports
from Globals                                    import DTMLFile, InitializeClass
from AccessControl                              import ClassSecurityInfo
from OFS.SimpleItem                             import SimpleItem
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from AccessControl.Permissions                  import view_management_screens, view
from ZODB.PersistentMapping                     import PersistentMapping

# product imports
from Products.NaayaThesaurus.constants  import *
from Products.NaayaThesaurus.utils      import th_utils

manage_addSource_html = PageTemplateFile('%s/zpt/Source/add' % NAAYATHESAURUS_PATH, globals())

def manage_addSource(self, id='', title='', REQUEST=None):
    """ adds a new Source object """
    ob = Source(id, title)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class Source(SimpleItem):
    """ Source """

    meta_type = SOURCE_METATYPE
    product_name = NAAYATHESAURUS_PRODUCT_NAME
    icon = 'misc_/NaayaThesaurus/source.gif'

    manage_options = (
        {'label':'Properties',  'action':'properties_html'},
        {'label':'Management',      'action':'sources_html'},
        {'label':'Statistics',      'action':'statistics_html'},
        {'label':'Undo',        'action':'manage_UndoForm'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id =       id
        self.title =    title
        self.sources =  PersistentMapping()


    #basic properties
    security.declareProtected(view_management_screens, 'manageBasicProperties')
    def manageBasicProperties(self, title='', REQUEST=None):
        """ manage basic properties for Source """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans('Saved changes.')
            return REQUEST.RESPONSE.redirect('properties_html')


    #sources management
    def __add_source(self, source_id, source_name):
        #create a new item
        item = SourceItem(source_id, source_name)
        self.sources[source_id] = item
        self.catalog.CatalogObject(item)

    def __update_source(self, source_id, old_source_id, source_name):
        #modify an item
        item = self.sources.get(old_source_id)
        if item is not None:
            self.__delete_source(old_source_id)
        self.__add_source(source_id, source_name)

    def __delete_source(self, ids):
        #delete 1 or more items
        ids = th_utils().utConvertToList(ids)
        collection = self.get_sources()

        for id in ids:
            self.catalog.UncatalogObject(collection[id])
            del collection[id]


    #source constrints
    security.declareProtected(view_management_screens, 'getIdsList')
    def getIdsList(self, ids, all=0):
        """ """
        if all: return self.sources.keys()
        return th_utils().getIdsList(ids)

    #sources getters
    def get_sources(self):
        #get all sources
        return self.sources

    def get_sources_sorted(self):
        #get all sources sorted
        return th_utils().utSortObjsListByAttr(self.sources.values(), 'source_id', 0)

    def get_source_by_id(self, id):
        #get an item
        try:    return self.sources[id]
        except: return None

    def get_source_item_data(self, id):
        #get an item data
        item = self.get_source_by_id(id)
        if item is not None: 
            return ['update', item.source_id, item.source_name]
        else:
            return ['add', '', '']


    #sources api
    security.declareProtected(view_management_screens, 'manage_add_source')
    def manage_add_source(self, source_id='', source_name='', REQUEST=None):
        """ manage sources """
        if not source_id: source_id = th_utils().utGenRandomId()
        self.__add_source(source_id, source_name)
        if REQUEST:
            self.setSessionInfoTrans('Record added.')
            REQUEST.RESPONSE.redirect('sources_html')

    security.declareProtected(view_management_screens, 'manage_update_source')
    def manage_update_source(self, source_id='', old_source_id='', source_name='', REQUEST=None):
        """ update source """
        self.__update_source(source_id, old_source_id, source_name)
        if REQUEST:
            self.setSessionInfoTrans('Record updated.')
            REQUEST.RESPONSE.redirect('sources_html')

    security.declareProtected(view_management_screens, 'manage_delete_sources')
    def manage_delete_sources(self, ids=[], delete_all='', REQUEST=None):
        """ delete sources """
        if delete_all:  ids = self.getIdsList(ids, 1)
        else:           ids = self.getIdsList(ids)
        self.__delete_source(ids)
        if REQUEST:
            self.setSessionInfoTrans('Selected records deleted.')
            REQUEST.RESPONSE.redirect('sources_html')

    security.declareProtected(view_management_screens, 'getSourceItemData')
    def getSourceItemData(self):
        """ return a source based on its ID """
        return self.get_source_item_data(self.REQUEST.get('source_id', None))


    #statistics
    def getAllSrc(self):
        query = [('meta_type',SOURCE_ITEM_METATYPE)]
        return self.catalog.searchCatalog(query)

    def getSrcNumber(self):
        return len(self.getAllSrc())


    #management tabs
    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =       PageTemplateFile("%s/zpt/Source/properties" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'sources_html')
    sources_html =        PageTemplateFile("%s/zpt/Source/sources" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'statistics_html')
    statistics_html =   PageTemplateFile("%s/zpt/Source/statistics" % NAAYATHESAURUS_PATH, globals())

InitializeClass(Source)


class SourceItem:
    """ SourceItem """

    meta_type = SOURCE_ITEM_METATYPE

    def __init__(self, source_id, source_name):
        """ constructor """
        self.source_id =     source_id
        self.source_name =   source_name

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(SourceItem)