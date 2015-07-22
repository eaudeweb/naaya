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
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA). Portions created by Eau de Web are Copyright (C)
#2007 by European Environment Agency. All Rights Reserved.
#
#Contributor(s):
#  Original Code:
#        Cornel Nitu (Eau de Web)
# Cristian Romanescu (Eau de Web)
"""
This is a core tool of the Naaya CMF.
Every portal B{must} have an object of this type inside.
"""
#Python imports
import copy
from ConfigParser import ConfigParser
from os.path import join, dirname
import simplejson as json 

#Zope imports
from AccessControl import ClassSecurityInfo
from App.ImageFile import ImageFile
from Globals import InitializeClass
from OFS.Folder import Folder

#Product imports
from Products.NaayaCore.constants import ID_EDITORTOOL, TITLE_EDITORTOOL, \
METATYPE_EDITORTOOL
from Products.NaayaCore.EditorTool.utilities import parse_css_margin, \
parse_css_border_width, strip_unit
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from naaya.core.StaticServe import StaticServeFromZip


def manage_addEditorTool(self, REQUEST=None):
    """ ZMI method that creates an EditorTool object instance into the portal"""
    ob = EditorTool(ID_EDITORTOOL, TITLE_EDITORTOOL)
    self._setObject(ID_EDITORTOOL, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)


def loadConfig(section='tinymce'):
    """ Loads the default configuration from *config.ini*.
    The configuration is loaded from the *config.ini* file.
    `section` Section to load from config.ini. You can use config.ini
    to create multiple templates for the editor and name them differently.
    Returns an dictionary with tinymce configuration options
    """
    ret = {}
    config = ConfigParser()
    config.read(join(dirname(__file__), 'config.ini'))
    if config.has_section(section):
        for option in config.options(section):
            ret[option.strip()] = config.get(section, option).strip()
    return ret

configuration = loadConfig() #Global configuration loaded from *config.ini*


