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
from Products.NaayaThesaurus.constants                  import *
from Products.NaayaThesaurus.utils                      import th_utils
from Products.NaayaThesaurus.session_manager            import session_manager
from Products.NaayaThesaurus.parsers.relation_parser    import relation_parser

manage_addConceptRelations_html = PageTemplateFile('%s/zpt/ConceptRelations/add' % NAAYATHESAURUS_PATH, globals())

def manage_addConceptRelations(self, id='', title='', REQUEST=None):
    """ adds a new ConceptRelations object """
    ob = ConceptRelations(id, title)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class ConceptRelations(SimpleItem, session_manager):
    """ ConceptRelations """

    meta_type = CONCEPT_RELATIONS_METATYPE
    product_name = NAAYATHESAURUS_PRODUCT_NAME
    icon = 'misc_/NaayaThesaurus/concept_relations.gif'

    manage_options = (
        {'label':'Properties',      'action':'properties_html'},
        {'label':'Management',      'action':'concept_relations_html'},
        {'label':'Import',   'action':'import_html'},
        {'label':'Statistics',      'action':'statistics_html'},
        {'label':'Undo',            'action':'manage_UndoForm'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id =                   id
        self.title =                title
        self.concept_relations =    PersistentMapping()


    #basic properties
    security.declareProtected(view_management_screens, 'manageBasicProperties')
    def manageBasicProperties(self, title='', REQUEST=None):
        """ manage basic properties for ConceptRelations """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans('Saved changes.')
            return REQUEST.RESPONSE.redirect('properties_html')


    #concept relations management
    def __add_relation(self, concept_id, relation_id, relation_type):
        #create a new item
        item = ConceptRelationsItem(concept_id, relation_id, relation_type)
        self.concept_relations[(concept_id, relation_id, relation_type)] = item
        self.catalog.CatalogObject(item)

    def __update_relation(self, concept_id, old_concept_id, relation_id,
                        old_relation_id, relation_type, old_relation_type):
        #modify an item
        l_old_id = (old_concept_id, old_relation_id, old_relation_type)
        item = self.concept_relations.get(l_old_id)
        if item is not None:
            self.__delete_relation(l_old_id)
        self.__add_relation(concept_id, relation_id, relation_type)

    def __delete_relation(self, ids):
        #delete 1 or more items
        if type(ids) != type((1,1)):
            ids = th_utils().utConvertToList(ids)
        else:
            ids = [ids]
        collection = self.get_relations()

        for id in ids:
            self.catalog.UncatalogObject(collection[id])
            del collection[id]


    #concept relations constraints
    security.declareProtected(view_management_screens, 'checkCpRel')
    def checkCpRel(self, concept_id):
        """ """
        if self.getConceptsFolder().get_concept_by_id(concept_id):
            return 1
        return 0

    security.declareProtected(view_management_screens, 'getIdsList')
    def getIdsList(self, ids, all=0):
        """ """
        if all: return self.concept_relations.keys()
        return th_utils().getIdsList(ids)


    #relations getters
    def get_relations(self):
        #get all relations
        return self.concept_relations

    def get_relations_sorted(self):
        #get all relations sorted
        return th_utils().utSortObjsListByAttr(self.concept_relations.values(), 'concept_id', 0)

    def get_relation_by_id(self, id):
        #get an item
        try:    return self.concept_relations[id]
        except: return None

    def get_relations_item_data(self, concept_id, relation_id, relation_type,
                                orig_concept_id, orig_relation_id, orig_relation_type):
        #get an item data
        item = self.get_relation_by_id((orig_concept_id, orig_relation_id, orig_relation_type))
        if item is not None:
            return ['update', concept_id, relation_id, relation_type,
                    orig_concept_id, orig_relation_id, orig_relation_type]
        else:
            return ['add', concept_id, relation_id, relation_type, '', '', '']


    #concept relations api
    security.declareProtected(view_management_screens, 'manage_add_relation')
    def manage_add_relation(self, concept_id='', relation_id='', relation_type='', REQUEST=None):
        """ manage relations """
        err = 0
        if self.checkCpRel(concept_id) and self.checkCpRel(relation_id):
            self.__add_relation(concept_id, relation_id, relation_type)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionRelationId(relation_id)
                self.setSessionRelationType(relation_type)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
            else:
                self.setSessionInfoTrans('Record added.')
            REQUEST.RESPONSE.redirect('concept_relations_html')

    security.declareProtected(view_management_screens, 'manage_update_relation')
    def manage_update_relation(self, concept_id='', old_concept_id='', relation_id='',
                            old_relation_id='', relation_type='', old_relation_type='', REQUEST=None):
        """ update relation """
        err = 0
        if self.checkCpRel(concept_id) and self.checkCpRel(relation_id):
            self.__update_relation(concept_id, old_concept_id, relation_id,
                                   old_relation_id, relation_type, old_relation_type)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionRelationId(relation_id)
                self.setSessionRelationType(relation_type)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
                REQUEST.RESPONSE.redirect('concept_relations_html?concept_id=%s&amp;relation_id=%s&amp;relation_type=%s'
                                           % (old_concept_id, old_relation_id, old_relation_type))
            else:
                self.setSessionInfoTrans('Record updated.')
                REQUEST.RESPONSE.redirect('concept_relations_html')

    security.declareProtected(view_management_screens, 'manage_delete_relations')
    def manage_delete_relations(self, ids=[], delete_all='', REQUEST=None):
        """ delete relations """
        if delete_all:  ids = self.getIdsList(ids, 1)
        else:           ids = self.getIdsList(ids)
        self.__delete_relation(ids)

        if REQUEST:
            self.setSessionInfoTrans('Selected records deleted.')
            REQUEST.RESPONSE.redirect('concept_relations_html')

    security.declareProtected(view_management_screens, 'getRelationItemData')
    def getRelationItemData(self):
        """ return a relation based on its ID """
        if self.isSessionConceptId():
            concept_id =            self.getSessionConceptId()
            relation_id =           self.getSessionRelationId()
            relation_type =         self.getSessionRelationType()
            orig_concept_id =       self.REQUEST.get('concept_id', None)
            orig_relation_id =      self.REQUEST.get('relation_id', None)
            orig_relation_type =    self.REQUEST.get('relation_type', None)
        else:
            concept_id =            self.REQUEST.get('concept_id', self.getSessionConceptId())
            relation_id =           self.REQUEST.get('relation_id', self.getSessionRelationId())
            relation_type =         self.REQUEST.get('relation_type', self.getSessionRelationType())
            orig_concept_id =       concept_id
            orig_relation_id =      relation_id
            orig_relation_type =    relation_type

        self.delSessionConceptId()
        self.delSessionRelationId()
        self.delSessionRelationType()
        return self.get_relations_item_data(concept_id, relation_id, relation_type,
                                            orig_concept_id, orig_relation_id, orig_relation_type)


    #import related
    def skos_import(self, file, REQUEST=None):
        """ """
        parser = relation_parser()

        #parse the SKOS information
        chandler = parser.parseHeader(file)

        if chandler is None:
            if REQUEST:
                self.setSessionErrorsTrans('Parsing error. The file could not be parsed.')
                return REQUEST.RESPONSE.redirect('import_html')

        #info
        count_rel = 0
        err_list = []

        #set data
        for data in chandler.getBody():
            concept_id = data['concept_id'].encode('utf-8').split('/')[-1]
            relation_id = data['relation_id'].encode('utf-8').split('/')[-1]
            relation_type = data['relation_type']

            if concept_id:
                if self.checkCpRel(concept_id) and self.checkCpRel(relation_id):
                    self.__add_relation(concept_id, relation_id, relation_type)
                    count_rel += 1
                else:
                    if not relation_id:
                        err_list.append(('(${content_id}, None) - relation_id not specified', {'concept_id': concept_id }, ))
                    else:
                        err_list.append(('(${concept_id}, ${relation_id}) - at least one of the concept_id or relation_id does not exist',
                        {'concept_id': concept_id, 'relation_id': relation_id }))
            else:
                err_list.append('None - concept_id not specified')

        if REQUEST:
            self.setSessionInfoTrans(['File imported successfully.',
                ('Translations added: ${count_rel}', {'count_rel': count_rel}, )])
            if err_list:
                self.setSessionErrorsTrans(['Relations not imported (by its (concept_id, relation_id)):', err_list, ])
            return REQUEST.RESPONSE.redirect('import_html')


    #relation type related
    def getRelTypes(self):
        """ """
        return RELATION_TYPES

    def getRelTypesIDs(self):
        """ """
        return self.getRelTypes().keys()

    def getRelTypeByID(self, id):
        """ """
        return self.getRelTypes()[id]


    #statistics
    def getAllConRel(self):
        query = [('meta_type',CONCEPT_RELATION_ITEM_METATYPE)]
        return self.catalog.searchCatalog(query)

    def getConRelNumber(self):
        return len(self.getAllConRel())

    def getRelationsNumber(self):
        results = {}
        for conrel_ob in self.getAllConRel():
            try:    br_count = results[1]
            except: br_count = 0
            try:    nr_count = results[2]
            except: nr_count = 0
            try:    re_count = results[3]
            except: re_count = 0

            if conrel_ob.relation_type == '1':
                results[1] = br_count + 1
            elif conrel_ob.relation_type == '2':
                results[2] = nr_count + 1
            elif conrel_ob.relation_type == '3':
                results[3] = re_count + 1

        return results


    #management tabs
    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =           PageTemplateFile("%s/zpt/ConceptRelations/properties" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'concept_relations_html')
    concept_relations_html =    PageTemplateFile("%s/zpt/ConceptRelations/concept_relations" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'statistics_html')
    statistics_html =           PageTemplateFile("%s/zpt/ConceptRelations/statistics" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'import_html')
    import_html =               PageTemplateFile("%s/zpt/ConceptRelations/import" % NAAYATHESAURUS_PATH, globals())

InitializeClass(ConceptRelations)


class ConceptRelationsItem:
    """ ConceptRelationsItem """

    meta_type = CONCEPT_RELATION_ITEM_METATYPE

    def __init__(self, concept_id, relation_id, relation_type):
        """ constructor """
        self.concept_id =      concept_id
        self.relation_id =     relation_id
        self.relation_type =   relation_type

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(ConceptRelationsItem)
