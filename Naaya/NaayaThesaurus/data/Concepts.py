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
from Products.NaayaThesaurus.parsers.concept_parser     import concept_parser


manage_addConcepts_html = PageTemplateFile('%s/zpt/Concepts/add' % NAAYATHESAURUS_PATH, globals())

def manage_addConcepts(self, id='', title='', REQUEST=None):
    """ adds a new Concepts object """
    ob = Concepts(id, title)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class Concepts(SimpleItem, session_manager):
    """ Concepts """

    meta_type = CONCEPTS_METATYPE
    product_name = NAAYATHESAURUS_PRODUCT_NAME
    icon = 'misc_/NaayaThesaurus/concepts.gif'

    manage_options = (
        {'label':'Properties',      'action':'properties_html'},
        {'label':'Management',      'action':'concepts_html'},
        {'label':'Import',   'action':'import_html'},
        {'label':'Statistics',      'action':'statistics_html'},
        {'label':'Undo',            'action':'manage_UndoForm'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id =         id
        self.title =      title
        self.concepts =   PersistentMapping()


    #basic properties
    security.declareProtected(view_management_screens, 'manageBasicProperties')
    def manageBasicProperties(self, title='', REQUEST=None):
        """ manage basic properties for Concepts """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans('Saved changes.')
            return REQUEST.RESPONSE.redirect('properties_html')


    #concepts management
    def __add_concept(self, concept_id):
        #create a new item
        item = ConceptItem(concept_id)
        self.concepts[concept_id] = item
        self.catalog.CatalogObject(item)

    def __update_concept(self, concept_id, old_concept_id):
        #modify an item
        item = self.concepts.get(old_concept_id)
        if item is not None:
            self.__delete_concept(old_concept_id)
        self.__add_concept(concept_id)

    def __delete_concept(self, ids):
        #delete 1 or more items
        ids = th_utils().utConvertToList(ids)
        collection = self.get_concepts()

        for id in ids:
            self.catalog.UncatalogObject(collection[id])
            del collection[id]


    #concept constraints
    security.declareProtected(view_management_screens, 'getIdsList')
    def getIdsList(self, ids, all=0):
        """ """
        if all: return self.concepts.keys()
        return th_utils().getIdsList(ids)


    #concepts getters
    def get_concepts(self):
        #get all concepts
        return self.concepts

    def get_concepts_sorted(self):
        #get all concepts sorted
        return th_utils().utSortObjsListByAttr(self.concepts.values(), 'concept_id', 0)

    def get_concept_by_id(self, concept_id):
        #get an item
        try:    return self.concepts[concept_id]
        except: return None

    def get_concept_item_data(self, concept_id):
        #get an item data
        item = self.get_concept_by_id(concept_id)
        if item is not None:
            return ['update', item.concept_id]
        else:
            return ['add', '']


    #concepts api
    security.declareProtected(view_management_screens, 'manage_add_concept')
    def manage_add_concept(self, concept_id='', REQUEST=None):
        """ manage concepts """
        if not concept_id: concept_id = th_utils().utGenRandomId()
        self.__add_concept(concept_id)
        if REQUEST:
            self.setSessionInfoTrans('Record added.')
            REQUEST.RESPONSE.redirect('concepts_html')

    security.declareProtected(view_management_screens, 'manage_update_concept')
    def manage_update_concept(self, concept_id='', old_concept_id='', REQUEST=None):
        """ update concept """
        self.__update_concept(concept_id, old_concept_id)
        if REQUEST:
            self.setSessionInfoTrans('Record updated.')
            REQUEST.RESPONSE.redirect('concepts_html')

    security.declareProtected(view_management_screens, 'manage_delete_concepts')
    def manage_delete_concepts(self, ids=[], delete_all='', REQUEST=None):
        """ delete concepts """
        del_count = 0
        #TODO: uncomment when Groups will be implemented
#        if delete_all:  ids = self.getIdsList(ids, 1)
#        else:           ids = self.getIdsList(ids)
        if delete_all:  ids = self.getIdsList(ids, 1)
        ids = th_utils().utConvertToList(ids)
        self.__delete_concept(ids)

        #delete all related data
        for concept_id in ids:
            #delete all related terms
            query = [('meta_type',TERM_ITEM_METATYPE),
                     ('concept_id',concept_id)]
            term_list = self.catalog.searchCatalog(query)
            term_folder = self.getTermsFolder()
            for term_ob in term_list:
                term_folder.manage_delete_terms(['%s###%s' % (term_ob.concept_id, term_ob.langcode)])
                del_count += 1

            #delete all related definitions
            query = [('meta_type',DEFINITION_ITEM_METATYPE),
                     ('concept_id',concept_id)]
            def_list = self.catalog.searchCatalog(query)
            def_folder = self.getDefinitionsFolder()
            for def_ob in def_list:
                def_folder.manage_delete_definitions(['%s###%s' % (def_ob.concept_id, def_ob.langcode)])
                del_count += 1

            #delete all related altterms
            query = [('meta_type',ALTTERM_ITEM_METATYPE),
                     ('concept_id',concept_id)]
            alt_list = self.catalog.searchCatalog(query)
            alt_folder = self.getAltTermsFolder()
            for alt_ob in alt_list:
                alt_folder.manage_delete_altterms(['%s###%s' % (alt_ob.concept_id, alt_ob.langcode)])
                del_count += 1

            #delete all related scopes
            query = [('meta_type',SCOPE_ITEM_METATYPE),
                     ('concept_id',concept_id)]
            scope_list = self.catalog.searchCatalog(query)
            scope_folder = self.getScopeNotesFolder()
            for scope_ob in scope_list:
                scope_folder.manage_delete_scopes(['%s###%s' % (scope_ob.concept_id, scope_ob.langcode)])
                del_count += 1

            #delete all related theme relations
            query = [('meta_type',THEME_RELATION_ITEM_METATYPE),
                     ('concept_id',concept_id)]
            threl_list = self.catalog.searchCatalog(query)
            threl_folder = self.getThemeRelationsFolder()
            for threl_ob in threl_list:
                threl_folder.manage_delete_threlations(['%s###%s' % (threl_ob.concept_id, threl_ob.theme_id)])
                del_count += 1

            #delete all related concept relations
            query = [('meta_type',CONCEPT_RELATION_ITEM_METATYPE),
                     ('concept_id',concept_id)]
            cprel_list = self.catalog.searchCatalog(query)
            cprel_folder = self.getConceptRelationsFolder()
            for cprel_ob in cprel_list:
                cprel_folder.manage_delete_relations(['%s###%s###%s' % (cprel_ob.concept_id, cprel_ob.relation_id, cprel_ob.relation_type)])
                del_count += 1

            query = [('meta_type',CONCEPT_RELATION_ITEM_METATYPE),
                     ('relation_id',concept_id)]
            cprel_list = self.catalog.searchCatalog(query)
            cprel_folder = self.getConceptRelationsFolder()
            for cprel_ob in cprel_list:
                cprel_folder.manage_delete_relations(['%s###%s###%s' % (cprel_ob.concept_id, cprel_ob.relation_id, cprel_ob.relation_type)])
                del_count += 1

        if REQUEST:
            self.setSessionInfoTrans('Selected records deleted.',
                ('${del_count} related records were deleted.', {'del_count': del_count}, ))
            REQUEST.RESPONSE.redirect('concepts_html')

    security.declareProtected(view_management_screens, 'getConceptItemData')
    def getConceptItemData(self):
        """ return a concept based on its ID """
        return self.get_concept_item_data(self.REQUEST.get('concept_id', None))


    #import related
    def skos_import(self, file, REQUEST=None):
        """ """
        parser = concept_parser()

        #parse the SKOS information
        chandler = parser.parseHeader(file)

        if chandler is None:
            if REQUEST:
                self.setSessionErrorsTrans('Parsing error. The file could not be parsed.')
                return REQUEST.RESPONSE.redirect('import_html')

        #get data
        concept_info = chandler.getConcepts()
        theme_relation_info = chandler.getThemes()

        #info
        count_concepts = 0
        count_themes_rel = 0

        #set Concepts
        for id, data in concept_info.items():
            concept_id = data['concept_id'].encode('utf-8').split('/')[-1]
            if concept_id != '':
                count_concepts += 1
                self.__add_concept(concept_id)

        #set ThemeRelations
        for id, data in theme_relation_info.items():
            concept_id = data['concept_id'].encode('utf-8').split('/')[-1]
            theme_id = data['theme_id'].encode('utf-8').split('/')[-1]
            if concept_id and theme_id:
                count_themes_rel += 1
                theme_relations_folder = self.getThemeRelationsFolder()
                theme_relations_folder.manage_add_threlation(concept_id, theme_id)

        if REQUEST:
            self.setSessionInfoTrans(['File imported successfully.',
                ('Concepts added: ${count_concepts}', {'count_concepts': count_concepts}, ),
                ('ThemeRelations added: ${count_themes_rel}', {'count_themes_rel': count_themes_rel}, )])
            return REQUEST.RESPONSE.redirect('import_html')


    #management tabs
    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =       PageTemplateFile("%s/zpt/Concepts/properties" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'concepts_html')
    concepts_html =       PageTemplateFile("%s/zpt/Concepts/concepts" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'statistics_html')
    statistics_html =       PageTemplateFile("%s/zpt/Concepts/statistics" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'import_html')
    import_html =           PageTemplateFile("%s/zpt/Concepts/import" % NAAYATHESAURUS_PATH, globals())

InitializeClass(Concepts)


class ConceptItem:
    """ ConceptItem """

    meta_type = CONCEPT_ITEM_METATYPE

    def __init__(self, concept_id):
        """ constructor """
        self.concept_id =     concept_id

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(ConceptItem)
