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
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
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

# product imports
from constants  import *
from utils      import utils, catalog_utils

# constants
LABEL_OBJECT = 'Glossary element'

class ElementBasic:
    """ define the basic properties for NyGlossaryElement """

    def __init__(self, title, source, contributor):
        """ constructor """
        self.title = title
        self.source = source
        self.contributor = contributor


manage_addGlossaryElement_html = PageTemplateFile('zpt/NaayaGlossaryElement/add', globals())

def manage_addGlossaryElement(self, id='', title='', source='', subjects=[], contributor='', approved=1, REQUEST=None):
    """ adds a new NyGlossaryElement object """
    ob = NyGlossaryElement(id, title, source, subjects, contributor, approved)
    self._setObject(id, ob)
    element_obj = self._getOb(id)
    element_obj.subjects = self.get_subject_by_codes(subjects)
    element_obj.load_translations_list()

    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class NyGlossaryElement(SimpleItem, ElementBasic, utils, catalog_utils):
    """ NyGlossaryElement """

    meta_type = NAAYAGLOSSARY_ELEMENT_METATYPE
    meta_label = LABEL_OBJECT
    product_name = NAAYAGLOSSARY_PRODUCT_NAME
    icon = 'misc_/NaayaGlossary/element.gif'

    manage_options = (
        {'label':'Translations',    'action':'translations_html'},
        {'label':'Properties',      'action':'properties_html'},
        {'label':"View",            'action':'index_html'},
        {'label':'Undo',            'action':'manage_UndoForm'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title, source, subjects, contributor, approved):
        """ constructor """
        self.id =           id
        self.subjects =     subjects
        self.approved =     approved
        ElementBasic.__dict__['__init__'](self, title, source, contributor)

    def is_published(self): return self.approved

    #####################
    #  BASIC PROPERTIES #
    #####################
    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'manageBasicProperties')
    def manageBasicProperties(self, title='', source='', subjects=[], contributor='',
                              approved=0, REQUEST=None):
        """ manage basic properties for NyGlossaryElement """
        self.title = title
        self.source = source
        self.subjects = self.get_subject_by_codes(subjects)
        self.approved = approved
        self._p_changed = 1
        self.cu_recatalog_object(self)
        if REQUEST: return REQUEST.RESPONSE.redirect('properties_html?save=ok')

    security.declarePrivate("manage_afterAdd")
    def manage_afterAdd(self, item, container):
        """ this method is called, whenever _setObject in ObjectManager gets called """
        SimpleItem.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.cu_catalog_object(self)

    security.declarePrivate("manage_beforeDelete")
    def manage_beforeDelete(self, item, container):
        """ this method is called, when the object is deleted """
        SimpleItem.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.cu_uncatalog_object(self)

    #########################
    #     THEME FUNCTIONS   #
    #########################
    def code_in_subjects(self, code):
        """ check if code is in the list """
        for subj_info in self.subjects:
            if subj_info['code'] == code:
                return 1
        return 0

    def get_subjects(self):
        """ get the languages """
        self.utSortListOfDictionariesByKey(self.subjects, 'code')
        return self.subjects

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'set_subjects')
    def set_subjects(self, code, name):
        """ set the languages """
        append = self.subjects.append
        append({'code':code, 'name':name})

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'del_subject')
    def del_subject(self, code):
        """ remove a language from list """
        for subj_info in self.subjects:
            if subj_info['code'] == code:
                self.subjects.remove(subj_info)

    #################################
    #  NAME TRANSLATIONS FUNCTIONS  #
    #################################
    def get_translation_by_language(self, language):
        """ get translation by language """
        try:    return getattr(self, language)
        except: return ''

    def check_if_no_translations(self):
        """ check if translation """
        for lang in self.get_english_names():
            if self.get_translation_by_language(lang) != '':
                return 1
        return 0

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'set_translations_list')
    def set_translations_list(self, language, translation):
        """ set the languages """
        setattr(self, language, translation)

    def load_translations_list (self):
        """ load languages """
        for lang in self.get_english_names():
            setattr(self, lang, '')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'manageNameTranslations')
    def manageNameTranslations(self, lang_code='', translation='', REQUEST=None):
        """ save translation for a language """
        self.set_translations_list(lang_code, translation)
        self.cu_recatalog_object(self)
        if REQUEST: return REQUEST.RESPONSE.redirect('translations_html?tab=0')

    #######################################
    #  DEFINITION TRANSLATIONS FUNCTIONS  #
    #######################################
    def definition_lang(self, language):
        """ return definition translation property name """
        return 'def_%s' % language

    def get_def_trans_by_language(self, language):
        """ get translation by language """
        try:    return getattr(self, self.definition_lang(language))
        except: return ''

    def check_if_no_def_trans(self):
        """ check if translation """
        for lang in self.get_english_names():
            if self.get_def_trans_by_language(lang) != '':
                return 1
        return 0

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'set_def_trans_list')
    def set_def_trans_list(self, language, translation):
        """ set the languages """
        setattr(self, self.definition_lang(language), translation)

    def load_def_trans_list (self):
        """ load languages """
        for lang in self.get_english_names():
            setattr(self, self.definition_lang(lang), '')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'manageDefinitionTranslations')
    def manageDefinitionTranslations(self, lang_code='', translation='', REQUEST=None):
        """ save translation for a language """
        self.set_def_trans_list(lang_code, translation)
        self.cu_recatalog_object(self)
        if REQUEST: return REQUEST.RESPONSE.redirect('translations_html?tab=1')

    #####################
    #   MANAGEMENT TABS #
    #####################
    security.declareProtected(view_management_screens, 'translations_html')
    translations_html =     PageTemplateFile("zpt/NaayaGlossaryElement/translations", globals())

    security.declareProtected(view_management_screens, 'name_trans_html')
    name_trans_html =     PageTemplateFile("zpt/NaayaGlossaryElement/name_trans", globals())

    security.declareProtected(view_management_screens, 'definition_trans_html')
    definition_trans_html =     PageTemplateFile("zpt/NaayaGlossaryElement/definition_trans", globals())

    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =       PageTemplateFile("zpt/NaayaGlossaryElement/properties", globals())

    view_elements_html =    PageTemplateFile("zpt/NaayaGlossaryElement/view_elements", globals())
    index_html =            PageTemplateFile("zpt/NaayaGlossaryElement/index", globals())

    #################
    #   SITE MAP    #
    #################
    security.declarePublic('getGlossaryObTree')
    def getGlossaryObTree(self):
        """ """
        return None

InitializeClass(NyGlossaryElement)
