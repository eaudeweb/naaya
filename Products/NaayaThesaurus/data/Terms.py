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
from Products.NaayaThesaurus.constants              import *
from Products.NaayaThesaurus.utils                  import th_utils
from Products.NaayaThesaurus.session_manager        import session_manager
from Products.NaayaThesaurus.parsers.term_parser    import term_parser

manage_addTerms_html = PageTemplateFile('%s/zpt/Terms/add' % NAAYATHESAURUS_PATH, globals())

def manage_addTerms(self, id='', title='', REQUEST=None):
    """ adds a new Terms object """
    ob = Terms(id, title)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class Terms(SimpleItem, session_manager):
    """ Terms """

    meta_type = TERMS_METATYPE
    product_name = NAAYATHESAURUS_PRODUCT_NAME
    icon = 'misc_/NaayaThesaurus/terms.gif'

    manage_options = (
        {'label':'Properties',      'action':'properties_html'},
        {'label':'Management',      'action':'terms_html'},
        {'label':'Import',   'action':'import_html'},
        {'label':'Statistics',      'action':'statistics_html'},
        {'label':'Undo',            'action':'manage_UndoForm'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id =       id
        self.title =    title
        self.terms =    PersistentMapping()


    #basic properties
    security.declareProtected(view_management_screens, 'manageBasicProperties')
    def manageBasicProperties(self, title='', REQUEST=None):
        """ manage basic properties for Terms """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans('Saved changes.')
            return REQUEST.RESPONSE.redirect('properties_html')


    #terms management
    def __add_term(self, concept_id, langcode, concept_name, source_id):
        #create a new item
        item = TermItem(concept_id, langcode, concept_name, source_id)
        self.terms[(concept_id, langcode)] = item
        self.catalog.CatalogObject(item)

    def __update_term(self, concept_id, old_concept_id, langcode, old_langcode,
                      concept_name, source_id):
        #modify an item
        item = self.terms.get((old_concept_id, old_langcode))
        if item is not None:
            self.__delete_term((old_concept_id, old_langcode))
        self.__add_term(concept_id, langcode, concept_name, source_id)

    security.declareProtected(view_management_screens, 'update_source_id')
    def update_source_id(self, concept_id, langcode, source_id):
        """ update the source_id list """
        term_ob = self.get_term_by_id((concept_id, langcode))
        if term_ob.source_id: upd_source_id = "%s %s" % (term_ob.source_id, source_id)
        else:                 upd_source_id = source_id
        self.__update_term(concept_id, concept_id, langcode, langcode, term_ob.concept_name, upd_source_id)

    def __delete_term(self, ids):
        #delete 1 or more items
        if type(ids) != type((1,1)):
            ids = th_utils().utConvertToList(ids)
        else:
            ids = [ids]
        collection = self.get_terms()

        for id in ids:
            self.catalog.UncatalogObject(collection[id])
            del collection[id]


    #term constraints
    security.declareProtected(view_management_screens, 'checkTerm')
    def checkTerm(self, concept_id):
        """ """
        if self.getConceptsFolder().get_concept_by_id(concept_id):
            return 1
        return 0

    security.declareProtected(view_management_screens, 'getIdsList')
    def getIdsList(self, ids, all=0):
        """ """
        if all: return self.terms.keys()
        return th_utils().getIdsList(ids)


    #terms getters
    def get_terms(self):
        #get all terms
        return self.terms

    def get_terms_sorted(self):
        #get all terms sorted
        return th_utils().utSortObjsListByAttr(self.terms.values(), 'concept_id', 0)

    def get_term_by_id(self, id):
        #get an item
        try:    return self.terms[id]
        except: return None

    def get_term_item_data(self, concept_id, langcode, orig_concept_id, orig_langcode, concept_name, source_id):
        #get an item data
        item = self.get_term_by_id((orig_concept_id, orig_langcode))
        if item is not None:
            if concept_name is None:
                concept_name = item.concept_name
            if source_id is None:
                source_id = item.source_id
            return ['update', concept_id, langcode, concept_name, source_id, orig_concept_id, orig_langcode]
        else:
            return ['add', concept_id, langcode, concept_name, source_id, '', '']


    #terms api
    security.declareProtected(view_management_screens, 'manage_add_term')
    def manage_add_term(self, concept_id='', langcode='', concept_name='', source_id='', REQUEST=None):
        """ manage terms """
        err = 0
        if self.checkTerm(concept_id):
            self.__add_term(concept_id, langcode, concept_name, source_id)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionLangcode(langcode)
                self.setSessionConceptName(concept_name)
                self.setSessionSourceId(source_id)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
            else:
                self.setSessionInfoTrans('Record added.')
            REQUEST.RESPONSE.redirect('terms_html')

    security.declareProtected(view_management_screens, 'manage_update_term')
    def manage_update_term(self, concept_id='', old_concept_id='', langcode='', old_langcode='',
                           concept_name='', source_id='', REQUEST=None):
        """ update term """
        err = 0
        if self.checkTerm(concept_id):
            self.__update_term(concept_id, old_concept_id, langcode, old_langcode, concept_name, source_id)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionConceptId(concept_id)
                self.setSessionLangcode(langcode)
                self.setSessionConceptName(concept_name)
                self.setSessionSourceId(source_id)
                self.setSessionErrorsTrans('${concept_id} is not a valid concept ID.', concept_id=concept_id)
                REQUEST.RESPONSE.redirect('terms_html?concept_id=%s&amp;langcode=%s' % (old_concept_id, old_langcode))
            else:
                self.setSessionInfoTrans('Record updated.')
                REQUEST.RESPONSE.redirect('terms_html')

    security.declareProtected(view_management_screens, 'manage_delete_terms')
    def manage_delete_terms(self, ids=[], delete_all='', REQUEST=None):
        """ delete terms """
        if delete_all:  ids = self.getIdsList(ids, 1)
        else:           ids = self.getIdsList(ids)
        self.__delete_term(ids)

        if REQUEST:
            self.setSessionInfoTrans('Selected records deleted.')
            REQUEST.RESPONSE.redirect('terms_html')

    security.declareProtected(view_management_screens, 'getTermItemData')
    def getTermItemData(self):
        """ return a term based on its ID """
        if self.isSessionConceptId():
            concept_id =        self.getSessionConceptId()
            langcode =          self.getSessionLangcode()
            concept_name =      self.getSessionConceptName()
            source_id =         self.getSessionSourceId()
            orig_concept_id =   self.REQUEST.get('concept_id', None)
            orig_langcode =     self.REQUEST.get('langcode', None)
        else:
            concept_id =        self.REQUEST.get('concept_id', self.getSessionConceptId())
            langcode =          self.REQUEST.get('langcode', self.getSessionLangcode())
            concept_name =      self.getSessionConceptName()
            source_id =         self.getSessionSourceId()
            orig_concept_id =   concept_id
            orig_langcode =     langcode

        self.delSessionConceptId()
        self.delSessionLangcode()
        self.delSessionConceptName()
        self.delSessionSourceId()
        return self.get_term_item_data(concept_id, langcode, orig_concept_id, orig_langcode, concept_name, source_id)


    #import related
    def skos_import(self, file, langcode, REQUEST=None):
        """ """
        parser = term_parser()

        #parse the SKOS information
        chandler = parser.parseHeader(file)

        if chandler is None:
            if REQUEST:
                self.setSessionErrorsTrans('Parsing error. The file could not be parsed.')
                return REQUEST.RESPONSE.redirect('import_html')

        #get the target language
        skos_lang = chandler.getLanguage()
        if skos_lang:   langcode = skos_lang.encode('utf-8')

        #get data
        pref_info =     chandler.getPref()
        alt_info =      chandler.getAlt()
        def_info =      chandler.getDef()
        scope_info =    chandler.getScope()
        src_info =      chandler.getSrc()
        def_src_info =  chandler.getDefSrc()

        #info
        count_terms =   0
        err_terms =     []
        count_altterms = 0
        err_altterms =  []
        count_def =     0
        err_defs =      []
        count_scope =   0
        err_scope =     []
        count_src =     0
        err_src =       []
        count_def_src = 0
        err_def_src =   []

        #set Terms
        for id, data in pref_info.items():
            concept_id = data['concept_id'].encode('utf-8').split('/')[-1]
            if concept_id:
                concept_name = data['concept_name']
                source_id = ''
                if self.checkTerm(concept_id):
                    self.__add_term(concept_id, langcode, concept_name, source_id)
                    count_terms += 1
                else:
                    err_terms.append(concept_id)
            else:
                err_terms.append('None')

        #set Alternatives terms
        for id, data in alt_info.items():
            concept_id = data['concept_id'].encode('utf-8').split('/')[-1]
            if concept_id:
                alt_terms_folder = self.getAltTermsFolder()
                alt_name = data['alt_name']
                if self.checkTerm(concept_id):
                    alt_terms_folder.manage_add_altterm(concept_id, langcode, alt_name)
                    count_altterms += 1
                else:
                    err_altterms.append(concept_id)
            else:
                err_altterms.append('None')

        #set Definitions
        for id, data in def_info.items():
            concept_id = data['concept_id'].encode('utf-8').split('/')[-1]
            if concept_id:
                definitions_folder = self.getDefinitionsFolder()
                definition = data['definition']
                if self.checkTerm(concept_id):
                    #TODO: implement source
                    definitions_folder.manage_add_definition(concept_id, langcode, definition, '')
                    count_def += 1
                else:
                    err_defs.append(concept_id)
            else:
                err_defs.append('None')

        #set ScopeNotes
        for id, data in scope_info.items():
            concept_id = data['concept_id'].encode('utf-8').split('/')[-1]
            if concept_id:
                scopenotes_folder = self.getScopeNotesFolder()
                scope_note = data['scope_note']
                if self.checkTerm(concept_id):
                    scopenotes_folder.manage_add_scope(concept_id, langcode, scope_note)
                    count_scope += 1
                else:
                    err_scope.append(concept_id)
            else:
                err_scope.append('None')

        #set Terms sources
        for id, data in src_info.items():
            source_id =     data['source_id']
            source_name =   data['source_name']
            concept_id =    data['concept_id'].encode('utf-8').split('/')[-1]

            if concept_id:
                if self.checkTerm(concept_id):
                    sources_folder = self.getSourceFolder()
                    #add source record
                    sources_folder.manage_add_source(source_id, source_name)
                    #update term record
                    self.update_source_id(concept_id, langcode, source_id)
                    count_src += 1
                else:
                    err_src.append(concept_id)
            else:
                err_src.append('None')

        #set Definitions sources
        for id, data in def_src_info.items():
            source_id =     data['source_id']
            source_name =   data['source_name']
            concept_id =    data['concept_id'].encode('utf-8').split('/')[-1]

            if concept_id:
                if self.checkTerm(concept_id):
                    sources_folder = self.getSourceFolder()
                    definitions_folder = self.getDefinitionsFolder()
                    #add source record
                    sources_folder.manage_add_source(source_id, source_name)
                    #update definition record
                    definitions_folder.update_source_id(concept_id, langcode, source_id)
                    count_def_src += 1
                else:
                    err_def_src.append(concept_id)
            else:
                err_def_src.append('None')

        if REQUEST:
            self.setSessionInfoTrans(['File imported successfully.',
                ('Translations added: ${count_terms}', {'count_terms':  count_terms}, ),
                ('Alternative terms added: ${count_altterms}', {'count_altterms':  count_altterms}, ),
                ('Definitions added: ${count_def}', {'count_def':  count_def}, ),
                ('ScopeNotes added: ${count_scope}', {'count_scope':  count_scope}, ),
                ('Terms Sources added: ${count_src}', {'count_src':  count_src}, ),
                ('Definitions Sources added: ${count_def_src}', {'count_def_src':  count_def_src}, ),
            ])
            msg_err = []
            if err_terms:
                msg_err.append(('Translations not imported because the specified concept_id does not exist: ${err_terms}',
                    {'err_terms': th_utils().utJoinToString(err_terms, ', ')}, ))
            if err_altterms:
                msg_err.append(('Alternative terms not imported because the specified concept_id does not exist: ${err_altterms}',
                    {'err_altterms': th_utils().utJoinToString(err_altterms, ', ')}, ))
            if err_defs:
                msg_err.append(('Definitions not imported because the specified concept_id does not exist: ${err_defs}',
                    {'err_defs': th_utils().utJoinToString(err_defs, ', ')}, ))
            if err_scope:
                msg_err.append(('ScopeNotes not imported because the specified concept_id does not exist: ${err_scope}',
                    {'err_scope': th_utils().utJoinToString(err_scope, ', ')}, ))
            if err_src:
                msg_err.append(('Term sources not imported because the specified concept_id does not exist: ${err_src}',
                    {'err_src': th_utils().utJoinToString(err_src, ', ')}, ))
            if err_def_src:
                msg_err.append(('Definition sources not imported because the specified concept_id does not exist: ${err_def_src}',
                    {'err_def_src': th_utils().utJoinToString(err_def_src, ', ')}, ))
            if msg_err:
                self.setSessionErrorsTrans(msg_err)
            return REQUEST.RESPONSE.redirect('import_html')


    #statistics
    def getAllTerms(self):
        query = [('meta_type',TERM_ITEM_METATYPE)]
        return self.catalog.searchCatalog(query)

    def getTermsNumber(self):
        return len(self.getAllTerms())

    def getTermsTransNumber(self):
        results = {}
        for term_ob in self.getAllTerms():
            try:    tr_count = results[term_ob.langcode][0]
            except: tr_count = 0
            tr_count += 1

            try:    src_count = results[term_ob.langcode][1]
            except: src_count = 0
            if term_ob.source_id: src_count += 1

            results[term_ob.langcode] = (tr_count, src_count)
        return results

    def getTermsWithSource(self):
        count = 0
        for term_ob in self.getAllTerms():
            if len(term_ob.source_id): count += 1
        return count

    def getEmptyTrans(self):
        empty_count = 0
        for term_ob in self.getAllTerms():
            if not term_ob.concept_name:
                empty_count += 1
        return empty_count


    #management tabs
    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =   PageTemplateFile("%s/zpt/Terms/properties" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'terms_html')
    terms_html =        PageTemplateFile("%s/zpt/Terms/terms" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'statistics_html')
    statistics_html =   PageTemplateFile("%s/zpt/Terms/statistics" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'import_html')
    import_html =       PageTemplateFile("%s/zpt/Terms/import" % NAAYATHESAURUS_PATH, globals())

InitializeClass(Terms)


class TermItem:
    """ TermItem """

    meta_type = TERM_ITEM_METATYPE

    def __init__(self, concept_id, langcode, concept_name, source_id):
        """ constructor """
        self.concept_id =       concept_id
        self.langcode =         langcode
        self.concept_name =     concept_name
        self.source_id =        source_id

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(TermItem)
