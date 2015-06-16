from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens
from zope import interface
from zope import event
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

# product imports
from constants import *
from utils import utils, catalog_utils
from interfaces import INyGlossaryElement
from events import ItemTranslationChanged

# constants
LABEL_OBJECT = 'Glossary element'

class ElementBasic:
    """ define the basic properties for NyGlossaryElement """

    def __init__(self, title, source, contributor):
        """ constructor """
        self.title = title
        self.source = source
        self.contributor = contributor


manage_addGlossaryElement_html = PageTemplateFile('zpt/NaayaGlossaryElement/add',
        globals())

def manage_addGlossaryElement(self, id='', title='', source='', subjects=[],
        contributor='', approved=1, REQUEST=None):
    """ adds a new NyGlossaryElement object """
    ob = NyGlossaryElement(id, title, source, subjects, contributor, approved)
    self._setObject(id, ob)
    element_obj = self._getOb(id)
    element_obj.subjects = self.get_subject_by_codes(subjects)
    element_obj.load_translations_list()
    #imported here to avoid cross-import errors
    from NyGlossary import set_default_translation
    set_default_translation(element_obj)

    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class NyGlossaryElement(SimpleItem, ElementBasic, utils, catalog_utils):
    """ NyGlossaryElement """

    interface.implements(INyGlossaryElement)
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
        self.contributor = contributor
        self.approved = approved
        self._p_changed = 1
        self.cu_recatalog_object(self)
        if REQUEST: return REQUEST.RESPONSE.redirect('properties_html?save=ok')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'approveElement')
    def approveElement(self, REQUEST=None):
        """ used for approval link in basket of approvals"""
        self.approved = 1
        if REQUEST:
            return REQUEST.RESPONSE.redirect('index_approvals_html')

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
        return getattr(self.aq_base, language, '')

    def get_translation_by_language_for_js(self, language):
        """ get translation by language for the javascript code"""
        try:
            translation = self.get_translation_by_language(language)
            if not translation:
                translation = self.title_or_id()
        except AttributeError:
            translation = self.title_or_id()
        return translation.replace('_', ' ')

    def check_if_no_translations(self):
        """ check if translation """
        for lang in self.get_english_names():
            if self.get_translation_by_language(lang) != '':
                return 1
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

    def load_translations_list (self):
        """ load languages """
        for lang in self.get_english_names():
            self.set_translations_list(lang, '')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'manageNameTranslations')
    def manageNameTranslations(self, lang_code='', translation='', REQUEST=None):
        """ save translation for a language """
        self.set_translations_list(lang_code, translation)
        if REQUEST: return REQUEST.RESPONSE.redirect('translations_html?tab=0')

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
    index_html =            NaayaPageTemplateFile("zpt/NaayaGlossaryElement/index", globals(), 'glossary_element_index')

    #################
    #   SITE MAP    #
    #################
    security.declarePublic('getGlossaryObTree')
    def getGlossaryObTree(self):
        """ """
        return None

    security.declareProtected(view_management_screens, 'manage_tabs')
    def manage_tabs(self):
        # we override manage_tabs to insert warning about synchronized glossary
        if self.sync_remote_url:
            extra_html = self.sync_info_text(zmi=True)
        else:
            extra_html = ''
        return super(NyGlossaryElement, self).manage_tabs() + extra_html

InitializeClass(NyGlossaryElement)
