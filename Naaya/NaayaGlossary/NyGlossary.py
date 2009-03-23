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
# The Original Code is NaayaGlossary version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
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
from ZPublisher.HTTPRequest                     import record
from AccessControl                              import ClassSecurityInfo
from Products.ZCatalog.ZCatalog                 import ZCatalog
from Globals                                    import MessageDialog, InitializeClass
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate    import manage_addPageTemplate
from AccessControl.Permissions                  import view_management_screens, view

#Product imports
import NyGlossaryFolder
from constants                                          import *
from utils                                              import utils, catalog_utils
from parsers.xliff_parser                               import xliff_parser
from Products.NaayaCore.managers.utils                  import file_utils
from Products.NaayaGlossary.parsers.subjects_parser     import subjects_parser
from Products.NaayaGlossary.parsers.stop_words_parser   import stop_words_parser
from Products.NaayaGlossary.parsers.import_parsers      import glossary_export

#Naaya imports
from Products.NaayaCore.managers.utils import genObjectId

#constants
LABEL_OBJECT = 'Glossary'

manage_addGlossaryCentre_html = PageTemplateFile('zpt/NaayaGlossary/add', globals())
def manage_addGlossaryCentre(self, id, title='', parent_anchors=False, REQUEST=None):
    """ Adds a new NaayaGlossary object """
    ob = NyGlossary(id, title, parent_anchors)
    self._setObject(id, ob)
    obj = self._getOb(id)
    obj.loadProperties()
    obj.addCatalog()
    obj.loadRDF()

    style_css = open(join(NAAYAGLOSSARY_PATH,'zpt','NaayaGlossary','style_presentation.zpt'))
    content = style_css.read()
    style_css.close()
    manage_addPageTemplate(obj, 'style_presentation_css', title='Naaya Glossary CSS', text=content)

    obj._p_changed = 1
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)


class NyGlossary(Folder, utils, catalog_utils, glossary_export, file_utils):
    """ NyGlossary """

    __alphabets_cache = {}
    parent_anchors = False
    meta_type =     NAAYAGLOSSARY_CENTRE_METATYPE
    meta_label = LABEL_OBJECT
    product_name =  NAAYAGLOSSARY_PRODUCT_NAME
    icon =          "misc_/NaayaGlossary/glossary.gif"

    manage_options =((Folder.manage_options[0],) +
                ({'label':'Properties',         'action':'properties_html'},
                {'label':'Languages',           'action':'languages_html'},
                {'label':'Themes',              'action':'themes_html'},
                {'label':'View',                'action':'index_html'},
                {'label':'Export',              'action':'export_html'},
                {'label':'Import',              'action':'import_html'},
                {'label':'Management',          'action':'management_page_html'},
                {'label':'Undo',                'action':'manage_UndoForm'},)
                )
