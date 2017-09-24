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
from Products.NaayaThesaurus.constants          import *
from Products.NaayaThesaurus.utils              import th_utils
from Products.NaayaThesaurus.session_manager    import session_manager

manage_addDefinitions_html = PageTemplateFile('%s/zpt/Definitions/add' % NAAYATHESAURUS_PATH, globals())

def manage_addDefinitions(self, id='', title='', REQUEST=None):
    """ adds a new Definitions object """
    ob = Definitions(id, title)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class Definitions(SimpleItem, session_manager):
    """ Definitions """

    meta_type = DEFINITIONS_METATYPE
    product_name = NAAYATHESAURUS_PRODUCT_NAME
    icon = 'misc_/NaayaThesaurus/definitions.gif'

    manage_options = (
        {'label':'Properties',      'action':'properties_html'},
        {'label':'Management',      'action':'definitions_html'},
        {'label':'Statistics',      'action':'statistics_html'},
        {'label':'Undo',            'action':'manage_UndoForm'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id =           id
        self.title =        title
        self.definitions =  PersistentMapping()


    #basic properties
    security.declareProtected(view_management_screens, 'manageBasicProperties')
    def manageBasicProperties(self, title='', REQUEST=None):
        """ manage basic properties for Definitions """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans('Saved changes.')
            return REQUEST.RESPONSE.redirect('properties_html')


    #definitions management
    def __add_definition(self, concept_id, langcode, definition, source_id):
        #create a new item
        item = DefinitionItem(concept_id, langcode, definition, source_id)
        self.definitions[(concept_id, langcode)] = item
        self.catalog.CatalogObject(item)

    def __update_definition(self, concept_id, old_concept_id, langcode, old_langcode,
                          definition, source_id):
        #modify an item
        item = self.definitions.get((old_concept_id, old_langcode))
        if item is not None:
            self.__delete_definition((old_concept_id, old_langcode))
        self.__add_definition(concept_id, langcode, definition, source_id)

    security.declareProtected(view_management_screens, 'update_source_id')
    def update_source_id(self, concept_id, langcode, source_id):
        """ update the source_id list """
        definition_ob = self.get_definition_by_id((concept_id, langcode))
        if definition_ob.source_id: upd_source_id = "%s %s" % (definition_ob.source_id, source_id)
        else:                       upd_source_id = source_id
        self.__update_definition(concept_id, concept_id, langcode, langcode, definition_ob.definition, upd_source_id)

    def __delete_definition(self, ids):
        #delete 1 or more items
        if type(ids) != type((1,1)):
            ids = th_utils().utConvertToList(ids)
        else:
            ids = [ids]
        collection = self.get_definitions()

        for id in ids:
            self.catalog.UncatalogObject(collection[id])
            del collection[id]


    #definition constraints
    security.declareProtected(view_management_screens, 'checkDefinition')
    def checkDefinition(self, concept_id):
        """ """
        if self.getConceptsFolder().get_concept_by_id(concept_id):
            return 1
        return 0

    security.declareProtected(view_management_screens, 'getIdsList')
    def getIdsList(self, ids, all=0):
        """ """
        if all: return self.definitions.keys()
        return th_utils().getIdsList(ids)


    #definitions getters
    def get_definitions(self):
        #get all definitions
        return self.definitions

    def get_definitions_sorted(self):
        #get all definitions sorted
        return th_utils().utSortObjsListByAttr(self.definitions.values(), 'concept_id', 0)

    def get_definition_by_id(self, id):
        #get an item
        try:    return self.definitions[id]
        except: return None

    def get_definition_item_data(self, concept_id, langcode, orig_concept_id, orig_langcode, definition, source_id):
        #get an item data
        item = self.get_definition_by_id((orig_concept_id, orig_langcode))
        if item is not None:
            if definition is None:
                definition = item.definition
            if source_id is None:
                source_id = item.source_id
            return ['update', concept_id, langcode, definition, source_id, orig_concept_id, orig_langcode]
        else:
            return ['add', concept_id, langcode, definition, source_id, '', '']


    #definitions api
    security.declareProtected(view_management_screens, 'manage_add_definition')
    def manage_add_definition(self, concept_id='', langcode='', definition='', source_id='', REQUEST=None):
        """ manage definitions """
        err = 0
        if self.checkDefinition(concept_id):
            self.__add_definition(concept_id, langcode, definition, source_id)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionLangcode(langcode)
                self.setSessionDefinition(definition)
                self.setSessionSourceId(source_id)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
            else:
                self.setSessionInfoTrans('Record added.')
            REQUEST.RESPONSE.redirect('definitions_html')

    security.declareProtected(view_management_screens, 'manage_update_definition')
    def manage_update_definition(self, concept_id='', old_concept_id='', langcode='', old_langcode='',
                                 definition='', source_id='', REQUEST=None):
        """ update definition """
        err = 0
        if self.checkDefinition(concept_id):
            self.__update_definition(concept_id, old_concept_id, langcode, old_langcode, definition, source_id)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionLangcode(langcode)
                self.setSessionDefinition(definition)
                self.setSessionSourceId(source_id)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
                REQUEST.RESPONSE.redirect('definitions_html?concept_id=%s&amp;langcode=%s' % (old_concept_id, old_langcode))
            else:
                self.setSessionInfoTrans('Record updated.')
                REQUEST.RESPONSE.redirect('definitions_html')

    security.declareProtected(view_management_screens, 'manage_delete_definitions')
    def manage_delete_definitions(self, ids=[], delete_all='', REQUEST=None):
        """ delete definitions """
        if delete_all:  ids = self.getIdsList(ids, 1)
        else:           ids = self.getIdsList(ids)
        self.__delete_definition(ids)

        if REQUEST:
            self.setSessionInfoTrans('Selected records deleted.')
            REQUEST.RESPONSE.redirect('definitions_html')

    security.declareProtected(view_management_screens, 'getDefinitionItemData')
    def getDefinitionItemData(self):
        """ return a definition based on its ID """
        if self.isSessionConceptId():
            concept_id =        self.getSessionConceptId()
            langcode =          self.getSessionLangcode()
            definition =        self.getSessionDefinition()
            source_id =         self.getSessionSourceId()
            orig_concept_id =   self.REQUEST.get('concept_id', None)
            orig_langcode =     self.REQUEST.get('langcode', None)
        else:
            concept_id =        self.REQUEST.get('concept_id', self.getSessionConceptId())
            langcode =          self.REQUEST.get('langcode', self.getSessionLangcode())
            definition =        self.getSessionDefinition()
            source_id =         self.getSessionSourceId()
            orig_concept_id =   concept_id
            orig_langcode =     langcode

        self.delSessionConceptId()
        self.delSessionLangcode()
        self.delSessionDefinition()
        self.delSessionSourceId()
        return self.get_definition_item_data(concept_id, langcode, orig_concept_id, orig_langcode, definition, source_id)


        return self.get_definition_item_data(self.REQUEST.get('concept_id', None), self.REQUEST.get('langcode', None))


    #statistics
    def getAllDef(self):
        query = [('meta_type',DEFINITION_ITEM_METATYPE)]
        return self.catalog.searchCatalog(query)

    def getDefNumber(self):
        return len(self.getAllDef())

    def getDefTransNumber(self):
        results = {}
        for def_ob in self.getAllDef():
            try:    tr_count = results[def_ob.langcode][0]
            except: tr_count = 0
            tr_count += 1

            try:    src_count = results[def_ob.langcode][1]
            except: src_count = 0
            if def_ob.source_id: src_count += 1

            results[def_ob.langcode] = (tr_count, src_count)
        return results

    def getDefWithSource(self):
        count = 0
        for def_ob in self.getAllDef():
            if len(def_ob.source_id): count += 1
        return count

    def getEmptyDefs(self):
        empty_count = 0
        for def_ob in self.getAllDef():
            if not def_ob.definition:
                empty_count += 1
        return empty_count


    #management tabs
    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =       PageTemplateFile("%s/zpt/Definitions/properties" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'definitions_html')
    definitions_html =        PageTemplateFile("%s/zpt/Definitions/definitions" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'statistics_html')
    statistics_html =   PageTemplateFile("%s/zpt/Definitions/statistics" % NAAYATHESAURUS_PATH, globals())

InitializeClass(Definitions)


class DefinitionItem:
    """ DefinitionItem """

    meta_type = DEFINITION_ITEM_METATYPE

    def __init__(self, concept_id, langcode, definition, source_id):
        """ constructor """
        self.concept_id =   concept_id
        self.langcode =     langcode
        self.definition =   definition
        self.source_id =    source_id

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(DefinitionItem)