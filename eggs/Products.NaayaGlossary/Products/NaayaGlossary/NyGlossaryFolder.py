import Products
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens
from zope import interface
from zope import event

import NyGlossaryElement
from constants import *
from utils import utils, catalog_utils
from Products.NaayaGlossary.parsers.import_parsers import glossary_export
from interfaces import INyGlossaryFolder
from events import ItemTranslationChanged
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

LABEL_OBJECT = 'Glossary folder'

manage_addGlossaryFolder_html = PageTemplateFile('zpt/NaayaGlossaryFolder/add',
        globals())

def manage_addGlossaryFolder(self, id, title='', subjects=[], source='',
        contributor='', approved=1, REQUEST=None):
    """ adds a new NyGlossaryFolder object """
    ob = NyGlossaryFolder(id, title, subjects, source, contributor, approved)
    self._setObject(id, ob)

    #translation related
    fld_obj = self._getOb(id)
    fld_obj.subjects = self.get_subject_by_codes(subjects)
    fld_obj.load_translations_list()
    #imported here to avoid cross-import errors
    from NyGlossary import set_default_translation
    set_default_translation(fld_obj)

    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)


class NyGlossaryFolder(Folder, utils, glossary_export, catalog_utils):
    """ NyGlossaryFolder """

    interface.implements(INyGlossaryFolder)
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
        for term in self.utSortObjsListByAttr(id_lst, 'id', 0):
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

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'manage_folder_properties')
    def manage_folder_properties(self, title='', subjects=[], source='', contributor='', approved=0, REQUEST=None):
        """ folder properties """
        self.title =        title
        self.subjects =     self.get_subject_by_codes(subjects)
        self.source =       source
        self.contributor =  contributor
        self.approved =     approved
        if REQUEST: REQUEST.RESPONSE.redirect('properties_html?save=ok')

    #########################
    #   MANAGEMENT TABS     #
    #########################
    index_html =                PageTemplateFile('zpt/NaayaGlossaryFolder/index', globals())

    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =    NaayaPageTemplateFile('zpt/NaayaGlossaryFolder/properties', globals(), 'glossary_folder_properties')

    security.declareProtected(view_management_screens, 'export_html')
    export_html =               PageTemplateFile("zpt/NaayaGlossaryFolder/export", globals())

    # stealing templates from NyGlossaryElement
    security.declareProtected(view_management_screens, 'translations_html')
    translations_html =     PageTemplateFile("zpt/NaayaGlossaryElement/translations", globals())

    security.declareProtected(view_management_screens, 'name_trans_html')
    name_trans_html =     PageTemplateFile("zpt/NaayaGlossaryElement/name_trans", globals())

    security.declareProtected(view_management_screens, 'definition_trans_html')
    definition_trans_html =     PageTemplateFile("zpt/NaayaGlossaryElement/definition_trans", globals())

    #################################
    #  NAME TRANSLATIONS FUNCTIONS  #
    #################################
    def is_published(self): return self.approved

    def get_translation_by_language(self, language):
        """ get translation by language """
        try:    return getattr(self.aq_base, language)
        except: return ''

    def get_translation_by_language_for_js(self, language):
        """ get translation by language for the javascript code"""
        try:
            translation = getattr(self.aq_base, language)
            if not translation:
                translation = self.title_or_id()
        except AttributeError:
            translation = self.title_or_id()
        return translation.replace('_', ' ')

    def check_if_no_translations(self):
        """ check if translations['translation'] != '': """
        for lang in self.get_english_names():
            if self.get_translation_by_language(lang) != '': return 1
        return 0

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'set_translations_list')
    def set_translations_list(self, language, translation):
        """ set the languages """
        real_self = self.aq_base
        if getattr(real_self, language, u"") == translation:
            # no need to do anything, so let's avoid generating a transaction
            return
        if translation == "":
            if hasattr(real_self, language):
                delattr(real_self, language)
        else:
            setattr(real_self, language, translation)
        event.notify(ItemTranslationChanged(self, language, translation))

    def load_translations_list(self):
        """ load languages """
        for lang in self.get_english_names():
            self.set_translations_list(lang, '')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'manageNameTranslations')
    def manageNameTranslations(self, lang_code='', translation='', REQUEST=None):
        """ save translation for a language """
        self.set_translations_list(lang_code, translation)
        if REQUEST: return REQUEST.RESPONSE.redirect('translations_html')

    #######################################
    #  DEFINITION TRANSLATIONS FUNCTIONS  #
    #######################################
    def get_def_trans_by_language(self, language):
        """ get translation by language """
        return getattr(self.aq_base, self.definition_lang(language), '')

    def check_if_no_def_trans(self):
        """ check if translation """
        for lang in self.get_english_names():
            if self.get_def_trans_by_language(lang) != '':
                return 1
        return 0

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'set_def_trans_list')
    def set_def_trans_list(self, language, translation):
        """ set the languages """
        self.set_translations_list(self.definition_lang(language), translation)

    def load_def_trans_list(self):
        """ load languages """
        for lang in self.get_english_names():
            self.set_translations_list(self.definition_lang(lang), '')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'manageDefinitionTranslations')
    def manageDefinitionTranslations(self, lang_code='', translation='', REQUEST=None):
        """ save translation for a language """
        self.set_def_trans_list(lang_code, translation)
        if REQUEST: return REQUEST.RESPONSE.redirect('translations_html?tab=1')

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
        return self.utSortObjsListByAttr(self.objectValues([NAAYAGLOSSARY_ELEMENT_METATYPE]), 'id', 0)

    def hasGlossElems(self):
        """ """
        return len(self.getGlossElems())

    security.declareProtected(view_management_screens, 'manage_tabs')
    def manage_tabs(self):
        # we override manage_tabs to insert warning about synchronized glossary
        if self.sync_remote_url:
            extra_html = self.sync_info_text(zmi=True)
        else:
            extra_html = ''
        return super(NyGlossaryFolder, self).manage_tabs() + extra_html

InitializeClass(NyGlossaryFolder)
