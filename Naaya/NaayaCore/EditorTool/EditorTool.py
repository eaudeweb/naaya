#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "GeoMapTool"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA). Portions created by Eau de Web are Copyright (C) 
#2007 by European Environment Agency. All Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#        Cornel Nitu (Eau de Web)

"""
This is a core tool of the Naaya CMF.
Every portal B{must} have an object of this type inside.
"""

#Python imports
from ConfigParser import ConfigParser
from os.path import join, dirname

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.LocalFS.LocalFS import manage_addLocalFS

#Product imports
from Products.NaayaCore.constants import *


def manage_addEditorTool(self, REQUEST=None):
    """
    ZMI method that creates an object of this type.
    """
    ob = EditorTool(ID_EDITORTOOL, TITLE_EDITORTOOL)
    self._setObject(ID_EDITORTOOL, ob)
    self._getOb(ID_EDITORTOOL).loadDefaultData()
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class EditorTool(Folder):
    """
    Class that implements the tool.
    """

    meta_type = METATYPE_EDITORTOOL
    icon = 'misc_/NaayaCore/EditorTool.gif'

    manage_options = (
        Folder.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """
        Initialize variables.
        """
        self.id = id
        self.title = title
        self.configuration = {}

    def getConfiguration(self):
        """ return configuration """
        return self.configuration

    def _getTinyMCEInstance(self):
        """ return the TinyMCE instance object we intend to use """
        return self._getOb('tinymce')

    def _getTinyMCELanguages(self):
        """ return the list of languages that TinyMCE could handle """
        return ['da', 'en', 'es', 'fr', 'hu', 'it', 'ro', 'ru']

    def _getTinyMCEDefaultLang(self):
        return 'en'

    def render(self, lang=None, **kwargs):
        """ return the HTML necessary to run the TinyMCE """
        #language negotiations
        if lang is None: lang = self.gl_get_selected_language()
        if lang not in self._getTinyMCELanguages():
            lang = self._getTinyMCEDefaultLang()

        #render the javascript
        tinymce_js_file = "tiny_mce.js"
        tinymce = self._getTinyMCEInstance()
        js = []
        jsappend = js.append
        jsappend('<script type="text/javascript" src="%s/%s"></script>' % (tinymce.jscripts.tiny_mce.absolute_url(), tinymce_js_file))
        jsappend('<script type="text/javascript" src="%s/%s"></script>' % (tinymce.jscripts.tiny_mce.absolute_url(), 'Naaya/file_browser_callback.js'))
        jsappend('<script type="text/javascript" src="%s/%s"></script>' % (tinymce.jscripts.tiny_mce.absolute_url(), 'Naaya/jscripts/select_relative_link.js'))
        jsappend('<script type="text/javascript" src="%s/%s"></script>' % (tinymce.jscripts.tiny_mce.absolute_url(), 'Naaya/jscripts/select_image.js'))
        jsappend('<script type="text/javascript">')
        jsappend('nyFileBrowserCallBack = getNyFileBrowserCallBack("%s")' % (self.REQUEST['URLPATH1'],))
        jsappend('tinyMCE.init({')
        jsappend('language:"%s",' % lang)
        [ jsappend('%s:"%s",' % (k, ','.join(v))) for k, v in self.configuration.items() ]
        jsappend('document_base_url:"%s/"' % self.getSitePath())
        jsappend('});')
        jsappend('</script>')
        return '\n'.join(js)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ Creates default stuff. """
        self.manage_addProduct['LocalFS'].manage_addLocalFS('tinymce', '', join(dirname(__file__), 'tinymce'))

        config = ConfigParser()
        config.read(join(dirname(__file__), 'config.ini'))
        for section in config.sections():
            for option in config.options(section):
                self.configuration[option] = [i.strip() for i in config.get(section, option).split(',')]

    security.declarePrivate('manage_props')
    def manage_props(self, wordlike, justify, links):
        """ manage properties """
        if wordlike:
            pass
        if justify:
            justify = ['justifyleft', 'justifycenter', 'justifyright', 'justifyfull', 'separator']
            buttons1 = self.configuration.get('theme_advanced_buttons1', '')
            pos = buttons1.index('strikethrough') + 1
            for j in justify:
                buttons1.insert(j, pos)
                pos += 1
            self.configuration['theme_advanced_buttons1'] = buttons1
            self._p_changed = 1
        if links:
            pass

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/editor_test', globals())

InitializeClass(EditorTool)
