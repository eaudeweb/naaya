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

manage_addScopeNotes_html = PageTemplateFile('%s/zpt/ScopeNotes/add' % NAAYATHESAURUS_PATH, globals())

def manage_addScopeNotes(self, id='', title='', REQUEST=None):
    """ adds a new ScopeNotes object """
    ob = ScopeNotes(id, title)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class ScopeNotes(SimpleItem, session_manager):
    """ ScopeNotes """

    meta_type = SCOPE_NOTES_METATYPE
    product_name = NAAYATHESAURUS_PRODUCT_NAME
    icon = 'misc_/NaayaThesaurus/scope_notes.gif'

    manage_options = (
        {'label':'Properties',      'action':'properties_html'},
        {'label':'Management',      'action':'scope_notes_html'},
        {'label':'Statistics',      'action':'statistics_html'},
        {'label':'Undo',            'action':'manage_UndoForm'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id =           id
        self.title =        title
        self.scopes =   PersistentMapping()


    #basic properties
    security.declareProtected(view_management_screens, 'manageBasicProperties')
    def manageBasicProperties(self, title='', REQUEST=None):
        """ manage basic properties for ScopeNotes """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans('Saved changes.')
            return REQUEST.RESPONSE.redirect('properties_html')


    #scope notes management
    def __add_scope(self, concept_id, langcode, scope_note):
        #create a new item
        item = ScopeItem(concept_id, langcode, scope_note)
        self.scopes[(concept_id, langcode)] = item
        self.catalog.CatalogObject(item)

    def __update_scope(self, concept_id, old_concept_id, langcode, old_langcode, scope_note):
        #modify an item
        item = self.scopes.get((old_concept_id, old_langcode))
        if item is not None:
            self.__delete_scope((old_concept_id, old_langcode))
        self.__add_scope(concept_id, langcode, scope_note)

    def __delete_scope(self, ids):
        #delete 1 or more items
        if type(ids) != type((1,1)):
            ids = th_utils().utConvertToList(ids)
        else:
            ids = [ids]
        collection = self.get_scopes()

        for id in ids:
            self.catalog.UncatalogObject(collection[id])
            del collection[id]


    #scope constraints
    security.declareProtected(view_management_screens, 'checkScope')
    def checkScope(self, concept_id):
        """ """
        if self.getConceptsFolder().get_concept_by_id(concept_id):
            return 1
        return 0

    security.declareProtected(view_management_screens, 'getIdsList')
    def getIdsList(self, ids, all=0):
        """ """
        if all: return self.scopes.keys()
        return th_utils().getIdsList(ids)


    #scope notes getters
    def get_scopes(self):
        #get all scope notes
        return self.scopes

    def get_scopes_sorted(self):
        #get all scope notes sorted
        return th_utils().utSortObjsListByAttr(self.scopes.values(), 'concept_id', 0)

    def get_scope_by_id(self, id):
        #get an item
        try:    return self.scopes[id]
        except: return None

    def get_scope_item_data(self, concept_id, langcode, orig_concept_id, orig_langcode, scope_note):
        #get an item data
        item = self.get_scope_by_id((orig_concept_id, orig_langcode))
        if item is not None:
            if scope_note is None:
                scope_note = item.scope_note
            return ['update', concept_id, langcode, scope_note, orig_concept_id, orig_langcode]
        else:
            return ['add', concept_id, langcode, scope_note, '', '']


    #scope notes api
    security.declareProtected(view_management_screens, 'manage_add_scope')
    def manage_add_scope(self, concept_id='', langcode='', scope_note='', REQUEST=None):
        """ manage scope notes """
        err = 0
        if self.checkScope(concept_id):
            self.__add_scope(concept_id, langcode, scope_note)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionLangcode(langcode)
                self.setSessionScopeNote(scope_note)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
            else:
                self.setSessionInfoTrans('Record added.')
            REQUEST.RESPONSE.redirect('scope_notes_html')

    security.declareProtected(view_management_screens, 'manage_update_scope')
    def manage_update_scope(self, concept_id='', old_concept_id='', langcode='', old_langcode='',
                           scope_note='', REQUEST=None):
        """ update scope note """
        err = 0
        if self.checkScope(concept_id):
            self.__update_scope(concept_id, old_concept_id, langcode, old_langcode, scope_note)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionLangcode(langcode)
                self.setSessionScopeNote(scope_note)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
                REQUEST.RESPONSE.redirect('scope_notes_html?concept_id=%s&amp;langcode=%s' % (old_concept_id, old_langcode))
            else:
                self.setSessionInfoTrans('Record updated.')
                REQUEST.RESPONSE.redirect('scope_notes_html')

    security.declareProtected(view_management_screens, 'manage_delete_scopes')
    def manage_delete_scopes(self, ids=[], delete_all='', REQUEST=None):
        """ delete scope notes """
        if delete_all:  ids = self.getIdsList(ids, 1)
        else:           ids = self.getIdsList(ids)
        self.__delete_scope(ids)

        if REQUEST:
            self.setSessionInfoTrans('Selected records deleted.')
            REQUEST.RESPONSE.redirect('scope_notes_html')

    security.declareProtected(view_management_screens, 'getScopeItemData')
    def getScopeItemData(self):
        """ return a scope note based on its ID """
        if self.isSessionConceptId():
            concept_id =        self.getSessionConceptId()
            langcode =          self.getSessionLangcode()
            scope_note =        self.getSessionScopeNote()
            orig_concept_id =   self.REQUEST.get('concept_id', None)
            orig_langcode =     self.REQUEST.get('langcode', None)
        else:
            concept_id =        self.REQUEST.get('concept_id', self.getSessionConceptId())
            langcode =          self.REQUEST.get('langcode', self.getSessionLangcode())
            scope_note =        self.getSessionScopeNote()
            orig_concept_id =   concept_id
            orig_langcode =     langcode

        self.delSessionConceptId()
        self.delSessionLangcode()
        self.delSessionScopeNote()
        return self.get_scope_item_data(concept_id, langcode, orig_concept_id, orig_langcode, scope_note)


    #statistics
    def getAllScope(self):
        query = [('meta_type',SCOPE_ITEM_METATYPE)]
        return self.catalog.searchCatalog(query)

    def getScopeNumber(self):
        return len(self.getAllScope())

    def getScopeTransNumber(self):
        results = {}
        for scope_ob in self.getAllScope():
            try:    tr_count = results[scope_ob.langcode]
            except: tr_count = 0
            results[scope_ob.langcode] = tr_count + 1
        return results

    def getEmptyTrans(self):
        empty_count = 0
        for scope_ob in self.getAllScope():
            if not scope_ob.scope_note:
                empty_count += 1
        return empty_count


    #management tabs
    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =   PageTemplateFile("%s/zpt/ScopeNotes/properties" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'scope_notes_html')
    scope_notes_html =  PageTemplateFile("%s/zpt/ScopeNotes/scope_notes" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'statistics_html')
    statistics_html =   PageTemplateFile("%s/zpt/ScopeNotes/statistics" % NAAYATHESAURUS_PATH, globals())

InitializeClass(ScopeNotes)


class ScopeItem:
    """ ScopeItem """

    meta_type = SCOPE_ITEM_METATYPE

    def __init__(self, concept_id, langcode, scope_note):
        """ constructor """
        self.concept_id =   concept_id
        self.langcode =     langcode
        self.scope_note =   scope_note

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(ScopeItem)