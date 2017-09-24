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
from Products.NaayaThesaurus.utils                      import th_utils
from Products.NaayaThesaurus.constants                  import *
from Products.NaayaThesaurus.session_manager            import session_manager
from Products.NaayaThesaurus.parsers.concept_parser     import concept_parser


manage_addThemeRelations_html = PageTemplateFile('%s/zpt/ThemeRelations/add' % NAAYATHESAURUS_PATH, globals())

def manage_addThemeRelations(self, id='', title='', REQUEST=None):
    """ adds a new ThemeRelations object """
    ob = ThemeRelations(id, title)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class ThemeRelations(SimpleItem, session_manager):
    """ ThemeRelations """

    meta_type = THEME_RELATION_METATYPE
    product_name = NAAYATHESAURUS_PRODUCT_NAME
    icon = 'misc_/NaayaThesaurus/theme_relations.gif'

    manage_options = (
        {'label':'Properties',      'action':'properties_html'},
        {'label':'Management',      'action':'theme_relations_html'},
        {'label':'Statistics',      'action':'statistics_html'},
        {'label':'Undo',            'action':'manage_UndoForm'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id =              id
        self.title =           title
        self.theme_relations = PersistentMapping()


    #basic properties
    security.declareProtected(view_management_screens, 'manageBasicProperties')
    def manageBasicProperties(self, title='', REQUEST=None):
        """ manage basic properties for ThemeRelations """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans('Saved changes.')
            return REQUEST.RESPONSE.redirect('properties_html')


    #theme relations management
    def __add_threlation(self, concept_id, theme_id):
        #create a new item
        item = ThemeRelationItem(concept_id, theme_id)
        self.theme_relations[(concept_id, theme_id)] = item
        self.catalog.CatalogObject(item)

    def __update_threlation(self, concept_id, old_concept_id, theme_id, old_theme_id):
        #modify an item
        item = self.theme_relations.get((old_concept_id, old_theme_id))
        if item is not None:
            self.__delete_threlation((old_concept_id, old_theme_id))
        self.__add_threlation(concept_id, theme_id)

    def __delete_threlation(self, ids):
        #delete 1 or more items
        if type(ids) != type((1,1)):
            ids = th_utils().utConvertToList(ids)
        else:
            ids = [ids]
        collection = self.get_threlations()

        for id in ids:
            self.catalog.UncatalogObject(collection[id])
            del collection[id]


    #theme relations constraints
    security.declareProtected(view_management_screens, 'checkThRel')
    def checkThRel(self, concept_id):
        """ """
        if self.getConceptsFolder().get_concept_by_id(concept_id):
            return 1
        return 0

    security.declareProtected(view_management_screens, 'getIdsList')
    def getIdsList(self, ids, all=0):
        """ """
        if all: return self.theme_relations.keys()
        return th_utils().getIdsList(ids)

    security.declareProtected(view_management_screens, 'infoOnDelete')
    def infoOnDelete(self, ids, all=0):
        """ """
        results = []
        dic_cp = {}
        lst_cp = []

        for rel_id in self.getIdsList(ids, all):
            rel_ob = self.get_threlation_by_id(rel_id)
            try:    lst_cp = dic_cp[rel_ob.concept_id]
            except: lst_cp= []
            lst_cp.append(rel_ob)
            dic_cp[rel_ob.concept_id] = lst_cp
            results.append(rel_ob)

        for concept_id in dic_cp.keys():
            query = [('meta_type',THEME_RELATION_ITEM_METATYPE),
                     ('concept_id',concept_id)]
            if len(dic_cp[concept_id]) == len(self.catalog.searchCatalog(query)):
                dic_cp[concept_id] = 1
            else:
                dic_cp[concept_id] = 0

        return (results, dic_cp)


    #theme relations getters
    def get_threlations(self):
        #get all theme relations
        return self.theme_relations

    def get_threlations_sorted(self):
        #get all theme relations sorted
        return th_utils().utSortObjsListByAttr(self.theme_relations.values(), 'concept_id', 0)

    def get_threlation_by_id(self, id):
        #get an item
        try:    return self.theme_relations[id]
        except: return None

    def get_threlation_item_data(self, concept_id, theme_id, orig_concept_id, orig_theme_id):
        #get an item data
        item = self.get_threlation_by_id((orig_concept_id, orig_theme_id))
        if item is not None:
            return ['update', concept_id, theme_id, orig_concept_id, orig_theme_id]
        else:
            return ['add', concept_id, theme_id, '', '']


    #themes api
    security.declareProtected(view_management_screens, 'manage_add_threlation')
    def manage_add_threlation(self, concept_id='', theme_id='', REQUEST=None):
        """ manage theme relations """
        err = 0
        if self.checkThRel(concept_id):
            self.__add_threlation(concept_id, theme_id)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionThemeId(theme_id)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
            else:
                self.setSessionInfoTrans('Record added.')
            REQUEST.RESPONSE.redirect('theme_relations_html')

    security.declareProtected(view_management_screens, 'manage_update_threlation')
    def manage_update_threlation(self, concept_id='', old_concept_id='', theme_id='', old_theme_id='', REQUEST=None):
        """ update theme relation """
        err = 0
        if self.checkThRel(concept_id):
            self.__update_threlation(concept_id, old_concept_id, theme_id, old_theme_id)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionThemeId(theme_id)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
                REQUEST.RESPONSE.redirect('theme_relations_html?concept_id=%s&amp;theme_id=%s' % (old_concept_id, old_theme_id))
            else:
                self.setSessionInfoTrans('Record updated.')
                REQUEST.RESPONSE.redirect('theme_relations_html')

    security.declareProtected(view_management_screens, 'manage_delete_threlations')
    def manage_delete_threlations(self, ids=[], REQUEST=None):
        """ delete theme relations """
        del_count = 0
        self.__delete_threlation(self.getIdsList(ids))

        query = [('meta_type',THEME_ITEM_METATYPE)]
        th_list = self.catalog.searchCatalog(query)
        for th_ob in th_list:
            query = [('meta_type',THEME_RELATION_ITEM_METATYPE),
                     ('theme_id',th_ob.theme_id)]
            if not self.catalog.searchCatalog(query):
                theme_folder = self.getThemesFolder()
                theme_folder.manage_delete_themes(['%s###%s' % (th_ob.theme_id, th_ob.langcode)])
                del_count += 1

        if REQUEST:
            self.setSessionInfoTrans(['Selected records deleted.',
                ('${del_count} related records were deleted.', {'del_count': del_count}, )])
            REQUEST.RESPONSE.redirect('theme_relations_html')

    security.declareProtected(view_management_screens, 'getThRelationItemData')
    def getThRelationItemData(self):
        """ return a theme relation based on its ID """
        if self.isSessionConceptId():
            concept_id =        self.getSessionConceptId()
            theme_id =          self.getSessionThemeId()
            orig_concept_id =   self.REQUEST.get('concept_id', None)
            orig_theme_id =     self.REQUEST.get('theme_id', None)
        else:
            concept_id =        self.REQUEST.get('concept_id', self.getSessionConceptId())
            theme_id =          self.REQUEST.get('theme_id', self.getSessionThemeId())
            orig_concept_id =   concept_id
            orig_theme_id =     theme_id

        self.delSessionConceptId()
        self.delSessionThemeId()
        return self.get_threlation_item_data(concept_id, theme_id, orig_concept_id, orig_theme_id)


    #statistics
    def getAllRelTh(self):
        query = [('meta_type',THEME_RELATION_ITEM_METATYPE)]
        return self.catalog.searchCatalog(query)

    def getRelThNumber(self):
        return len(self.getAllRelTh())

    def getDistinctThNumber(self):
        return len(self.getDistinctThemes())

    def getDistinctThemes(self):
        themes_list = []
        add_theme_id = themes_list.append

        query = [('meta_type',THEME_RELATION_ITEM_METATYPE)]
        th_relations = self.catalog.searchCatalog(query)

        for rel_ob in th_relations:
            theme_id = rel_ob.theme_id
            if theme_id not in themes_list: add_theme_id(theme_id)

        return themes_list

    def getUntranslatedThemes(self):
        th_count = 0
        for theme_id in self.getDistinctThemes():
            query = [('meta_type',THEME_ITEM_METATYPE),
                     ('theme_id',theme_id)]
            if not self.catalog.searchCatalog(query):
                th_count += 1
        return th_count


    #management tabs
    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =       PageTemplateFile("%s/zpt/ThemeRelations/properties" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'theme_relations_html')
    theme_relations_html =   PageTemplateFile("%s/zpt/ThemeRelations/theme_relations" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'statistics_html')
    statistics_html =       PageTemplateFile("%s/zpt/ThemeRelations/statistics" % NAAYATHESAURUS_PATH, globals())

InitializeClass(ThemeRelations)


class ThemeRelationItem:
    """ ThemeRelationItem """

    meta_type = THEME_RELATION_ITEM_METATYPE

    def __init__(self, concept_id, theme_id):
        """ constructor """
        self.concept_id =   concept_id
        self.theme_id =     theme_id

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(ThemeRelationItem)
