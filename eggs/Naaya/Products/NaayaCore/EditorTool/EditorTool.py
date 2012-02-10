"""
This tool provides an WYSIWYG api for rich content editing with text
formatting, image, multimedia etc. It's used in almost all Naaya content
types.

"""

import re
import copy
from ConfigParser import ConfigParser
from os.path import join, dirname
import simplejson as json

from AccessControl import ClassSecurityInfo
from App.ImageFile import ImageFile
from Globals import InitializeClass
from OFS.Folder import Folder

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
    Returns a dictionary with tinymce configuration options
    """
    boolean_settings = ['button_tile_map',
                'apply_source_formatting',
                'remove_linebreaks',
                'relative_urls',
                'convert_urls',
                'paste_use_dialog',
                'verify_html',
                'theme_advanced_resizing']
    ret = {}
    config = ConfigParser()
    config.read(join(dirname(__file__), 'config.ini'))
    if config.has_section(section):
        for option in config.options(section):
            if option.strip() in boolean_settings:
                ret[option.strip()] = config.getboolean(section, option)
            else:
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
        return '<script type="text/javascript" language="javascript" src="%(parent_url)s/tinymce/jscripts/tiny_mce/jquery.tinymce.js"></script>' % {'parent_url': self.absolute_url()}

    security.declarePublic('additional_styles')
    def additional_styles(self):
        """
        Returns the additional naaya styles to be displayed in tinymce
        """
        ret = ''

        # insert other styles here

        styleselect = self._get_styleselect_styles()
        if styleselect is not None:
            ret += styleselect

        return ret

    def _get_styleselect_styles(self):
        """
        Returns the styles to use for styleselect listing inside tinymce
        Searches the current style objects for the specific format
        /*BEGIN-TINYMCE-STYLESELECT*/
        ...
        selector { style }
        ...
        /*END-TINYMCE-STYLESELECT*/
        """
        style_objects = self.getLayoutTool().getCurrentStyleObjects()
        for so in style_objects:
            text = so()
            match = re.search('/\\*BEGIN-TINYMCE-STYLESELECT\\*/(.*?)/\\*END-TINYMCE-STYLESELECT\\*/', text, re.S)
            if match is not None:
                return match.group(1)
        return None

    def _add_styleselect_to_cfg(self, cfg):
        """
        Adds a style select box to the front of the first row of buttons
        if it can find the styles file it needs
        if not it does nothing

        the format for the styles is
        /*BEGIN-TINYMCE-STYLESELECT*/
        ...
        selector { style }
        ...
        /*END-TINYMCE-STYLESELECT*/
        """
        # get the styles
        text = self._get_styleselect_styles()
        if text is None:
            return

        # find class selectors
        selectors_text = re.sub('{(.|\n)*?}', '', text)
        selectors = re.findall('\\.\w+(?=\s|[,{])', selectors_text)
        selectors = [sel[1:] for sel in selectors]

        # add the button and selectors to it
        cfg['theme_advanced_styles'] = ';'.join(['%s=%s' % (sel.capitalize(), sel) for sel in selectors])

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
        if not lang:
            lang = self.gl_get_selected_language()
        doc_url = "/".join(self.aq_parent.getPhysicalPath())
        if extra_options.has_key('config_template'):
            template = extra_options['config_template']
            cfg = loadConfig(template)
        else:
            cfg = copy.copy(configuration)
        cfg.update({
            'language': lang,
            'select_image_url' : '%s/select_image?document=%s' \
                    % (self.absolute_url(), doc_url),
            'edit_image_url' : '%s/prepare_image?mode=edit&document=%s' % (self.absolute_url(), doc_url),
            'link_popup_url' : '%s/select_link' % self.absolute_url(),
            'element_id': element,
            'script_url' : '%s/tinymce/jscripts/tiny_mce/tiny_mce.js' \
                % self.absolute_url(),
            'site_url': self.getSite().absolute_url(),
            'language' : self.gl_get_selected_language(),
        })
        cfg.update(extra_options)
        # romancri 20100420:
        # When using dialects, clobber the dialect. Otherwise, TinyMCE fails
        # because it doesn't have these translation files.
        if 'language' in cfg.keys() and cfg['language']:
            cfg['language'] = cfg['language'].split('-')[0]

        self._add_styleselect_to_cfg(cfg)

        css_url = '/'.join(self.getPhysicalPath()) + '/additional_styles'
        old_css = cfg.get('content_css', '')
        cfg['content_css'] = css_url
        if old_css != '':
            cfg['content_css'] += ',' + old_css

        return "<script type=\"text/javascript\">\
$().ready(function() {$('textarea#%s').tinymce(%s);})\
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

        if not url.startswith('http') and not url.startswith('/'):
            document = self.getEnclosingDocument(REQUEST)
            if document is not None:
                url = '%s/%s' % (document.absolute_url(), url)

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

    def enumerateImages(self, source, page=0, query=None, REQUEST=None):
        """ Retrieve the list of images depending on the source.
        Return a list of ``Image`` objects
        """

        def get_image_info(source, image):
            image_object = {
                'url': image.absolute_url(),
                'title': image.title_or_id(),
                'source': '',
                'author': ''
            }

            if source == 'album':
                image_object['source'] = image.source
                image_object['author'] = image.author

            return image_object

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
            if query is None:
                album = self.restrictedTraverse(album_url)
                ret = album.getObjects()
            else:
                ctool = self.getCatalogTool()
                filter_index = 'objectkeywords_' + self.gl_get_selected_language()
                ret_brains = ctool.search({'path': album_url,
                    'meta_type': 'Naaya Photo',
                    filter_index: query})
                ret = [x.getObject() for x in ret_brains]

        total_images = len(ret)
        images = ret[(int(page) * 12):((int(page) + 1) * 12)]

        options = {
            'total_images': total_images,
            'images': [get_image_info(source, image) for image in images]
        }

        return json.dumps(options)


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
        Return a dictionary with found attributes such as border, margin etc.
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
        """ Safely retrieve a parameter from request
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
        StaticServeFromZip('tinymce', 'www/tinymce_3_4_7_jquery_naaya.zip', globals())
    tinymce_naaya \
        = StaticServeFromZip('Naaya', 'www/tinymce_naaya.zip', globals())
    select_image = PageTemplateFile('zpt/select_image', globals())
    select_image_size = PageTemplateFile('zpt/select_image_size', globals())
    prepare_image = PageTemplateFile('zpt/prepare_image', globals())
    select_link = PageTemplateFile('zpt/select_link', globals())

InitializeClass(EditorTool)
