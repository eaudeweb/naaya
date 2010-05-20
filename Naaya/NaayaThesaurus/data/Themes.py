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

# Zope imports
from Globals                                    import InitializeClass
from AccessControl                              import ClassSecurityInfo
from OFS.SimpleItem                             import SimpleItem
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from AccessControl.Permissions                  import view_management_screens, view
from ZODB.PersistentMapping                     import PersistentMapping

# product imports
from Products.NaayaThesaurus.constants              import *
from Products.NaayaThesaurus.utils                  import th_utils
from Products.NaayaThesaurus.session_manager        import session_manager
from Products.NaayaThesaurus.parsers.theme_parser   import theme_parser


manage_addThemes_html = PageTemplateFile('%s/zpt/Themes/add' % NAAYATHESAURUS_PATH, globals())

def manage_addThemes(self, id='', title='', REQUEST=None):
    """ adds a new Themes object """
    ob = Themes(id, title)
    self._setObject(id, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class Themes(SimpleItem, session_manager):
    """ Themes """

    meta_type = THEMES_METATYPE
    product_name = NAAYATHESAURUS_PRODUCT_NAME
    icon = 'misc_/NaayaThesaurus/themes.gif'

    manage_options = (
        {'label':'Basic properties',    'action':'properties_html'},
        {'label':'Management',          'action':'themes_html'},
        {'label':'Import',       'action':'import_html'},
        {'label':'Statistics',          'action':'statistics_html'},
        {'label':'Undo',                'action':'manage_UndoForm'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ constructor """
        self.id =       id
        self.title =    title
        self.themes =   PersistentMapping()


    #basic properties
    security.declareProtected(view_management_screens, 'manageBasicProperties')
    def manageBasicProperties(self, title='', REQUEST=None):
        """ manage basic properties for Themes """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            self.setSessionInfoTrans('Saved changes.')
            return REQUEST.RESPONSE.redirect('properties_html')


    #themes management
    def __add_theme(self, theme_id, langcode, name):
        #create a new item
        item = ThemeItem(theme_id, langcode, name)
        self.themes[(theme_id, langcode)] = item
        self.catalog.CatalogObject(item)

    def __update_theme(self, theme_id, old_theme_id, langcode, old_langcode, name):
        #modify an item
        item = self.themes.get((old_theme_id, old_langcode))
        if item is not None:
            self.__delete_theme((old_theme_id, old_langcode))
        self.__add_theme(theme_id, langcode, name)

    def __delete_theme(self, ids):
        #delete 1 or more items
        if type(ids) != type((1,1)):
            ids = th_utils().utConvertToList(ids)
        else:
            ids = [ids]
        collection = self.get_themes()

        for id in ids:
            self.catalog.UncatalogObject(collection[id])
            del collection[id]


    #theme constraints
    security.declareProtected(view_management_screens, 'checkTheme')
    def checkTheme(self, theme_id):
        """ """
        if theme_id in self.getThemeRelationsFolder().getDistinctThemes():
            return 1
        return 0

    security.declareProtected(view_management_screens, 'getIdsList')
    def getIdsList(self, ids, all=0):
        """ """
        if all: return self.themes.keys()
        return th_utils().getIdsList(ids)


    #themes getters
    def get_themes(self):
        #get all themes
        return self.themes

    def get_themes_sorted(self):
        #get all themes sorted
        return th_utils().utSortObjsListByAttr(self.themes.values(), 'langcode', 0)

    def get_theme_by_id(self, id):
        #get an item
        try:    return self.themes[id]
        except: return None

    def get_theme_item_data(self, theme_id, langcode, orig_theme_id, orig_langcode, theme_name):
        #get an item data
        item = self.get_theme_by_id((orig_theme_id, orig_langcode))
        if item is not None:
            if theme_name is None:
                theme_name = item.theme_name
            return ['update', theme_id, langcode, theme_name, orig_theme_id, orig_langcode]
        else:
            return ['add', theme_id, langcode, theme_name, '', '']


    #themes api
    security.declareProtected(view_management_screens, 'manage_add_theme')
    def manage_add_theme(self, theme_id='', langcode='', theme_name='', REQUEST=None):
        """ manage themes """
        err = 0
        if self.checkTheme(theme_id):
            self.__add_theme(theme_id, langcode, theme_name)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionThemeId(theme_id)
                self.setSessionLangcode(langcode)
                self.setSessionThemeName(theme_name)
                self.setSessionErrorsTrans('${theme_id} is not a valid theme ID.', theme_id=theme_id)
            else:
                self.setSessionInfoTrans('Record added.')
            REQUEST.RESPONSE.redirect('themes_html')

    security.declareProtected(view_management_screens, 'manage_update_theme')
    def manage_update_theme(self, theme_id='', old_theme_id='', langcode='', old_langcode='', theme_name='', REQUEST=None):
        """ update theme """
        err = 0
        if self.checkTheme(theme_id):
            self.__update_theme(theme_id, old_theme_id, langcode, old_langcode, theme_name)
        else:
            err = 1

        if REQUEST:
            if err:
                self.setSessionThemeId(theme_id)
                self.setSessionLangcode(langcode)
                self.setSessionThemeName(theme_name)
                self.setSessionErrorsTrans('${theme_id} is not a valid theme ID.', theme_id=theme_id)
                REQUEST.RESPONSE.redirect('themes_html?theme_id=%s&amp;langcode=%s' % (old_theme_id, old_langcode))
            else:
                self.setSessionInfoTrans('Record updated.')
                REQUEST.RESPONSE.redirect('themes_html')

    security.declareProtected(view_management_screens, 'manage_delete_themes')
    def manage_delete_themes(self, ids=[], delete_all='', REQUEST=None):
        """ delete themes """
        if delete_all:  ids = self.getIdsList(ids, 1)
        else:           ids = self.getIdsList(ids)
        self.__delete_theme(ids)

        if REQUEST:
            self.setSessionInfoTrans('Selected records deleted.')
            REQUEST.RESPONSE.redirect('themes_html')

    security.declareProtected(view_management_screens, 'getThemeItemData')
    def getThemeItemData(self):
        """ return a theme based on its ID """
        if self.isSessionThemeId():
            theme_id =          self.getSessionThemeId()
            langcode =          self.getSessionLangcode()
            theme_name =        self.getSessionThemeName()
            orig_theme_id =     self.REQUEST.get('theme_id', None)
            orig_langcode =     self.REQUEST.get('langcode', None)
        else:
            theme_id =          self.REQUEST.get('theme_id', self.getSessionThemeId())
            langcode =          self.REQUEST.get('langcode', self.getSessionLangcode())
            theme_name =        self.getSessionThemeName()
            orig_theme_id =     theme_id
            orig_langcode =     langcode

        self.delSessionThemeId()
        self.delSessionLangcode()
        self.delSessionThemeName()
        return self.get_theme_item_data(theme_id, langcode, orig_theme_id, orig_langcode, theme_name)


    #import related
    def skos_import(self, file, langcode, REQUEST=None):
        """ """
        parser = theme_parser()

        #parse the SKOS information
        chandler = parser.parseHeader(file)

        if chandler is None:
            if REQUEST:
                self.setSessionErrorsTrans('Parsing error. The file could not be parsed.')
                return REQUEST.RESPONSE.redirect('import_html')

        #get the target language
        skos_lang = chandler.getLanguage()
        if skos_lang:   target_language = skos_lang.encode('utf-8')
        else:           target_language = langcode

        #get data
        body_info = chandler.getBody()

        #info
        count_themes = 0
        err_themes = []

        #set data
        for id, data in body_info.items():
            theme_id = id.encode('utf-8').split('/')[-1]

            if theme_id:
                if self.checkTheme(theme_id):
                    theme_name = data['name']
                    self.__add_theme(theme_id, target_language, theme_name)
                    count_themes += 1
                else:
                    err_themes.append(theme_id)
            else:
                err_themes.append('None')

        if REQUEST:
            self.setSessionInfoTrans(['File imported successfully.',
                ('Translations added: ${count_themes}', {'count_themes': count_themes}, )])
            if err_themes:
                self.setSessionErrorsTrans(['Translations not imported (by its theme_id):',
                    ('Errors: ${err_themes}', {'err_themes': th_utils().utJoinToString(err_themes, ', ')}, )])
            return REQUEST.RESPONSE.redirect('import_html?msg=done')


    #statistics
    def getAllThemes(self):
        query = [('meta_type',THEME_ITEM_METATYPE)]
        return self.catalog.searchCatalog(query)

    def getThemesNumber(self):
        return len(self.getAllThemes())

    def getThemesTransNumber(self):
        results = {}
        for theme_ob in self.getAllThemes():
            try:    tr_count = results[theme_ob.langcode]
            except: tr_count = 0

            results[theme_ob.langcode] = tr_count + 1
        return results

    def getEmptyTrans(self):
        empty_count = 0
        for theme_ob in self.getAllThemes():
            if not theme_ob.theme_name:
                empty_count += 1
        return empty_count


    #management tabs
    security.declareProtected(view_management_screens, 'properties_html')
    properties_html =       PageTemplateFile("%s/zpt/Themes/properties" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'themes_html')
    themes_html =       PageTemplateFile("%s/zpt/Themes/themes" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'statistics_html')
    statistics_html =       PageTemplateFile("%s/zpt/Themes/statistics" % NAAYATHESAURUS_PATH, globals())

    security.declareProtected(view_management_screens, 'import_html')
    import_html =       PageTemplateFile("%s/zpt/Themes/import" % NAAYATHESAURUS_PATH, globals())

InitializeClass(Themes)


class ThemeItem:
    """ ThemeItem """

    meta_type = THEME_ITEM_METATYPE

    def __init__(self, theme_id, langcode, theme_name):
        """ constructor """
        self.theme_id =     theme_id
        self.langcode =     langcode
        self.theme_name =   theme_name

    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

InitializeClass(ThemeItem)