#Info:
#Map struct. for pick list,     'action':'GlossMap_html'
#Map alph. for pick list,       'action':'GlossMapAlph_html'
#Map alphabetical,              'action':'map_alphabetical_html'
#Map structural,                'action':'map_structural_html'


    security = ClassSecurityInfo()

    def __init__(self, id, title, parent_anchors):
        """ constructor """
        self.id =                   id
        self.title =                title
        self.languages_list =       []
        self.stop_words_list =      []
        self.subjects_list =        []
        self.approved =             1
        self.__alphabets_cache =    {}
        self.parent_anchors =       parent_anchors
        utils.__dict__['__init__'](self)
        glossary_export.__dict__['__init__'](self)

    def all_meta_types(self, interfaces=None):
        """ what can you put inside me """
        meta_types = [
            {'name': NAAYAGLOSSARY_FOLDER_METATYPE, 'action': 'manage_addGlossaryFolder_html', 'product': NAAYAGLOSSARY_PRODUCT_NAME},
        ]
        for x in Products.meta_types:
            meta_types.append(x)
        return meta_types

    manage_addGlossaryFolder_html = NyGlossaryFolder.manage_addGlossaryFolder_html
    manage_addGlossaryFolder = NyGlossaryFolder.manage_addGlossaryFolder

    def getCenterOb(self): return self
    def is_published(self): return self.approved

    #####################
    # LOAD PROPERTIES   #
    #####################
    def addCatalog(self):
        """ add the default catalog """
        id_catalog = NAAYAGLOSSARY_CATALOG_NAME
        glossary_catalog = ZCatalog(id_catalog)
        self._setObject(id_catalog, glossary_catalog)
        catalog_obj = self._getOb(id_catalog)

        #create indexes
        for lang in self.get_english_names():
            index_extra = record()
            index_extra.default_encoding = 'utf-8'
            try:    catalog_obj.manage_addIndex(self.cookCatalogIndex(lang), 'TextIndexNG2',index_extra)
            except:    pass

        try: catalog_obj.addIndex('approved', 'FieldIndex')
        except: pass
        try: catalog_obj.addIndex('bobobase_modification_time', 'FieldIndex')
        except: pass
        try: catalog_obj.addIndex('id', 'FieldIndex')
        except: pass
        try: catalog_obj.addIndex('meta_type', 'FieldIndex')
        except: pass
        try: catalog_obj.addIndex('path', 'PathIndex')
        except: pass
        try: catalog_obj.addIndex('title', 'TextIndex')
        except: pass

       #create metadata
        try: catalog_obj.addColumn('id')
        except: pass
        try: catalog_obj.addColumn('title')
        except: pass
        try: catalog_obj.addColumn('meta_type')
        except: pass
        try: catalog_obj.addColumn('bobobase_modification_time')
        except: pass
        try: catalog_obj.addColumn('summary')
        except: pass

    def mapLocalizerLangs(self):
        """ """
        results = []
        localizer_langs = self.get_languages_mapping()
        for item in localizer_langs:
            results.append({'lang':item['code'], 'english_name':item['name']})
        return results

    def loadProperties(self):
        """ load the default properties """
        self.languages_list = self.mapLocalizerLangs()
        self.load_stop_words_list()
        self.load_subjects_list()

    def load_stop_words_list(self):
        """ loads stop words properties defaults """
        stop_word_obj = stop_words_parser()
        content = self.futRead(join(NAAYAGLOSSARY_PATH, 'config', 'stop_words.xml'))
        stop_words_handler, error = stop_word_obj.parseContent(content)

        append = self.stop_words_list.append
        for word in stop_words_handler.stop_words:
            append({'stop_word':word.text})
        self._p_changed = 1

    def load_subjects_list (self):
        """ loads subjects properties defaults """
        subjects_obj = subjects_parser()
        content = self.futRead(join(NAAYAGLOSSARY_PATH,'config', 'subjects.xml'))
        subjects_handler, error = subjects_obj.parseContent(content)
        for code in subjects_handler.subjects:
            self.set_subjects_list(code.code, code.name)
        self._p_changed = 1

    ######################
    # TEST PERMISSIONS   #
    ######################
    def getAuthenticatedUser(self):
        """ return the authenticated user """
        return self.REQUEST.AUTHENTICATED_USER.getUserName()

    #####################
    # BASIC FUNCTIONS   #
    #####################
    def getGlossaryCatalog(self):
        """ return the glossary catalog object """
        return self._getOb(NAAYAGLOSSARY_CATALOG_NAME)

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'manageBasicProperties')
    def manageBasicProperties(self, title='', approved=0, parent_anchors=0, REQUEST=None):
        """ manage basic properties for NyGlossary """
        self.title =        title
        self.approved =     approved
        self.parent_anchors = parent_anchors
        self._p_changed =   1
        if REQUEST: return REQUEST.RESPONSE.redirect('properties_html?save=ok')

    #######################
    #   THEME FUNCTIONS   #
    #######################
    def get_subjects_list(self):
        """ get the subjects """
        self.utSortListOfDictionariesByKey(self.subjects_list, 'code')
        return self.subjects_list

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'set_subjects_list')
    def set_subjects_list(self, code, name):
        """ set the subjects """
        self.subjects_list.append({'code':code, 'name':name})

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'del_subject_from_list')
    def del_subject_from_list(self, code):
        """ remove a subjects from list """
        for subj_info in self.subjects_list:
            if subj_info['code'] == code:
                self.subjects_list.remove(subj_info)

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'update_subject_in_list')
    def update_subject_in_list(self, old_code, code, name):
        """ finds the subject with the given code and updates its data """
        for subj in self.subjects_list:
            if subj['code'] == old_code:
                subj['code'] = code
                subj['name'] = name

    def get_subject_by_name(self, names):
        """ return corresponding codes """
        results = []
        names = self.utConvertToList(names)
        for subj_info in self.subjects_list:
            if subj_info['name'] in names:
                results.append(subj_info['code'])
        return results

    def get_subject_by_codes(self, codes):
        """ return the subjects list """
        results = []
        codes = self.utConvertToList(codes)
        for subj_info in self.subjects_list:
            if subj_info['code'] in codes:
                results.append(subj_info)
        return results

    def check_subjects_exists(self, code):
        """ check if this subject exists """
        ret = 1
        for l_code in self.subjects_list:
            if l_code['code'] == code:
                ret = 0
        return ret

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'manageThemesProperties')
    def manageThemesProperties(self, ids=[], old_code='', code='', name='', REQUEST=None):
        """ manage subjects for NyGlossary """
        if self.utAddObjectAction(REQUEST):
            if string.strip(code) == '' or string.strip(name) == '':
                return REQUEST.RESPONSE.redirect('themes_html?tab=0')
            else:
                if self.check_subjects_exists(code):
                    self.set_subjects_list(code, name)
                    self._p_changed = 1
                else:
                    return REQUEST.RESPONSE.redirect('themes_html?tab=0')
        elif self.utUpdateObjectAction(REQUEST):
            if string.strip(code) == '' or string.strip(name) == '':
                return REQUEST.RESPONSE.redirect('themes_html?tab=0')
            else:
                self.del_subject_from_list(old_code)
                self.set_subjects_list(code, name)
                self._p_changed = 1
        elif self.utDeleteObjectAction(REQUEST):
            if not ids or len(ids) == 0:
                return REQUEST.RESPONSE.redirect('themes_html?tab=0')
            for subj in self.utConvertToList(ids):
                self.del_subject_from_list(subj)
            self._p_changed = 1
        if REQUEST: return REQUEST.RESPONSE.redirect('themes_html?tab=0&amp;save=ok')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'addTheme')
    def addTheme(self, code='', name=''):
        """ Add a new theme with the given code and name """
        code, name = string.strip(code), string.strip(name)
        if not name:
            return self.REQUEST.RESPONSE.redirect('index_themes_html')
        if not code:
            code = genObjectId(name)
        if not code in [subj['code'] for subj in self.subjects_list]:
            self.set_subjects_list(code, name)
            self._p_changed = 1
            self.setSessionInfo(['Theme added.'])
        else:
            self.setSessionErrors(["Code already exists."])
        return self.REQUEST.RESPONSE.redirect('index_themes_html')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'deleteThemes')
    def deleteThemes(self, ids=[]):
        """ Delete the themes with the given ids """
        if not ids or len(ids) == 0:
            return self.REQUEST.RESPONSE.redirect('index_themes_html')
        for subj in self.utConvertToList(ids):
            self.del_subject_from_list(subj)
        self._p_changed = 1
        self.setSessionInfo(['Themes deleted.'])
        return self.REQUEST.RESPONSE.redirect('index_themes_html')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'updateTheme')
    def updateTheme(self, old_code='', code='', name='', lang_codes=[], translations=[]):
        """ Change theme name or code """
        code, name = string.strip(code), string.strip(name)
        if not code or not name:
            return self.REQUEST.RESPONSE.redirect('index_themes_html')
        if code == old_code:
            self.update_subject_in_list(old_code, code, name)
            self._p_changed = 1
            for lang in lang_codes:
                self.manageDefinitionTranslations(code, lang, translations[lang_codes.index(lang)])
            self.setSessionInfo(['Saved changes.'])
        elif code != old_code and not code in [subj['code'] for subj in self.subjects_list]:
            self.update_subject_in_list(old_code, code, name)
            self._p_changed = 1
            for lang in lang_codes:
                self.manageDefinitionTranslations(code, lang, translations[lang_codes.index(lang)])
            self.setSessionInfo(['Saved changes.'])
        else:
            self.setSessionErrors(["Code already exists."])
            return self.REQUEST.RESPONSE.redirect('index_themes_html?code=%s' % old_code)
        return self.REQUEST.RESPONSE.redirect('index_themes_html')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'updateGlossaryItem')
    def updateGlossaryItem(self, item_title='', item_subjects='', item_source='',
                           item_contributor='', item_approved='', item_translation=[],
                           item_meta_type='', item_lang_code=[], item_url=''):
        """ """

        #do folder update
        if item_meta_type == "Naaya Glossary Folder":
            #update properties
            folder = self.getGlossaryChild(item_url)
            if folder:
                folder.manage_folder_properties(item_title, item_subjects,
                                                item_source, item_contributor,
                                                item_approved)
                #update translations
                for translation in item_translation:
                    lang_code = item_lang_code[item_translation.index(translation)]
                    folder.manageFolderTranslations(lang_code, translation)
            return self.REQUEST.RESPONSE.redirect('index_html?item=%s' % item_url)

        elif item_meta_type == "Naaya Glossary Element":
            #do element update
            element = self.getGlossaryChild(item_url)
            if element:
                element.manageBasicProperties(item_title, item_source,
                                              item_subjects, item_contributor,
                                              item_approved)
                for translation in item_translation:
                    lang_code = item_lang_code[item_translation.index(translation)]
                    folder.manageNameTranslations(lang_code, translation)

    #########################
    #   THEME TRANSLATIONS  #
    #########################
    def getThemeByCode(self, code):
        """ """
        return self.get_subject_by_codes(code)[0]

    def get_theme_trans_by_language(self, code, language):
        """ get translation by language """
        try:
            theme = self.getThemeByCode(code)
            return theme[language]
        except:
            return ''

    def check_if_no_theme_trans(self):
        """ check if translation """
        for theme in self.get_subjects_list():
            for lang in self.get_english_names():
                try:    trans = theme[lang]
                except: trans = ''
                if trans != '': return 1
        return 0

    def set_theme_trans_list(self, code, language, translation):
        """ set the languages """
        theme = self.getThemeByCode(code)
        self.del_subject_from_list(code)
        theme[language] = translation
        self.subjects_list.append(theme)

    def load_theme_trans_list(self, code):
        """ load languages """
        for lang in self.get_english_names():
            setattr(self, lang, '')

    def manageDefinitionTranslations(self, th_code='', lang_code='', translation='', REQUEST=None):
        """ save translation for a language """
        self.set_theme_trans_list(th_code, lang_code, translation)
        self._p_changed = 1
        self.cu_recatalog_object(self)
        if REQUEST: return REQUEST.RESPONSE.redirect('themes_html?tab=1&amp;code=%s' % th_code)


    ##########################
    #   LANGUAGES FUNCTIONS  #
    ##########################
    def get_languages_list(self):
        """ get the languages """
        self.utSortListOfDictionariesByKey(self.languages_list, 'english_name')
        return self.languages_list

    def get_english_names(self):
        """ get the english name from languages list """
        results = []
        for k in self.get_languages_list():
            results.append(k['english_name'])
        return results

    def get_language_codes(self):
        """ get the codes from languages list """
        results = []
        for k in self.get_languages_list():
            results.append(k['lang'])
        return results

    def get_language_code(self, language):
        """ """
        for k in self.get_languages_list():
            if k['english_name'] == language:
                return k['lang']

    def get_language_by_code(self, lang_code):
        """ get the english name given the code """
        for k in self.get_languages_list():
            if k['lang'] == lang_code:
                return k['english_name']

    def set_languages_list(self, lang, english_name):
        """ set the languages """
        self.languages_list.append({'lang':lang, 'english_name':english_name})

    def del_language_from_list(self, lang):
        """ remove a language from list """
        for lang_info in self.languages_list:
            if lang_info['lang'] == lang:
                self.languages_list.remove(lang_info)

    def get_unicode_langs(self):
        """ return the unicode languages list """
        return []

    def check_language_exists(self, english_name):
        """ check if this language exists """
        ret = 1
        for eng_lang in self.languages_list:
            if eng_lang['english_name'] == english_name:
                ret = 0
        return ret

    def updateObjectsByLang(self, language):
        """ update objects when a new language is added """
        for l_folder in self.objectValues(NAAYAGLOSSARY_FOLDER_METATYPE):
            try:
                trans = getattr(l_folder, language)
                if trans: self.cu_recatalog_object(l_folder)
            except:
                setattr(l_folder, language, '')

            for l_element in l_folder.objectValues(NAAYAGLOSSARY_ELEMENT_METATYPE):
                try:
                    trans = getattr(l_element, language)
                    if trans: self.cu_recatalog_object(l_element)
                except:
                    setattr(l_element, language, '')
        return 'done'

    def manageLanguagesProperties(self, ids='', lang='', english_name='', old_english_name='', REQUEST=None):
        """ manage languages for NyGlossary """
        if self.utAddObjectAction(REQUEST):
            if string.strip(lang)=='' or string.strip(english_name)=='':
                return REQUEST.RESPONSE.redirect('languages_html')
            else:
                if self.check_language_exists(english_name):
                    self.set_languages_list(lang, english_name)
                    self.updateObjectsByLang(english_name)

                    try:
                        catalog_obj = self.getGlossaryCatalog()
                        index_extra = record()
                        index_extra.default_encoding = 'utf-8'
                        try:    catalog_obj.manage_addIndex(self.cookCatalogIndex(english_name), 'TextIndexNG2',index_extra)
                        except: pass
                    except: pass

                    self._p_changed = 1
                else:
                    return REQUEST.RESPONSE.redirect('languages_html')
        elif self.utDeleteObjectAction(REQUEST):
            if not ids or len(ids) == 0:
                return REQUEST.RESPONSE.redirect('languages_html')
            for english_name in self.utConvertToList(ids):
                self.del_language_from_list(english_name)
            self._p_changed = 1
        if REQUEST: return REQUEST.RESPONSE.redirect('languages_html?save=ok')

    def addLanguage(self, english_name='', lang=''):
        """ """
        if string.strip(lang)=='' or string.strip(english_name)=='':
            self.setSessionErrors(["Please specify language name and code."])
            return self.REQUEST.RESPONSE.redirect('index_languages_html')
        else:
            if self.check_language_exists(english_name):
                self.set_languages_list(lang, english_name)
                self.updateObjectsByLang(english_name)

                try:
                    catalog_obj = self.getGlossaryCatalog()
                    index_extra = record()
                    index_extra.default_encoding = 'utf-8'
                    try:    catalog_obj.manage_addIndex(self.cookCatalogIndex(english_name), 'TextIndexNG2',index_extra)
                    except: pass
                except: pass

                self._p_changed = 1
            else:
                self.setSessionErrors(["Language already exists."])
                return self.REQUEST.RESPONSE.redirect('index_languages_html')
        self.setSessionInfo(['Saved changes.'])
        return self.REQUEST.RESPONSE.redirect('index_languages_html')

    def deleteLanguages(self, ids=[]):
        """ """
        if not ids or len(ids) == 0:
            return self.REQUEST.RESPONSE.redirect('index_languages_html')
        for english_name in self.utConvertToList(ids):
            self.del_language_from_list(english_name)
        self._p_changed = 1
        return self.REQUEST.RESPONSE.redirect('index_languages_html')


    ######################################
    # GLOSSARY ADMINISTRATION FUNCTIONS  #
    ######################################
    def get_not_approved(self):
        """.return the elements not approved """
        lst_not_approved = []
        append = lst_not_approved.append
        for obj in self.cu_get_cataloged_objects(meta_type=[NAAYAGLOSSARY_ELEMENT_METATYPE], sort_on='id', sort_order=''):
            if (not obj.approved): append(obj)
        return lst_not_approved

    def get_published(self, path=''):
        """.return the elements published """
        lst_published = []
        append = lst_published.append
        for obj in self.cu_get_cataloged_objects(meta_type=[NAAYAGLOSSARY_ELEMENT_METATYPE], sort_on='id', sort_order='', path=path):
            if obj.is_published(): append(obj)
        return lst_published

    def getGlossaryChild(self, path):
        if path:
            return self.restrictedTraverse(path, None)

    def checkPermissionManageGlossary(self):
        return self.checkPermission(PERMISSION_MANAGE_NAAYAGLOSSARY)

    ######################################
    # GLOSSARY FUNCTIONALITIES FUNCTIONS #
    ######################################

    def getObjectCodes(self, names=[], REQUEST=None):
        """ get object codes """
        return [brain.id for brain in self.cu_get_codes_by_name([NAAYAGLOSSARY_ELEMENT_METATYPE], names)]

    def getObjectByCode(self, id='', REQUEST=None):
        """ get object by code """
        return self.cu_search_catalog_by_id(id)

    def searchGlossary(self, query='', size=10000, language='English', definition='*', REQUEST=None):
        """ search glossary """
        if not size: size = 10000
        results = self.cu_search_catalog([NAAYAGLOSSARY_ELEMENT_METATYPE], query, size, language, definition)
        return (language, query, results)

    def folder_list_sorted(self):
        """ Return all the folders, sorted"""
        results = []
        for l_folder in self.cu_get_cataloged_objects(meta_type=[NAAYAGLOSSARY_FOLDER_METATYPE], sort_on='id', sort_order=''):
            if len(l_folder.objectValues([NAAYAGLOSSARY_ELEMENT_METATYPE])) > 0:

                for k in l_folder.objectValues([NAAYAGLOSSARY_ELEMENT_METATYPE]):
                    if k.is_published():
                        results.append(l_folder)
                        break

        return results

    def get_all_objects(self, path=''):
        """ return sorted objects by name """
        return self.cu_get_cataloged_objects(meta_type=[NAAYAGLOSSARY_ELEMENT_METATYPE], sort_on='id', sort_order='', path=path)

    def get_all_elements(self):
        """ return sorted objects by name """
        return self.cu_get_cataloged_objects(meta_type=[NAAYAGLOSSARY_ELEMENT_METATYPE,], sort_on='id', sort_order='')

    def xliff_import(self, file, REQUEST=None):
        """ XLIFF is the XML Localization Interchange File Format
            designed by a group of software providers.
            It is specified by www.oasis-open.org
        """

        parser = xliff_parser()

        #parse the xliff information
        chandler = parser.parseHeader(file)

        if chandler is None:
            return MessageDialog(title = 'Parse error',
             message = 'Unable to parse XLIFF file' ,
             action = 'manage_main',)

        header_info = chandler.getFileTag()
        #get the target language
        target_language = [x for x in header_info if x[0]=='target-language'][0][1]

        body_info = chandler.getBody() #return a dictionary {id: (source, target)}
        obj = mapTiny()
        for ids, translation in body_info.items():
            elem_id = ids[0].encode('utf-8')

            if elem_id!='':
                l_context_name = translation['context-name']
                if l_context_name:
                    folder_id = ids[1].encode('utf-8')
                else:
                    folder_id = string.upper(elem_id[:1])
                folder = self._getOb(folder_id, None)
                if folder is None:
                    try:
                        self.manage_addGlossaryFolder(folder_id, translation['context'], [], '', '', 1)
                        folder = self._getOb(folder_id)
                        folder.set_translations_list(target_language, translation['context'])
                    except Exception, error:
                        #print error
                        pass
                else:
                    folder.set_translations_list(target_language, translation['context'])
                if target_language in self.get_english_names():
                    obj.entry = translation['source']
                    obj.translations[target_language] = translation['target']
                if obj.entry!='':
                    elem_ob = folder._getOb(obj.entry.encode('utf-8'), None)
                    if elem_ob is not None:
                        for k,v in obj.translations.items():
                            elem_ob.set_translations_list(k, v)
                        elem_ob.cu_recatalog_object(elem_ob)
                    else:
                        try:
                            folder.manage_addGlossaryElement(elem_id, obj.entry, '', [], '', self.utConvertToInt(translation['approved'].encode('utf-8')))
                        except Exception, error:
                            #print error
                            pass
                        elem_ob = folder._getOb(elem_id, None)
                        if elem_ob is not None:

                            #name translation
                            for k,v in obj.translations.items():
                                elem_ob.set_translations_list(k, v)

                            #definition translation
                            elem_ob.set_def_trans_list(target_language, translation['note'])
                            elem_ob.cu_recatalog_object(elem_ob)
            obj.emptyObject()
        if REQUEST: return REQUEST.RESPONSE.redirect('import_html')

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'terms_import')
    def terms_import(self, format='', file=None):
        """ """
        if format == 'xliff':
            self.xliff_import(file, self.REQUEST)
        elif format == 'tmx':
            self.tmx_import(file, self.REQUEST)

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'terms_export')
    def terms_export(self, format='', language='', published=0):
        """ """
        if format == 'xliff':
            return self.xliff_export(language=language, published=published, REQUEST=self.REQUEST)
        elif format == 'tmx':
            return self.tmx_export(published=published, REQUEST=self.REQUEST)


    #####################
    #   SKOS Functions  #
    #####################
    security.declareProtected(view_management_screens, 'loadRDF')
    def loadRDF(self):
        """ loads rdf files """
        from os.path import join
        from Products.PythonScripts.PythonScript import manage_addPythonScript

        file_content = open(join(NAAYAGLOSSARY_PATH, 'rdfs', 'glossary_skos.spy'), 'r').read()
        manage_addPythonScript(self, 'glossary_skos.rdf')
        self._getOb('glossary_skos.rdf').write(file_content)

    def GetElementsInfo(self):
        """ """
        result=[]
        folder_list = self.folder_list_sorted()
        for folder in folder_list:
            for elem in folder.get_object_list():
                if elem.is_published() and elem.meta_type == NAAYAGLOSSARY_ELEMENT_METATYPE:
                    result.append(elem)
        return result

    ##########################
    # GLOSSARY STUCTURAL MAP #
    ##########################
    def __getStructMap(self, root, showitems, expand, depth):
        l_tree = []
        l_folders = root.getGlossaryObTree()
        for l_folder in l_folders:
            if l_folder.hasGlossFolders() or (l_folder.hasGlossElems() and showitems==1):
                if l_folder.absolute_url(1) in expand or 'all' in expand:
                    l_tree.append((l_folder, 0, depth))
                    l_tree.extend(self.__getStructMap(l_folder, 1, expand, depth+1))
                    if showitems:
                        for l_item in l_folder.getGlossElems():
                            l_tree.append((l_item, -1, depth+1))
                else:
                    l_tree.append((l_folder, 1, depth))
            else:
                l_tree.append((l_folder, -1, depth))
        return l_tree

    def getStructMap(self, expand=[], root=None, showitems=0):
        if root is None: root = self
        return self.__getStructMap(root, showitems, expand, 0)

    def getSiteMapTrail(self, expand, tree):
        if expand == 'all': return ','.join([node[0].absolute_url(1) for node in tree])
        else: return expand

    def structExpand(self, expand, node):
        return self.joinToList(self.addToList(expand, str(node)))

    def structCollapse(self, expand, node):
        return self.joinToList(self.removeFromList(expand, str(node)))

    ######################
    #    GLOSSARY MAP    #
    ######################
    def __getGlossMap(self, root, showitems, expand, depth):
        """ returns the site map tree """
        l_tree = []
        if root is self:
            l_folders = root.folder_list_sorted()
        else:
            l_folders = root.folder_list_sorted()

        for l_folder in l_folders:
            if l_folder.get_object_list():
                if l_folder.absolute_url(1) in expand:
                    l_tree.append((l_folder, 0, depth))
                    if showitems:
                        for l_item in l_folder.get_object_list():
                            if l_item.is_published():  l_tree.append((l_item, -1, depth+1))
                else:
                    l_tree.append((l_folder, 1, depth))
            else:
                l_tree.append((l_folder, -1, depth))
        return l_tree

    def getGlossMap(self, expand=[], root=None, showitems=0):
        """ returns the site map tree """
        if root is None:
            root = self
        return self.__getGlossMap(root, showitems, expand, 0)

    def buildExpandList(self, expand):
        return expand.split(',')

    def checkExpandNode(self, expand, node):
        return str(node) in expand

    def processExpand(self, expand, node):
        """ expands node """
        node = str(node)
        res = copy(expand)
        if node not in res:
            res.append(node)
        return ','.join(res)

    def processCollapse(self, expand, node):
        """ collapses node """
        node = str(node)
        res = copy(expand)
        if node in res:
            res.remove(node)
        return ','.join(res)

    security.declarePublic('getGlossaryObTree')
    def getGlossaryObTree(self):
        """ """
        results = []
        for item in self.objectValues(NAAYAGLOSSARY_FOLDER_METATYPE):
            if item.is_published(): results.append(item)
        return self.utSortObjsListByAttr(results, self.get_language_by_code(self.getSelectedLang()), 0)

    def getSelectedLang(self):
        """ """
        l_lang = self.gl_get_selected_language()
        if l_lang in self.get_language_codes():
            return l_lang
        return 'en'

    #################
    #   ALPHABETS   #
    #################
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

    def __build_alphabets_cache_for_lang(self, lang):
        self.__alphabets_cache[lang] = []
        dict_lang_tree = {}
        for ob in self.get_all_objects():
            if ob.is_published():
                t = ob.get_translation_by_language(self.get_language_by_code(lang))
                if t:
                    l = None
                    for x in self._unicode_map(lang):
                        if t[0] in x:
                            l = x[0].encode('utf-8')
                            break
                    if l is not None:
                        if not dict_lang_tree.has_key(l): dict_lang_tree[l] = []
                        if type(t) == type(u''): t = t.encode('utf-8')
                        dict_lang_tree[l].append(t)
        for x in self._unicode_map(lang):
            if dict_lang_tree.has_key(x[0].encode('utf-8')):
                self.__alphabets_cache[lang].append((x[0].encode('utf-8'), copy(dict_lang_tree[x[0].encode('utf-8')])))
        self._p_changed = 1

    security.declarePublic('getGlossaryTree')
    def getGlossaryTree(self, lang):
        #returns the glossary according with the given language
        if not self.__alphabets_cache.has_key(lang):
            self.__build_alphabets_cache_for_lang(lang)
        return self.__alphabets_cache[lang]

    #####################
    #   MANAGEMENT TABS #
    #####################
    #management tabs
    security.declareProtected(view_management_screens, 'themes_html')
    themes_html =           PageTemplateFile('zpt/NaayaGlossary/themes', globals())

    security.declareProtected(view_management_screens, 'themes_manage_html')
    themes_manage_html =    PageTemplateFile('zpt/NaayaGlossary/themes_manage', globals())

    security.declareProtected(view_management_screens, 'themes_trans_html')
    themes_trans_html =     PageTemplateFile('zpt/NaayaGlossary/themes_trans', globals())

    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =       PageTemplateFile('zpt/NaayaGlossary/properties', globals())

    security.declareProtected(view_management_screens, 'languages_html')
    languages_html =        PageTemplateFile('zpt/NaayaGlossary/languages', globals())

    security.declareProtected(view_management_screens, 'export_html')
    export_html =           PageTemplateFile('zpt/NaayaGlossary/export', globals())

    security.declareProtected(view_management_screens, 'import_html')
    import_html =           PageTemplateFile('zpt/NaayaGlossary/import', globals())

    security.declareProtected(view_management_screens, 'management_page_html')
    management_page_html =  PageTemplateFile('zpt/NaayaGlossary/administration', globals())

    security.declareProtected(view_management_screens, 'not_approved_html')
    not_approved_html =     PageTemplateFile('zpt/NaayaGlossary/administration_not_approved', globals())

    security.declareProtected(view_management_screens, 'all_terms_html')
    all_terms_html =        PageTemplateFile('zpt/NaayaGlossary/all_terms', globals())

    contexts_view_html =    PageTemplateFile('zpt/NaayaGlossary/contexts_view', globals())
    style_console_css =     PageTemplateFile('zpt/NaayaGlossary/style_console', globals())

    #layout pages
    main_search_html =      PageTemplateFile('zpt/NaayaGlossary/main_search', globals())
    search_html =           PageTemplateFile('zpt/NaayaGlossary/search_box', globals())
    search_help_html =      PageTemplateFile('zpt/NaayaGlossary/search_help', globals())

    #maps pages
    GlossMap_html =         PageTemplateFile("zpt/NaayaGlossary/GlossMap", globals())
    map_structural_html =   PageTemplateFile("zpt/NaayaGlossary/map_structural", globals())
    GlossMapAlph_html =     PageTemplateFile("zpt/NaayaGlossary/GlossMapAlph", globals())
    map_alphabetical_html = PageTemplateFile("zpt/NaayaGlossary/map_alphabetical", globals())

    #unified index
    index_html =            PageTemplateFile('zpt/NaayaGlossary/index', globals())
    index_themes_html =     PageTemplateFile('zpt/NaayaGlossary/index_themes', globals())
    index_languages_html =  PageTemplateFile('zpt/NaayaGlossary/index_languages', globals())
    index_approvals_html =  PageTemplateFile('zpt/NaayaGlossary/index_approvals', globals())
    index_impexp_html =     PageTemplateFile('zpt/NaayaGlossary/index_import_export', globals())
    index_properties_html = PageTemplateFile('zpt/NaayaGlossary/index_properties', globals())

    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'index_themes_html')
    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'index_languages_html')
    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'index_approvals_html')
    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'index_impexp_html')
    security.declareProtected(PERMISSION_MANAGE_NAAYAGLOSSARY, 'index_properties_html')

InitializeClass(NyGlossary)


class mapTiny:
    def __init__(self):
        """ """
        self.entry = ''
        self.source = ''
        self.translations = {}
        self.context = ''
        self.context_name = ''
        self.note = ''

    def emptyObject(self):
        """ """
        self.entry = ''
        self.source = ''
        self.translations = {}
        self.context = ''
        self.context_name = ''
        self.note = ''
