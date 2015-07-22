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
import tinyMCEUtils


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
        return ['da', 'en', 'es', 'fr', 'it', 'ro', 'ru']

    def _getTinyMCEDefaultLang(self):
        return 'en'

    def _getTinyMCELang(self, lang=None):
        """Return the language that should be used by TinyMCE.

            If the desired language is unsupported by TinyMCE,
            another language will be chosen.
            @param lang: language to use; default is the language of the portal
        """
        if lang is None: lang = self.gl_get_selected_language()
        if lang not in self._getTinyMCELanguages():
            lang = self._getTinyMCEDefaultLang()
        return lang

    def includeLibs(self, lang=None):
        """Return HTML code that includes the TinyMCE JavaScript libraries.

            @param lang: language to use; default is the language of the portal
        """
        tinymce = self._getTinyMCEInstance()
        doc_url = self.REQUEST['URLPATH1'].lstrip('/')
        js = []
        jsappend = js.append
        jsappend('<script type="text/javascript" src="%s/%s"></script>' % (tinymce.jscripts.tiny_mce.absolute_url(), 'tiny_mce_gzip.js'))
        jsappend('<script type="text/javascript">')
        jsappend('tinyMCE_GZ.init({')
        jsappend('page_name: "%s/getTinyMCEJavaScript",' % self.absolute_url())
        jsappend('plugins: "%s",' %  ','.join(self.configuration['plugins']))
        jsappend('themes: "%s",' %  ','.join(self.configuration['theme']))
        jsappend('languages: "%s"' % self._getTinyMCELang(lang))
        jsappend('});')
        jsappend('</script>')
        jsappend('<script type="text/javascript">')
        jsappend('nyFileBrowserCallBack = getNyFileBrowserCallBack("%s")' % (doc_url,))
        jsappend('</script>')
        return '\n'.join(js)

    def render(self, element, lang=None, image_support=False):
        """Return the HTML necessary to run the TinyMCE.

            @param element: name of the HTML element that will be converted to TinyMCE;
                            the element can be any kind, e.g. textarea or div
            @param lang: language to use; default is the language of the portal
            @param image_support: if True, the user can add images
        """
        doc_url = self.REQUEST['URLPATH1'].lstrip('/')
        lang = self._getTinyMCELang(lang)
        params = []
        params.append('elements:"%s"' % element)
        params.append('language:"%s"' % lang)
        params.append('server_url:"%s"' % self.REQUEST.get('BASE0', ''))
        if self.isRTL(lang):
            params.append('directionality:"rtl"')
        # TODO for Python 2.4: use generator comprehension
        if image_support:
            params.extend([('%s: "%s"' % (k, ','.join(v))) for k, v in self.configuration.items()])
        else:
            params.extend(['%s: "%s"' % (k, ','.join(v)) for k, v in self.configuration.items()
                                                                    if k != "theme_advanced_buttons2"])
            L = list(self.configuration['theme_advanced_buttons2'])
            L.remove('image')
            params.append('theme_advanced_buttons2: "%s"' % ','.join(L))
        doc = self.restrictedTraverse(doc_url)
        if not doc.imageContainer.relative:
            params.append('document_base_url:"%s/"' % self.getSitePath())
        return """<script type="text/javascript">tinyMCE.init({%s});</script>""" % (',\n'.join(params), )

    security.declarePublic('getTinyMCEJavaScript')
    def getTinyMCEJavaScript(self, REQUEST):
        """Return all the TinyMCE JavaScript code.

            The purpose of this function is to minimize the number of HTTP requests.
            It's needed by tinyMCE_GZ.
        """
        isJS = REQUEST.get('js', '') == 'true'
        languages = REQUEST['languages'].split(',')
        themes = REQUEST['themes'].split(',')
        plugins = REQUEST['plugins'].split(',')
        custom_files = [join('Naaya', 'file_browser_callback.js'),
                        join('Naaya', 'urlconverter_callback.js'),
                        join('Naaya', 'jscripts', 'select_relative_link.js'),
                        join('Naaya', 'jscripts', 'select_image.js')]
        content = tinyMCEUtils.getCompressedJavaScript(isJS,
                                                       languages,
                                                       themes,
                                                       plugins,
                                                       custom_files)
        REQUEST.RESPONSE.enableHTTPCompression(REQUEST)
        REQUEST.RESPONSE.setHeader('Content-type', 'application/x-javascript')
        REQUEST.RESPONSE.write(content)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """Loads the default TinyMCE configuration.

            The configuration is loaded from the "config.ini" file.
        """
        manage_addLocalFS(self, 'tinymce', '', join(dirname(__file__), 'tinymce'))

        config = ConfigParser()
        config.read(join(dirname(__file__), 'config.ini'))
        for section in config.sections():
            for option in config.options(section):
                self.configuration[option] = [i.strip() for i in config.get(section, option).split(',')]

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/editor_test', globals())

    security.declarePublic('style_css')
    style_css = PageTemplateFile('zpt/editor_css', globals())

InitializeClass(EditorTool)