class EditorTool(Folder):
    """ **EditorTool** installs itself into the portal and provides rich text 
    editing capabilities attachable via to HTML input elements such as textarea.
    It uses *TinyMCE* (http://tinymce.moxiecode.com/) editor.
    Please see README.txt located into this module for notes
    """

    meta_type = METATYPE_EDITORTOOL
    icon = 'misc_/NaayaCore/EditorTool.gif'
    manage_options = (Folder.manage_options)
    security = ClassSecurityInfo()


    def __init__(self, id, title):
        """ Initialize variables"""
        self.id = id
        self.title = title


    def getConfiguration(self):
        """ Return current default configuration """
        return configuration


    def includeLibs(self, lang=None):
        """ Returns HTML code that includes required JavaScript libraries.
        Parameters:
            `lang` 
                **Not used**
        """
        return '<script language="JavaScript" \
src="%(parent_url)s/tinymce/jscripts/tiny_mce/jquery.tinymce.js"></script>'\
    % {'parent_url': self.absolute_url()}


    def render(self, element, lang=None, image_support=False, extra_options={}):
        """Return the HTML necessary to run the TinyMCE.
        Parameters:
            `element` 
                `id` of HTML element that editor will is attached to.
            `lang` 
                **Not used** 
            `image_support` 
                **No longer used** In order to disable images. 
                Use extra_options, see below. 
            `extra_options` 
                Extra options you can pass to tinyMCE editor. See `config.ini` 
                for further reference. You can pass any option from there
                to override default one. 
                `extra_options['config_template']` Loads one of the defined 
                templates from `config.ini`. Default is 'tinymce'. 
                Also you can use 'tinymce_noimage' to disable image insertion.
        """
        doc_url = self.REQUEST['URLPATH1']
        if extra_options.has_key('config_template'):
            template = extra_options['config_template']
            cfg = loadConfig(template)
        else:
            cfg = copy.copy(configuration)
        cfg.update({
            'select_image_url' : '%s/select_image?document=%s' \
                    % (self.absolute_url(), doc_url),
            'edit_image_url' : '%s/prepare_image?mode=edit&document=%s' % (self.absolute_url(), doc_url),
            'link_popup_url' : '%s/select_link' % self.absolute_url(),
            'element_id': element,
            'script_url' : '%s/tinymce/jscripts/tiny_mce/tiny_mce.js' \
                % self.absolute_url(),
        })
        cfg.update(extra_options)
        return "<script type=\"text/javascript\">\
$().ready(function() {$('#%s').tinymce(%s);})\
</script>" % (element, json.dumps(cfg, indent=2))


    def get_preview_img(self, REQUEST=None):
        """ Compute src attribute for the preview image. Uploads image if
        requested.
        Returns the URL to the image.
        """
        url = ''
        if REQUEST.form.has_key('url'):
            url = REQUEST.form['url']
        if REQUEST.form.has_key('mode'):
            mode = REQUEST.form['mode']
            if mode == 'upload':
                url = self._upload_image(REQUEST)

        if not url.startswith('http'):
            url = '%s/%s' % (self.getEnclosingDocument(REQUEST).absolute_url(), url)
        return url


    def _upload_image(self, REQUEST=None):
        """ Upload an image into the document container. """
        if REQUEST:
            if REQUEST.form.has_key('file'):
                file = REQUEST.form['file']
                document = self.getEnclosingDocument(REQUEST)
                if document:
                    imageContainer = document.imageContainer;
                    uploaded = imageContainer.uploadImage(file, None)
                    return uploaded.absolute_url()
        else:
            print 'no image to upload'


    def enumerateImages(self, source, REQUEST=None):
        """ Retrieve the list of images depending on the source.
        Return a list of ``Image`` objects
        """
        ret = []
        if source == 'document':
            document = self.getEnclosingDocument(REQUEST)
            if document:
                ret = document.imageContainer.getImages()
        if source == 'website':
            site = self.getSite()
            ret = site.imageContainer.getImages()
        if source == 'album':
            album_url = REQUEST.form['album']
            album = self.restrictedTraverse(album_url)
            ret = album.getObjects()
        return ret


    def enumeratePhotoAlbums(self, REQUEST=None):
        """
        Lookup photo galleries from the site.
        Return a list with all photo galleries available within the site.
        """
        ctool = self.getCatalogTool()
        return [x.getObject() \
            for x in ctool.search({'meta_type' : 'Naaya Photo Folder'})]


    def getEnclosingDocument(self, REQUEST):
        """
        Return the enclosing document where this editor tool 
        instance is located.
        `REQUEST` 
            Http request that **must** contain the 'document' parameter
        Return enclosing document object
        """
        if REQUEST.form.has_key('document'):
            document_url = REQUEST.form['document']
            return self.restrictedTraverse(document_url)
        return None


    def prepare_image_styles(self, REQUEST=None):
        """ Parse `REQUEST` and retrieve image attributes to set them into
        preview. This method is called when user selects the image into editor
        and then presses image button to adjust its settings.
        Return an dictionary with found attributes such as border, margin etc.
        """
        ret = {
               'title' : self.get_request_param(REQUEST, 'title'),
               'alignment' : self.get_request_param(REQUEST, 'left'),
               'css_alignment' : '', 'margin' : '', 'border_preview' : '',
               'width_preview' : '', 'height_preview' : '', 'border' : '',
               'width' : '', 'height' : '', 'h_margin' : '', 'v_margin' : '',
        }
        if REQUEST.form.has_key('alignment'):
            alignment = REQUEST.form['alignment']
            if alignment:
                if alignment == 'left' or alignment == 'right':
                    ret['css_alignment'] = 'float: %s' % alignment
                else:
                    ret['css_alignment'] = 'vertical-align: %s' % alignment
        if REQUEST.form.has_key('margin'):
            ret['margin'] = 'margin: %s' % REQUEST.form['margin']
        if REQUEST.form.has_key('border'):
            ret['border_preview'] = 'border: %s' % REQUEST.form['border']
            ret['border'] = parse_css_border_width(REQUEST.form['border'])
        if REQUEST.form.has_key('width'):
            ret['width_preview'] = 'width: %s' % REQUEST.form['width']
            ret['width'] = strip_unit(REQUEST.form['width'])
        if REQUEST.form.has_key('height'):
            ret['height_preview'] = 'height: %s' % REQUEST.form['height']
            ret['height'] = strip_unit(REQUEST.form['height'])
        if REQUEST and REQUEST.form.has_key('margin'):
            margins = parse_css_margin(REQUEST.form['margin'])
            ret['h_margin'] = margins[0]
            ret['v_margin'] = margins[1]
        return ret

    def get_request_param(self, REQUEST, name, default=''):
        """ Safely retrieve an parameter from request
        Parameters:
            `REQUEST`
                Http request
            `name`
                Name of the parameter
            `default`
                Default value to return if parameter not found. If not specified
                is empty string.
        Return the parameter or default if none found. 
        """
        if self.REQUEST.has_key(name):
            return self.REQUEST.form[name]
        return default


    def isImageContainer(self, document):
        """ Verifies document if is image container or inherits the 
        imageContainer of NySite.
        Parameters:
            `document` 
                Document to be checked.
        Return ``true`` if document has its own instance of `imageContainer`
        """
        return self.getSite().imageContainer != document.imageContainer


    image_js = ImageFile('www/image.js', globals())
    link_js = ImageFile('www/link.js', globals())
    image_css = ImageFile('www/image.css', globals())
    tinymce = \
        StaticServeFromZip('tinymce', 'www/tinymce_3_2_7_jquery.zip', globals())
    tinymce_naaya \
        = StaticServeFromZip('Naaya', 'www/tinymce_naaya.zip', globals())
    select_image = PageTemplateFile('zpt/select_image', globals())
    prepare_image = PageTemplateFile('zpt/prepare_image', globals())
    select_link = PageTemplateFile('zpt/select_link', globals())

InitializeClass(EditorTool)
