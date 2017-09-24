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

#Python imports

#Zope imports
from ZPublisher.HTTPRequest             import record
from Globals                            import InitializeClass
from AccessControl                      import ClassSecurityInfo
from Products.ZCatalog.ZCatalog         import ZCatalog

#Product imports
from constants                      import *
from Products.NaayaThesaurus.utils  import th_utils


def manage_addThesaurusCatalog(self, REQUEST=None):
    """ add a new ThesaurusCatalog object """
    ob = ThesaurusCatalog()
    self._setObject(NAAYATHESAURUS_CATALOG_ID, ob)
    ob = self._getOb(NAAYATHESAURUS_CATALOG_ID)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class ThesaurusCatalog(ZCatalog):
    """ ThesaurusCatalog object"""

    meta_type = THESAURUSCATALOG_METATYPE
    icon = 'misc_/NaayaThesaurus/thesaurus_catalog.gif'

    manage_options = (
        ZCatalog.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id=NAAYATHESAURUS_CATALOG_ID, title= NAAYATHESAURUS_CATALOG_TITLE):
        ZCatalog.__init__(self, id, title)
        self.__generateDefaultIndexes()

    def __generateDefaultIndexes(self):
        available_indexes = self.indexes()
        available_metadata = self.schema()

        #create indexes
        for index in self._getDefaultIndexes():
            if not (index in available_indexes):
                if self._getIndexById(index) == 'TextIndexNG3':
                    p_extras = record()
                    p_extras.default_encoding = 'utf-8'
                    p_extras.splitter_single_chars = 1
                else:
                    p_extras = None
                self.addIndex(index, self._getIndexById(index), p_extras)
            if not (index in available_metadata):
                self.addColumn(index)

    def searchCatalog(self, filters):
        results = []

        #create filter
        criteria = {}
        for item in filters:
            criteria[item[0]] = item[1]

        #get brains list
        try:    results.extend(self(criteria))
        except: results = []

        return results
        #return th_utils().utEliminateDuplicates(results)


    #basic api
    def _getDefaultIndexes(self): return THESAURUS_INDEXES.keys()
    def _getIndexById(self, id):  return THESAURUS_INDEXES[id]

    def ClearCatalog(self):
        """ clear catalog """
        self.manage_catalogClear()

    def BuildCatalogPath(self, p_item):
        """ build a path for items to be added in catalog """
        #create a path for thesaurus objects
        if p_item.meta_type == THEME_ITEM_METATYPE:
            return 'themes/%s/%s' % (p_item.theme_id, p_item.langcode)
        elif p_item.meta_type == CONCEPT_ITEM_METATYPE:
            return 'concepts/%s' % p_item.concept_id
        elif p_item.meta_type == CONCEPT_RELATION_ITEM_METATYPE:
            return 'concept_relations/%s/%s/%s' % (p_item.concept_id, p_item.relation_id, p_item.relation_type)
        elif p_item.meta_type == TERM_ITEM_METATYPE:
            return 'terms/%s/%s' % (p_item.concept_id, p_item.langcode)
        elif p_item.meta_type == ALTTERM_ITEM_METATYPE:
            return 'alt_terms/%s/%s' % (p_item.concept_id, p_item.langcode)
        elif p_item.meta_type == SOURCE_ITEM_METATYPE:
            return 'sources/%s' % p_item.source_id
        elif p_item.meta_type == SCOPE_ITEM_METATYPE:
            return 'scopes/%s/%s' % (p_item.concept_id, p_item.langcode)
        elif p_item.meta_type == DEFINITION_ITEM_METATYPE:
            return 'definitions/%s/%s' % (p_item.concept_id, p_item.langcode)
        elif p_item.meta_type == THEME_RELATION_ITEM_METATYPE:
            return 'theme_relations/%s/%s' % (p_item.concept_id, p_item.theme_id)

    def CatalogObject(self, p_ob):
        """ catalog objects """
        self.catalog_object(p_ob, self.BuildCatalogPath(p_ob))

    def UncatalogObject(self, p_ob):
        """ uncatalog objects """
        if th_utils().utIsListType(p_ob):  map(lambda x, y: x.uncatalog_object(x.BuildCatalogPath(y)), (self,)*len(p_ob), p_ob)
        else:                              self.uncatalog_object(self.BuildCatalogPath(p_ob))

    def RecatalogObject(self, p_ob):
        """ recatalog objects """
        self.UncatalogObject(p_ob)
        self.CatalogObject(p_ob)

    def getTermObj(self, l_brain, REQUEST=None):
        #return a cataloged term object given a 'data_record_id_'
        my_path_list = self.getpath(l_brain.data_record_id_).split('/')

        concept_id = my_path_list[1]
        langcode = my_path_list[2]

        term_folder = self.getTermsFolder()
        return term_folder.get_term_by_id((concept_id, langcode))

InitializeClass(ThesaurusCatalog)
