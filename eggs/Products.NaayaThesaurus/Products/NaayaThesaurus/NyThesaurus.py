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
# The Original Code is NaayaThesaurus version 1.0
#
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Ghica Alexandru, Finsiel Romania


#Python imports
import string
from copy       import copy
from os.path    import join

#Zope imports
import Products
import AccessControl.User
from OFS.Folder                                 import Folder
from AccessControl                              import ClassSecurityInfo
from Products.ZCatalog.ZCatalog                 import ZCatalog
from Globals                                    import MessageDialog, InitializeClass
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate    import manage_addPageTemplate
from Products.PythonScripts.PythonScript        import manage_addPythonScript
from AccessControl.Permissions                  import view_management_screens, view

#Product imports
from Products.NaayaThesaurus.data.Themes            import manage_addThemes_html, manage_addThemes
from Products.NaayaThesaurus.data.ThemeRelations    import manage_addThemeRelations_html, manage_addThemeRelations
from Products.NaayaThesaurus.data.AltTerms          import manage_addAltTerms_html, manage_addAltTerms
from Products.NaayaThesaurus.data.ConceptRelations  import manage_addConceptRelations_html, manage_addConceptRelations
from Products.NaayaThesaurus.data.Concepts          import manage_addConcepts_html, manage_addConcepts
from Products.NaayaThesaurus.data.Definitions       import manage_addDefinitions_html, manage_addDefinitions
from Products.NaayaThesaurus.data.ScopeNotes        import manage_addScopeNotes_html, manage_addScopeNotes
from Products.NaayaThesaurus.data.Source            import manage_addSource_html, manage_addSource
from Products.NaayaThesaurus.data.Terms             import manage_addTerms_html, manage_addTerms
from Products.NaayaThesaurus.ThesaurusCatalog       import manage_addThesaurusCatalog
from Products.NaayaThesaurus.constants              import *
from Products.NaayaCore.managers.utils              import file_utils
from Products.NaayaThesaurus.utils                  import th_utils


manage_addThesaurus_html = PageTemplateFile('zpt/NaayaThesaurus/add', globals())
def manage_addThesaurus(self, id, title='', REQUEST=None):
    """ Adds a new NaayaThesaurus object """
    ob = NyThesaurus(id, title)
    self._setObject(id, ob)
    obj = self._getOb(id)
    obj._addDataFolders()
    obj._addDefaultData()

    #creates the catalog
    manage_addThesaurusCatalog(obj)

    obj._p_changed = 1
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)


