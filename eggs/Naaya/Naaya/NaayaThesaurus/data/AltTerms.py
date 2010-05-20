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


manage_addAltTerms_html = PageTemplateFile('%s/zpt/AltTerms/add' % NAAYATHESAURUS_PATH, globals())

def manage_addAltTerms(self, id='', title='', REQUEST=None):
    """ adds a new AltTerms object """
    ob = AltTerms(id, title)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class AltTerms(SimpleItem, session_manager):
    """ AltTerms """

    meta_type = ALTTERMS_METATYPE
    product_name = NAAYATHESAURUS_PRODUCT_NAME
    icon = 'misc_/NaayaThesaurus/alt_terms.gif'

    manage_options = (
        {'label':'Properties',      'action':'properties_html'},
        {'label':'Management',      'action':'altterms_html'},
        {'label':'Statistics',      'action':'statistics_html'},
        {'label':'Undo',            'action':'manage_UndoForm'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id =           id
        self.title =        title
        self.altterms =    PersistentMapping()


    #basic properties
    security.declareProtected(view_management_screens, 'manageBasicProperties')
    def manageBasicProperties(self, title='', REQUEST=None):
        """ manage basic properties for AltTerms """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans('Saved changes.')
            return REQUEST.RESPONSE.redirect('properties_html')


    #alt_terms management
    def __add_altterm(self, concept_id, langcode, alt_name):
        #create a new item
        item = AltTermItem(concept_id, langcode, alt_name)
        self.altterms[(concept_id, langcode)] = item
        self.catalog.CatalogObject(item)

    def __update_altterm(self, concept_id, old_concept_id, langcode, old_langcode, alt_name):
        #modify an item
        item = self.altterms.get((old_concept_id, old_langcode))
        if item is not None:
            self.__delete_altterm((old_concept_id, old_langcode))
        self.__add_altterm(concept_id, langcode, alt_name)

    def __delete_altterm(self, ids):
        #delete 1 or more items
        if type(ids) != type((1,1)):
            ids = th_utils().utConvertToList(ids)
        else:
            ids = [ids]
        collection = self.get_altterms()

        for id in ids:
            self.catalog.UncatalogObject(collection[id])
            del collection[id]


    #altterm constraints
    security.declareProtected(view_management_screens, 'checkAltTerm')
    def checkAltTerm(self, concept_id):
        """ """
        if self.getConceptsFolder().get_concept_by_id(concept_id):
            return 1
        return 0

    security.declareProtected(view_management_screens, 'getIdsList')
    def getIdsList(self, ids, all=0):
        """ """
        if all: return self.altterms.keys()
        return th_utils().getIdsList(ids)


    #terms getters
    def get_altterms(self):
        #get all alt_terms
        return self.altterms

    def get_altterms_sorted(self):
        #get all alt_terms sorted
        return th_utils().utSortObjsListByAttr(self.altterms.values(), 'concept_id', 0)

    def get_altterm_by_id(self, id):
        #get an item
        try:    return self.altterms[id]
        except: return None

    def get_altterm_item_data(self,concept_id, langcode, orig_concept_id, orig_langcode, alt_name):
        #get an item data
        item = self.get_altterm_by_id((orig_concept_id, orig_langcode))
        if item is not None:
            if alt_name is None:
                alt_name = item.alt_name
            return ['update', concept_id, langcode, alt_name, orig_concept_id, orig_langcode]
        else:
            return ['add', concept_id, langcode, alt_name, '', '']


    #alt_terms api
    security.declareProtected(view_management_screens, 'manage_add_altterm')
    def manage_add_altterm(self, concept_id='', langcode='', alt_name='', REQUEST=None):
        """ manage alt_terms """
        err = 0
        if self.checkAltTerm(concept_id):
            self.__add_altterm(concept_id, langcode, alt_name)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionLangcode(langcode)
                self.setSessionAltName(alt_name)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
            else:
                self.setSessionInfoTrans('Record added.')
            REQUEST.RESPONSE.redirect('altterms_html')

    security.declareProtected(view_management_screens, 'manage_update_altterm')
    def manage_update_altterm(self, concept_id='', old_concept_id='', langcode='', old_langcode='', alt_name='', REQUEST=None):
        """ update alt_term """
        err = 0
        if self.checkAltTerm(concept_id):
            self.__update_altterm(concept_id, old_concept_id, langcode, old_langcode, alt_name)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionLangcode(langcode)
                self.setSessionAltName(alt_name)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
                REQUEST.RESPONSE.redirect('altterms_html?concept_id=%s&amp;langcode=%s' % (old_concept_id, old_langcode))
            else:
                self.setSessionInfoTrans('Record updated.')
                REQUEST.RESPONSE.redirect('altterms_html')

    security.declareProtected(view_management_screens, 'manage_delete_altterms')
    def manage_delete_altterms(self, ids=[], delete_all='', REQUEST=None):
        """ delete alt_terms """
        if delete_all:  ids = self.getIdsList(ids, 1)
        else:           ids = self.getIdsList(ids)
        self.__delete_altterm(ids)

        if REQUEST:
            self.setSessionInfoTrans('Selected records deleted.')
            REQUEST.RESPONSE.redirect('altterms_html')

    security.declareProtected(view_management_screens, 'getAltTermItemData')
    def getAltTermItemData(self):
        """ return a term based on its ID """
        if self.isSessionConceptId():
            concept_id =        self.getSessionConceptId()
            langcode =          self.getSessionLangcode()
            alt_name =          self.getSessionAltName()
            orig_concept_id =   self.REQUEST.get('concept_id', None)
            orig_langcode =     self.REQUEST.get('langcode', None)
        else:
            concept_id =        self.REQUEST.get('concept_id', self.getSessionConceptId())
            langcode =          self.REQUEST.get('langcode', self.getSessionLangcode())
            alt_name =          self.getSessionAltName()
            orig_concept_id =   concept_id
            orig_langcode =     langcode

        self.delSessionConceptId()
        self.delSessionLangcode()
        self.delSessionAltName()
        return self.get_altterm_item_data(concept_id, langcode, orig_concept_id, orig_langcode, alt_name)


    #statistics
    def getAllAltTerms(self):
        query = [('meta_type',ALTTERM_ITEM_METATYPE)]
        return self.catalog.searchCatalog(query)

    def getAltTermsNumber(self):
        return len(self.getAllAltTerms())

    def getAltTermsTransNumber(self):
        results = {}
        for altt_ob in self.getAllAltTerms():
            try:    tr_count = results[altt_ob.langcode]
            except: tr_count = 0
            results[altt_ob.langcode] = tr_count + 1
        return results

    def getEmptyTrans(self):
        empty_count = 0
        for altterm_ob in self.getAllAltTerms():
            if not altterm_ob.alt_name:
                empty_count += 1
        return empty_count


    #management tabs
    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =   PageTemplateFile("%s/zpt/AltTerms/properties" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'altterms_html')
    altterms_html =     PageTemplateFile("%s/zpt/AltTerms/altterms" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'statistics_html')
    statistics_html =   PageTemplateFile("%s/zpt/AltTerms/statistics" % NAAYATHESAURUS_PATH, globals())

InitializeClass(AltTerms)


class AltTermItem:
    """ AltTermItem """

    meta_type = ALTTERM_ITEM_METATYPE

    def __init__(self, concept_id, langcode, alt_name):
        """ constructor """
        self.concept_id =   concept_id
        self.langcode =     langcode
        self.alt_name =     alt_name

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(AltTermItem)
