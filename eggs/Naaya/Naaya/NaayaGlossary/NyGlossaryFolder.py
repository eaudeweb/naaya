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

# Zope imports
import Products
from OFS.Folder                                 import Folder
from AccessControl                              import ClassSecurityInfo
from Globals                                    import InitializeClass
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from AccessControl.Permissions                  import view_management_screens, view

# product imports
import NyGlossaryElement
from constants                                          import *
from utils                                              import utils, catalog_utils
from Products.NaayaGlossary.parsers.import_parsers      import glossary_export

#constants
LABEL_OBJECT = 'Glossary folder'

manage_addGlossaryFolder_html = PageTemplateFile('zpt/NaayaGlossaryFolder/add', globals())

def manage_addGlossaryFolder(self, id, title='', subjects=[], source='', contributor='', approved=1, REQUEST=None):
    """ adds a new NyGlossaryFolder object """
    ob = NyGlossaryFolder(id, title, subjects, source, contributor, approved)
    self._setObject(id, ob)

    #translation related
    fld_obj = self._getOb(id)
    fld_obj.subjects = self.get_subject_by_codes(subjects)
    fld_obj.load_translations_list()

    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)


class NyGlossaryFolder(Folder, utils, glossary_export, catalog_utils):
    """ NyGlossaryFolder """

    meta_type =     NAAYAGLOSSARY_FOLDER_METATYPE
    meta_label = LABEL_OBJECT
    product_name =  NAAYAGLOSSARY_PRODUCT_NAME
    icon =          'misc_/NaayaGlossary/folder.gif'

    manage_options = ((Folder.manage_options[0],) +
                ({'label':'View',               'action':'index_html'},
                {'label':'Properties',          'action':'properties_html'},
                {'label':'Translations',        'action':'translations_html'},
                {'label':'Export',              'action':'export_html'},
                {'label':'Undo',                'action':'manage_UndoForm'},)
                )

    meta_types = (
        {'name': NAAYAGLOSSARY_ELEMENT_METATYPE, 
        'action': 'manage_addGlossaryElement_html', 
        'product': NAAYAGLOSSARY_PRODUCT_NAME
        },
        {'name': NAAYAGLOSSARY_FOLDER_METATYPE, 
        'action': 'manage_addGlossaryFolder_html', 
        'product': NAAYAGLOSSARY_PRODUCT_NAME
        },)

    security = ClassSecurityInfo()

    def __init__(self, id, title, subjects, source, contributor, approved):
        """ constructor """
        #basic properties
        self.id =           id
        self.title =        title

        #translate related
        self.subjects =         subjects
        self.source =           source
        self.contributor =      contributor
        self.approved =         approved

    manage_addGlossaryElement_html = NyGlossaryElement.manage_addGlossaryElement_html
    manage_addGlossaryElement = NyGlossaryElement.manage_addGlossaryElement

    manage_addGlossaryFolder_html = manage_addGlossaryFolder_html
    manage_addGlossaryFolder = manage_addGlossaryFolder

    #######################
    #   DISPLAY FUNCTIONS #
    #######################
    def get_object_list(self):
        """ return all id sorted objects from a folder """
        id_lst = []
        obj_lst = []
        for obj in self.objectValues([NAAYAGLOSSARY_ELEMENT_METATYPE]):
            id_lst.append(obj.id)
        id_lst.sort()
        for term in id_lst:
            ob = self._getOb(term)
            obj_lst.append(ob)
        return obj_lst

    def get_objets_sorted(self, lang_code):
        """ """
        l_elems = self.objectValues([NAAYAGLOSSARY_ELEMENT_METATYPE])
        return self.utSortObjsListByAttr(l_elems, self.get_language_by_code(lang_code), 0)

    ##########################
    #   META TYPES FUNCTIONS #
    ##########################
    def all_meta_types(self): return self.meta_types

    def getMetaTypes(self):
        """ return meta_types list  """
        return [x['name'] for x in Products.meta_types]

    def manage_folder_properties(self, title='', subjects=[], source='', contributor='', approved=0, REQUEST=None):
        """ folder properties """
        self.title =        title
        self.subjects =     self.get_subject_by_codes(subjects)
        self.source =       source
        self.contributor =  contributor
        self.approved =     approved
        if REQUEST: REQUEST.RESPONSE.redirect('properties_html?save=ok')

    def manage_afterAdd(self, item, container):
        """ this method is called, whenever _setObject in ObjectManager gets called """
        Folder.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.cu_catalog_object(self)

    def manage_beforeDelete(self, item, container):
        """ this method is called, when the object is deleted """
        Folder.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.cu_uncatalog_object(self)

    #########################
    #   MANAGEMENT TABS     #
    #########################
    index_html =                PageTemplateFile('zpt/NaayaGlossaryFolder/index', globals())

    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =    PageTemplateFile('zpt/NaayaGlossaryFolder/properties', globals())

    security.declareProtected(view_management_screens, 'export_html')
    export_html =               PageTemplateFile("zpt/NaayaGlossaryFolder/export", globals())

    security.declareProtected(view_management_screens, 'translations_html')
    translations_html =     PageTemplateFile("zpt/NaayaGlossaryFolder/translations", globals())

    ############################
    #  TRANSLATIONS FUNCTIONS  #
    ############################
    def is_published(self): return self.approved

    def get_translation_by_language(self, language):
        """ get translation by language """
        try:    return getattr(self, language)
        except: return ''

    def check_if_no_translations(self):
        """ check if translations['translation'] != '': """
        for lang in self.get_english_names():
            if getattr(self, lang) != '': return 1
        return 0

    def set_translations_list(self, language, translation):
        """ set the languages """
        setattr(self, language, translation)

    def load_translations_list (self):
        """ load languages """
        for lang in self.get_english_names():
            setattr(self, lang, '')

    def manageFolderTranslations(self, lang_code='', translation='', REQUEST=None):
        """ save translation for a language """
        self.set_translations_list(lang_code, translation)
        self.cu_recatalog_object(self)
        if REQUEST: return REQUEST.RESPONSE.redirect('translations_html')

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

    def set_subjects(self, code, name):
        """ set the languages """
        append = self.subjects.append
        append({'code':code, 'name':name})

    def del_subject(self, code):
        """ remove a language from list """
        for subj_info in self.subjects:
            if subj_info['code'] == code:
                self.subjects.remove(subj_info)

    #################
    #   SITE MAP    #
    #################
    security.declarePublic('getGlossaryObTree')
    def getGlossaryObTree(self):
        """ """
        results = []
        for item in self.objectValues([NAAYAGLOSSARY_FOLDER_METATYPE]):
            if item.is_published(): results.append(item)
        return self.utSortObjsListByAttr(results, self.get_language_by_code(self.getSelectedLang()), 0)

    def hasGlossFolders(self):
        """ """
        return len(self.objectValues([NAAYAGLOSSARY_FOLDER_METATYPE]))

    def getGlossElems(self):
        """ """
        return self.objectValues([NAAYAGLOSSARY_ELEMENT_METATYPE])

    def hasGlossElems(self):
        """ """
        return len(self.getGlossElems())

InitializeClass(NyGlossaryFolder)