class NyThesaurus(Folder):
    """ NyThesaurus """

    meta_type =     NAAYATHESAURUS_METATYPE
    product_name =  NAAYATHESAURUS_PRODUCT_NAME
    icon =          "misc_/NaayaThesaurus/thesaurus.gif"

    manage_options =((Folder.manage_options[0],) +
                ({'label':'Properties',          'action':'properties_html'},
                 {'label':'View',                'action':'index_html'},
                 {'label':'Undo',                'action':'manage_UndoForm'},)
                )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id =                   id
        self.title =                title
        self.approved =             1
        self.__alphabets_cache =    {}

    def __setstate__(self,state):
        """ """
        NyThesaurus.inheritedAttribute('__setstate__')(self, state)
        if not hasattr(self, '__alphabets_cache'):
            self.__alphabets_cache = {}

    def all_meta_types(self, interfaces=None):
        """ what can you put inside me """
        local_meta_types = [
            {'name': THEMES_METATYPE,               'action': 'manage_addThemes_html',              'product': NAAYATHESAURUS_PRODUCT_NAME},
            {'name': ALTTERMS_METATYPE,             'action': 'manage_addAltTerms_html',            'product': NAAYATHESAURUS_PRODUCT_NAME},
            {'name': CONCEPT_RELATIONS_METATYPE,    'action': 'manage_addConceptRelations_html',    'product': NAAYATHESAURUS_PRODUCT_NAME},
            {'name': CONCEPTS_METATYPE,             'action': 'manage_addConcepts_html',            'product': NAAYATHESAURUS_PRODUCT_NAME},
            {'name': DEFINITIONS_METATYPE,          'action': 'manage_addDefinitions_html',         'product': NAAYATHESAURUS_PRODUCT_NAME},
            {'name': SCOPE_NOTES_METATYPE,          'action': 'manage_addScopeNotes_html',          'product': NAAYATHESAURUS_PRODUCT_NAME},
            {'name': SOURCE_METATYPE,               'action': 'manage_addSource_html',              'product': NAAYATHESAURUS_PRODUCT_NAME},
            {'name': TERMS_METATYPE,                'action': 'manage_addTerms_html',               'product': NAAYATHESAURUS_PRODUCT_NAME},
            {'name': THEME_RELATION_METATYPE,       'action': 'manage_addThemeRelations_html',      'product': NAAYATHESAURUS_PRODUCT_NAME},
            {'name': NAAYATHESAURUS_CATALOG_TITLE,  'action': 'manage_addThesaurusCatalog',         'product': NAAYATHESAURUS_PRODUCT_NAME},
        ]
        f = lambda x: x['name'] in ('Page Template', 'Script (Python)', 'File', 'Folder', 'DTML Method', 'Image', THEMES_METATYPE)
        for x in filter(f, Products.meta_types):
            local_meta_types.append(x)
        return local_meta_types

    manage_addThemes_html = manage_addThemes_html
    manage_addThemes = manage_addThemes

    manage_addAltTerms_html = manage_addAltTerms_html
    manage_addAltTerms = manage_addAltTerms

    manage_addConceptRelations_html = manage_addConceptRelations_html
    manage_addConceptRelations = manage_addConceptRelations

    manage_addConcepts_html = manage_addConcepts_html
    manage_addConcepts = manage_addConcepts

    manage_addDefinitions_html = manage_addDefinitions_html
    manage_addDefinitions = manage_addDefinitions

    manage_addScopeNotes_html = manage_addScopeNotes_html
    manage_addScopeNotes = manage_addScopeNotes

    manage_addSource_html = manage_addSource_html
    manage_addSource = manage_addSource

    manage_addTerms_html = manage_addTerms_html
    manage_addTerms = manage_addTerms

    manage_addThemeRelations_html = manage_addThemeRelations_html
    manage_addThemeRelations = manage_addThemeRelations

    manage_addThesaurusCatalog = manage_addThesaurusCatalog

    #getters
    def getThesaurusOb(self): return self
    def is_approved(self): return self.approved

    security.declarePublic('getThesaurusPath')
    def getThesaurusPath(self, p=0): return self.absolute_url(p)


    #data object geters
    def getAltTermsFolder(self):            return self._getOb('alt_terms')
    def getConceptRelationsFolder(self):    return self._getOb('concept_relations')
    def getConceptsFolder(self):            return self._getOb('concepts')
    def getDefinitionsFolder(self):         return self._getOb('definitions')
    def getScopeNotesFolder(self):          return self._getOb('scope_notes')
    def getSourceFolder(self):              return self._getOb('source')
    def getTermsFolder(self):               return self._getOb('terms')
    def getThemesFolder(self):              return self._getOb('themes')
    def getThemeRelationsFolder(self):      return self._getOb('theme_relations')

    #load properties
    def _addDefaultData(self):
        #add default CSS file
        style_css = open(join(NAAYATHESAURUS_PATH,'zpt','NaayaThesaurus','style_presentation.zpt'))
        content = style_css.read()
        style_css.close()
        manage_addPageTemplate(self, 'thesaurus_css', title='Naaya Thesaurus CSS', text=content)

        #add RDF files
        file_content = open(join(NAAYATHESAURUS_PATH, 'rdfs', 'thesaurus-labels.spy'), 'r').read()
        manage_addPythonScript(self, 'thesaurus-labels.rdf')
        self._getOb('thesaurus-labels.rdf').write(file_content)

        file_content = open(join(NAAYATHESAURUS_PATH, 'rdfs', 'thesaurus-relations.spy'), 'r').read()
        manage_addPythonScript(self, 'thesaurus-relations.rdf')
        self._getOb('thesaurus-relations.rdf').write(file_content)

        file_content = open(join(NAAYATHESAURUS_PATH, 'rdfs', 'thesaurus-themes-relations.spy'), 'r').read()
        manage_addPythonScript(self, 'thesaurus-themes-relations.rdf')
        self._getOb('thesaurus-themes-relations.rdf').write(file_content)

        file_content = open(join(NAAYATHESAURUS_PATH, 'rdfs', 'thesaurus-themes-labels.spy'), 'r').read()
        manage_addPythonScript(self, 'thesaurus-themes-labels.rdf')
        self._getOb('thesaurus-themes-labels.rdf').write(file_content)

    def _addDataFolders(self):
        manage_addThemes(self, id='themes', title='Themes')
        manage_addAltTerms(self, id='alt_terms', title='Alternative Terms')
        manage_addConceptRelations(self, id='concept_relations', title='Concept Relations')
        manage_addConcepts(self, id='concepts', title='Concepts')
        manage_addDefinitions(self, id='definitions', title='Definitions')
        manage_addScopeNotes(self, id='scope_notes', title='Scope Notes')
        manage_addSource(self, id='source', title='Source')
        manage_addTerms(self, id='terms', title='Terms')
        manage_addThemeRelations(self, id='theme_relations', title='Theme Relations')


    #basic functions
    def manageBasicProperties(self, title='', approved=0, REQUEST=None):
        """ manage basic properties for NyThesaurus """
        self.title =        title
        self.approved =     approved
        self._p_changed =   1
        if REQUEST:
            self.setSessionInfoTrans('Saved changes.')
            return REQUEST.RESPONSE.redirect('properties_html')

    #alphabetic listing
    security.declarePublic('buildExpandList')
    def buildExpandList(self, expand):
        return expand.split(',')

    security.declarePublic('checkExpandNode')
    def checkExpandNode(self, expand, node):
        return str(node) in expand

    security.declarePublic('getThesaurusTree')
    def getThesaurusTree(self, lang):
        #returns the thesaurus according with the given language
        self.__clear_alphabets_cache_for_lang(lang)
        if not self.__alphabets_cache.has_key(lang):
            self.__build_alphabets_for_lang(lang)
        return self.__alphabets_cache[lang]

    #alphabets functions
    def _unicode_langs(self):
        #temporary list of implemented languages
        return unicode_character_map.keys()

    def _unicode_map(self, lang):
        #returns unicode set of characters for a given language
        return unicode_character_map.get(lang, unicode_character_map['en'])

    def __clear_alphabets_cache(self):
        self.__alphabets_cache = {}
        self._p_changed = 1

    def __clear_alphabets_cache_for_lang(self, lang):
        try: del(self.__alphabets_cache[lang])
        except: pass
        else: self._p_changed = 1

    def __build_alphabets_for_lang(self, lang):
        self.__alphabets_cache[lang] = []
        dict_lang_tree = {}

        for concept_ob in self.getAllConcepts():
            term_brain = self.getConceptTranslation(concept_ob.concept_id, lang)
            t = u''
            if term_brain.concept_name:
                t = self.catalog.getTermObj(term_brain).concept_name
            if t:
                l = None
                for x in self._unicode_map(lang):
                    if t[0] in x:
                        l = x[0].encode('utf-8')
                        break
                if l is not None:
                    if not dict_lang_tree.has_key(l): dict_lang_tree[l] = []
                    if type(t) == type(u''): t = t.encode('utf-8')
                    dict_lang_tree[l].append((t, term_brain.concept_id))

        for x in self._unicode_map(lang):
            if dict_lang_tree.has_key(x[0].encode('utf-8')):
                l_sorted = th_utils().utSortListByLocale(dict_lang_tree[x[0].encode('utf-8')], 0, lang)
                self.__alphabets_cache[lang].append((x[0].encode('utf-8'), copy(l_sorted)))
        self._p_changed = 1

    #thesaurus api
    security.declarePublic('getThemeByID')
    def getThemeByID(self, theme_id='', lang=''):
        """ """
        query = [('meta_type',THEME_ITEM_METATYPE),
                 ('theme_id',theme_id),
                 ('langcode', lang)]
        result = th_utils().utListToObj(self.catalog.searchCatalog(query))
        if not result: result = DummyTheme(theme_id, '')
        return result

    security.declarePublic('getTermByID')
    def getTermByID(self, concept_id='', lang=''):
        """ """
        query = [('meta_type',TERM_ITEM_METATYPE),
                 ('concept_id',concept_id),
                 ('langcode', lang)]
        return th_utils().utListToObj(self.catalog.searchCatalog(query))

    security.declarePublic('getConceptTranslation')
    def getConceptTranslation(self, concept_id, lang):
        """ """
        term_ob = self.getTermByID(concept_id, lang)
        if not term_ob: term_ob = DummyTerm(concept_id, '')
        return term_ob

    security.declarePublic('getTermByID')
    def getAltTermByID(self, concept_id='', lang=''):
        """ """
        query = [('meta_type',ALTTERM_ITEM_METATYPE),
                 ('concept_id',concept_id),
                 ('langcode', lang)]
        return th_utils().utListToObj(self.catalog.searchCatalog(query))

    security.declarePublic('getConceptByID')
    def getConceptByID(self, concept_id=''):
        """ """
        query = [('meta_type',CONCEPT_ITEM_METATYPE),
                 ('concept_id',concept_id)]
        return th_utils().utListToObj(self.catalog.searchCatalog(query))

    security.declarePublic('getDefinition')
    def getDefinition(self, concept_id='', lang=''):
        """ """
        query = [('meta_type',DEFINITION_ITEM_METATYPE),
                 ('concept_id',concept_id),
                 ('langcode',lang)]
        return th_utils().utListToObj(self.catalog.searchCatalog(query))

    security.declarePublic('getSource')
    def getSource(self, source_id=''):
        """ """
        query = [('meta_type',SOURCE_ITEM_METATYPE),
                 ('source_id',source_id)]
        return th_utils().utListToObj(self.catalog.searchCatalog(query))

    security.declarePublic('getScopeNote')
    def getScopeNote(self, concept_id='', lang=''):
        """ """
        query = [('meta_type',SCOPE_ITEM_METATYPE),
                 ('concept_id',concept_id),
                 ('langcode',lang)]
        return th_utils().utListToObj(self.catalog.searchCatalog(query))

    security.declarePublic('getThemeByID')
    def getThemesForConcept(self, concept_id='', lang=''):
        """ """
        results= []
        add_theme_trans = results.append

        query = [('meta_type',THEME_RELATION_ITEM_METATYPE),
                 ('concept_id',concept_id)]
        th_relations = self.catalog.searchCatalog(query)

        for rel_ob in th_relations:
            th_ob = self.getThemeByID(rel_ob.theme_id, lang)
            if th_ob:   add_theme_trans(th_ob)
            else:       add_theme_trans(DummyTheme(th_id, ''))

        return results

    security.declarePublic('getThemesByConceptId')
    def getThemesByConceptId(self, concept_id=''):
        """ """
        query = [('meta_type',THEME_RELATION_ITEM_METATYPE),
                 ('concept_id',concept_id)]
        return self.catalog.searchCatalog(query)

    security.declarePublic('getAllConcepts')
    def getAllConcepts(self):
        """ """
        query = [('meta_type',CONCEPT_ITEM_METATYPE)]
        return th_utils().utSortObjsListByAttr(self.catalog.searchCatalog(query), 'concept_id', 0)

    security.declarePublic('getConceptRelations')
    def getConceptRelations(self, concept_id=''):
        """ """
        query = [('meta_type',CONCEPT_RELATION_ITEM_METATYPE),
                 ('concept_id',concept_id)]
        return self.catalog.searchCatalog(query)

    security.declarePublic('getTranslations')
    def getTranslations(self, concept_id=''):
        """ """
        query = [('meta_type',TERM_ITEM_METATYPE),
                 ('concept_id',concept_id)]
        return self.catalog.searchCatalog(query)

    security.declarePublic('getLanguages')
    def getLanguages(self):
        """ """
        return self.catalog.uniqueValuesFor('langcode')

    security.declarePublic('getThemesList')
    def getThemesList(self, lang=''):
        """ return the themes list """
        results= []
        add_theme_trans = results.append

        themes_list = []
        add_theme_id = themes_list.append

        query = [('meta_type',THEME_RELATION_ITEM_METATYPE)]
        th_relations = self.catalog.searchCatalog(query)

        for rel_ob in th_relations:
            theme_id = rel_ob.theme_id
            if theme_id not in themes_list: add_theme_id(theme_id)

        for th_id in themes_list:
            th_ob = self.getThemeByID(th_id, lang)
            if th_ob:   add_theme_trans(th_ob)
            else:       add_theme_trans(DummyTheme(th_id, ''))

        return th_utils().utSortObjsByLocaleAttr(results, 'theme_name', 0, lang)

    security.declarePublic('getThemeConcept')
    def getThemeConcept(self, theme_id='', lang=''):
        """ """
        #get concepts
        query = [('meta_type', THEME_RELATION_ITEM_METATYPE),
                 ('theme_id', theme_id)]
        l_relations = self.catalog.searchCatalog(query)

        #get terms
        l_results = []
        add_result = l_results.append
        for item in l_relations:
            term_ob = self.getConceptTranslation(item.concept_id, lang)
            add_result(term_ob)
        return th_utils().utSortObjsByLocaleAttr(l_results, 'concept_name', 0, lang)

    security.declarePublic('getConceptDetails')
    def getConceptDetails(self, concept_id='', lang=''):
        """ """
        #the result list will contain:
        #   0: term_ob
        #   1: theme_list
        #   2: broader_list
        #   3: narrower_list
        #   4: related_list
        #   5: alt_term_ob
        #   6: translation_list
        #   7: definition
        #   8: scope_note
        #   9: term_source
        #  10: definition_source

        result=[]
        concept_ob = self.getConceptByID(concept_id)

        #term_ob
        term_ob = self.getTermByID(concept_id, lang)

        #term_source
        term_source = []
        if term_ob:
            for source_id in term_ob.source_id.split(' '):
                if source_id: term_source.append(self.getSource(source_id))

        #theme_list
        theme_list = self.getThemesForConcept(concept_id, lang)

        #relations lists
        broader_list = []
        narrower_list =[]
        related_list =[]

        relations_list = self.getConceptRelations(concept_id)
        for item in relations_list:
            if item.relation_type == '1':
                broader_list.append(item)
            elif item.relation_type == '2':
                narrower_list.append(item)
            elif item.relation_type == '3':
                related_list.append(item)

        #TODO: should return lists of term objects sorted instead of concept_relation objects
#        broader_list =  th_utils().utSortObjsByLocaleAttr(broader_list, 'concept_id', 0, lang)
#        narrower_list = th_utils().utSortObjsByLocaleAttr(narrower_list, 'concept_id', 0, lang)
#        related_list =  th_utils().utSortObjsByLocaleAttr(related_list, 'concept_id', 0, lang)

        #alt_term_ob
        alt_term_ob = self.getAltTermByID(concept_id, lang)

        #translation list
        translation_list = self.getTranslations(concept_id)

        #definition_ob
        definition_ob = self.getDefinition(concept_id, lang)

        #definition_source
        definition_source = []
        if definition_ob:
            for source_id in definition_ob.source_id.split(' '):
                if source_id: definition_source.append(self.getSource(source_id))

        #scope_ob
        scope_ob = self.getScopeNote(concept_id, lang)

        return (term_ob, theme_list, broader_list, narrower_list, related_list, alt_term_ob, translation_list,
                definition_ob, scope_ob, term_source, definition_source)


    #thesaurus search
    security.declarePublic('eliminateDuplicates')
    def eliminateDuplicates(self, p_objects):
        """Eliminate duplicates from a list of objects (with ids)"""
        dict = {}
        for l_object in p_objects:
            dict[l_object.concept_id] = l_object
        return dict.values()

    security.declarePublic('searchThesaurus')
    def searchThesaurus(self, query, lang=''):
        """ search thesaurus """
        results = []
        if not lang: lang = self.gl_get_selected_language()

        #search in terms
        l_query = [('meta_type',TERM_ITEM_METATYPE),
                   ('concept_name',query),
                   ('langcode',lang)]
        results.extend(self.catalog.searchCatalog(l_query))

        #search in definitions
        l_query = [('meta_type',DEFINITION_ITEM_METATYPE),
                   ('definition',query),
                   ('langcode',lang)]
        for def_ob in self.catalog.searchCatalog(l_query):
            results.append(self.getTermByID(def_ob.concept_id, lang))

        return th_utils().utSortObjsByLocaleAttr(self.eliminateDuplicates(results), 'concept_name', 0, lang)

    security.declarePublic('searchThesaurus')
    def searchThesaurusNames(self, query, lang=''):
        """ search thesaurus """
        results = []
        if not lang: lang = self.gl_get_selected_language()

        #search in terms
        l_query = [('meta_type',TERM_ITEM_METATYPE),
                   ('concept_name',query),
                   ('langcode',lang)]
        results.extend(self.catalog.searchCatalog(l_query))

        return th_utils().utSortObjsByLocaleAttr(self.eliminateDuplicates(results), 'concept_name', 0, lang)


    #RDF getters
    security.declarePublic('GetLabelsRDF')
    def GetLabelsRDF(self, rdf_lang, REQUEST=None):
        """."""
        if REQUEST: return REQUEST.RESPONSE.redirect('%s/thesaurus-labels.rdf?langcode=%s' % (self.getThesaurusPath(), rdf_lang))

    security.declarePublic('GetThemesRDF')
    def GetThemesRDF(self, rdf_lang, REQUEST=None):
        """."""
        if REQUEST: return REQUEST.RESPONSE.redirect('%s/thesaurus-themes-labels.rdf?langcode=%s' % (self.getThesaurusPath(), rdf_lang))

    security.declarePublic('alias_container_utXmlEncode')
    alias_container_utXmlEncode = th_utils().utXmlEncode


    #management tabs
    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =       PageTemplateFile('zpt/NaayaThesaurus/properties', globals())

    security.declareProtected(view_management_screens, 'th_messages_box')
    th_messages_box =       PageTemplateFile('zpt/NaayaThesaurus/messages_box', globals())

    security.declareProtected(view_management_screens, 'style_console_css')
    style_console_css =     PageTemplateFile('zpt/NaayaThesaurus/style_console', globals())

    security.declarePublic('index_html')
    index_html =            PageTemplateFile('zpt/NaayaThesaurus/thematic', globals())

    security.declarePublic('view_html')
    view_html =            PageTemplateFile('zpt/NaayaThesaurus/view', globals())

    security.declarePublic('alphabetic_html')
    alphabetic_html =       PageTemplateFile('zpt/NaayaThesaurus/alphabetic', globals())

    security.declarePublic('hierarchical_html')
    hierarchical_html =     PageTemplateFile('zpt/NaayaThesaurus/hierarchical', globals())

    security.declarePublic('thematic_html')
    thematic_html =         PageTemplateFile('zpt/NaayaThesaurus/thematic', globals())

    security.declarePublic('theme_concept_html')
    theme_concept_html =    PageTemplateFile('zpt/NaayaThesaurus/theme_concept', globals())

    security.declarePublic('concept_html')
    concept_html =          PageTemplateFile('zpt/NaayaThesaurus/concept', globals())

    security.declareProtected(view_management_screens, 'rdfs_html')
    rdfs_html =             PageTemplateFile('zpt/NaayaThesaurus/rdfs', globals())

    security.declarePublic('search_html')
    search_html =           PageTemplateFile('zpt/NaayaThesaurus/search', globals())

    security.declarePublic('alphabetic_map_html')
    alphabetic_map_html =   PageTemplateFile('zpt/NaayaThesaurus/alphabetic_map', globals())

    security.declarePublic('GlossMap_html')
    GlossMap_html =         PageTemplateFile('zpt/NaayaThesaurus/GlossMap', globals())

    def isThAdministrator(self):
        """Test if current user is administrator"""
        return self.REQUEST.AUTHENTICATED_USER.has_role('Manager', self) or self.REQUEST.AUTHENTICATED_USER.has_role('Administrator', self)

InitializeClass(NyThesaurus)


#Dummy objects:
class DummyTerm:
    """ """

    def __init__(self, concept_id, concept_name):
        self.concept_id =   concept_id
        self.concept_name = concept_name

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(DummyTerm)


class DummyTheme:
    """ """

    def __init__(self, theme_id, theme_name):
        self.theme_id =     theme_id
        self.theme_name =   theme_name

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(DummyTheme)
