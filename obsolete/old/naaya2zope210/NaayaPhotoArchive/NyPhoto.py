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
# Alin Voinea, Eau de Web
# Alex Morega, Eau de Web

#Python imports
import re
import sys
import os
from cStringIO import StringIO
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    # PIL installed as an egg
    import Image, ImageDraw, ImageFont

#calculations needed by apply_watermark
from math import atan, degrees
import simplejson as json
from decimal import Decimal

#Zope imports
from zope.deprecation import deprecate
from zope.interface import implements
from OFS.Image import getImageInfo, cookId, Pdata
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view_management_screens, ftp_access
from AccessControl.Permissions import view as view_permission

#Product imports
from constants import *
from Products.NaayaBase.NyContentType import NyContentType, NyContentData, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyFSContainer import NyFSContainer
from Products.Naaya.constants import *
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from interfaces import INyPhoto
from photo_archive import photo_archive_base
from Products.NaayaCore.managers.utils import make_id

DEFAULT_SCHEMA = {}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

DEFAULT_SCHEMA.update({
    'author':           dict(sortorder=100, widget_type='String', label='Author', localized=True),
    'source':           dict(sortorder=110, widget_type='String', label='Source', localized=True),
    'geo_location':     dict(sortorder=120, widget_type='Geo', data_type='geo', label='Geographic location', visible=True),
})

_photo_add_html = PageTemplateFile('zpt/photo_add', globals())
def photo_add_html(self, REQUEST):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_NYPHOTO)
    return _photo_add_html.__of__(self)(REQUEST, form_helper=form_helper)

def addNyPhoto(self, id='', REQUEST=None, _klass=None, **kwargs):
    """
    Create a Photo type of object.
    """
    if self.is_full():
        return None

    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs

    if _klass is None:
        _klass = NyPhoto
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    if schema_raw_data.get('sortorder', '') == '':
        schema_raw_data['sortorder'] = DEFAULT_SORTORDER
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    _content_type = schema_raw_data.pop('content_type', '')
    schema_raw_data.setdefault('discussion', getattr(self, 'discussion', 0)) # Fallback from album
    _title = schema_raw_data.pop('title','')

    _file = schema_raw_data.pop('file', '')
    if _file != '' and getattr(_file, 'filename', None) == '':
        _file = ''

    #process parameters
    id, _title = cookId(id, _title, _file)
    id = make_id(self, id=id, title=_title, prefix=PREFIX_NYPHOTO)
    schema_raw_data['title'] = _title

    ob = _klass(id, content_type=_content_type, displays=self.displays.copy())
    self.gl_add_languages(ob)
    self._setObject(id, ob)
    ob = self._getOb(id)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
    if form_errors:
        raise ValueError(form_errors.popitem()[1]) # pick a random error

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 1, None
    ob.approveThis(approved, approved_by)

    #extra settings
    ob.update_data(_file)
    ob.submitThis()
    if ob.discussion:
        ob.open_for_comments()
    else:
        ob.close_for_comments()
    self.recatalogNyObject(ob)

    #redirect if case
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url())

    return ob.getId()

class NyPhoto(NyContentData, NyAttributes, photo_archive_base, NyFSContainer, NyContentType):
    """ """

    implements(INyPhoto)

    meta_type = METATYPE_NYPHOTO
    icon = 'misc_/NaayaPhotoArchive/NyPhoto.gif'
    icon_marked = 'misc_/NaayaPhotoArchive/NyPhoto_marked.gif'

    manage_options = ((
        {'label': 'Displays', 'action': 'manage_displays_html'},
        ) + NyFSContainer.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, content_type='', displays={}):
        """ """
        #image stuff
        self.id = id
        self.content_type = content_type
        self.displays = displays
        NyFSContainer.__init__(self)
        NyContentData.__init__(self)
    
    def _getDisplayId(self, display='Original', watermark = False):
        """ Returns real display object id.
        """
        if watermark:
            watermark = 'watermark-'
        else:
            watermark = ''
        if display == 'Original':
            return watermark + self.getId()
        return watermark + display + '-' + self.getId()
    
    def _getDisplay(self, display='Original', watermark=False):
        """ Returns display object
        """
        if not self.is_generated(display, watermark):
            self.__generate_display(display, watermark)
        display = self._getDisplayId(display, watermark)
        return self._getOb(display, None)

    def width(self, sid='Original'):
        ob = self._getDisplay(sid)
        return getattr(ob, 'width', 0)
    
    def height(self, sid="Original"):
        ob = self._getDisplay(sid)
        return getattr(ob, 'height', 0)
        
    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self.getLocalProperty('title', lang),
            self.getLocalProperty('author', lang),
            self.getLocalProperty('source', lang),
            self.getLocalProperty('description', lang)])

    #FTP/WebDAV support
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """ Handle HTTP PUT requests. """
        self.dav__init(REQUEST, RESPONSE)
        if hasattr(self, 'dav__simpleifhandler'):
            self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
        file = REQUEST['BODYFILE']

        self.update_data(file)

        RESPONSE.setStatus(204)
        return RESPONSE

    def update_data(self, data, content_type=None, size=None, filename='Original', purge=True, watermark=False):
        if purge:
            self.manage_delObjects(self.objectIds())
        
        filename = self.utCleanupId(filename)
        filename = self._getDisplayId(filename, watermark)
        if filename in self.objectIds():
            self.manage_delObjects([filename])
        
        child_id = self.manage_addFile(filename)
        child = self._getOb(child_id)
        if hasattr(data, '__class__') and data.__class__ is Pdata:
            data = str(data)
        elif getattr(data, 'index_html', None):
            data = data.index_html()
        
        if not isinstance(data, str):
            data = data.read()
        child.content_type, child.width, child.height = getImageInfo(data)
        
        child.manage_upload(data, child.content_type)
        return child.getId()

    #core
    def __get_crop_aspect_ratio_size(self, size):
        img_width, img_height = self.width(), self.height()
        if img_width == img_height:
            return size, size
        
        width = height = size
        sw = float(width) / img_width
        sh = float(height) / img_height
        if img_width > img_height:
            width = int(sh * img_width + 0.5)
        else:
            height = int(sw * img_height + 0.5)
        return width, height
    
    def __get_crop_box(self, width, height):
        if width == height:
            return 0, 0, width, height
        elif width > height:
            return width/2 - height/2, 0, width/2 + height/2, height
        return 0, height/2 - width/2, width, height/2 + width/2
        
    def __get_aspect_ratio_size(self, width, height):
        #return proportional dimensions within desired size
        img_width, img_height = self.width(), self.height()
        sw = float(width) / img_width
        sh = float(height) / img_height
        if sw <= sh: height = int(sw * img_height + 0.5)
        else: width = int(sh * img_width + 0.5)
        return (width, height)

    def __resize(self, display):
        #resize and resample photo
        original_id = self._getDisplayId()
        string_image = StringIO(str(self.get_data(original_id)))
        if display == 'Original':
            return string_image

        crop = False
        width, height = self.displays.get(display, (0, 0))
        # Calculate image width, size
        if not (width and height):
            size = LISTING_DISPLAYS.get(display, self.width())
            width, height = self.__get_crop_aspect_ratio_size(size)
            crop = True
        else:
            width, height = self.__get_aspect_ratio_size(width, height)
        
        # Resize image
        newimg = StringIO()
        img = Image.open(string_image)
        fmt = img.format
        try: img = img.resize((width, height), Image.ANTIALIAS)
        except AttributeError: img = img.resize((width, height))
        
        # Crop if needed
        if crop:
            box = self.__get_crop_box(width, height)
            img = img.crop(box)
            #img.load()
        quality = self._photo_quality(string_image)
        img.save(newimg, fmt, quality=quality)
        newimg.seek(0)
        return newimg

    def _photo_quality(self, datafile):
        """ calculates photo quality of a StringIO object """
        datafile.seek(0)
        img = Image.open(datafile)
        mode = img.mode
        resolution = img.size
        filebytes = len(datafile.getvalue())
        MODEBITS = {
            # bits per pixel for common PIL image modes
            "1": 1, "P": 8, "L": 8, "RGB": 24, "RGBA": 32, "CMYK": 32
            }
        try:
            bits = MODEBITS[mode]
            imagebytes = ((resolution[0] * bits + 7) / 8) * resolution[1]
        except (KeyError):
            return DEFAULT_QUALITY
        else:
            quality = 100 - round(imagebytes / filebytes, 2)
            return quality

    def __generate_display(self, display, watermark=False):
        #generates and stores a display
        if watermark:
            watermark = 'watermark-'
        else:
            watermark = ''
        original_id = self._getDisplayId()
        datafile = self.__resize(display)
        if watermark:
            datafile = self._apply_watermark(datafile)
        self.update_data(datafile, self.getContentType(original_id),
                        filename=display, purge=False, watermark=watermark)
        import transaction
        if sys.platform == 'win32': 
            # commit the transaction here, so ExtFile has a chance to rename 
            # the file; otherwise an iterator will stream the image to the 
            # client while holding an open filehandle, which will make 
            # the ExtFile rename operation fail with an OSError. 
            transaction.commit()

    # Image edit
    
    def _apply_watermark(self, datafile):
        text = self.aq_parent.watermark_text
        FONT = os.path.join(os.path.dirname(__file__), 'fonts', 'VeraSeBd.ttf')
        img = Image.open(datafile)
        newimg = StringIO()
        fmt = img.format
        watermark = Image.new("RGBA", (img.size[0], img.size[1]))
        draw = ImageDraw.ImageDraw(watermark, "RGBA")
        size = 0
        while True:
            size += 1
            nextfont = ImageFont.truetype(FONT, size)
            nexttextwidth, nexttextheight = nextfont.getsize(text)
            if nexttextwidth+nexttextheight/3 > watermark.size[0]:
                break
            font = nextfont
            textwidth, textheight = nexttextwidth, nexttextheight
        draw.setfont(font)
        draw.text(((watermark.size[0]-textwidth)/2,
                   (watermark.size[1]-textheight)/2), text)
        watermark = watermark.rotate(degrees(atan(float(img.size[1])/img.size[0])),
                                 Image.BICUBIC)
        mask = watermark.convert("L").point(lambda x: min(x, 88))
        watermark.putalpha(mask)
        img.paste(watermark, None, watermark)
        quality = self._photo_quality(datafile)
        img.save(newimg, fmt, quality=quality)
        newimg.seek(0)
        return newimg

    def _transpose(self, method):
        original_id = self._getDisplayId()
        newimg = StringIO()
        string_img = StringIO(str(self.get_data(original_id)))
        img = Image.open(string_img)
        quality = self._photo_quality(string_img)
        fmt = img.format
        img = img.transpose(method)
        img.save(newimg, fmt, quality=quality)
        newimg.seek(0)
        return newimg

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'rotate_left')
    def rotate_left(self, REQUEST=None):
        """ Rotate image left.
        """
        original_id = self._getDisplayId()
        img = self._transpose(Image.ROTATE_90)
        self.update_data(img, self.getContentType(original_id), filename='Original')
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'rotate_right')
    def rotate_right(self, REQUEST=None):
        """ Rotate image right.
        """
        original_id = self._getDisplayId()
        img = self._transpose(Image.ROTATE_270)
        self.update_data(img, self.getContentType(original_id), filename='Original')
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect(self.absolute_url())
    
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'flip_horizontally')
    def flip_horizontally(self, REQUEST=None):
        """ Flip image left-right.
        """
        original_id = self._getDisplayId()
        img = self._transpose(Image.FLIP_LEFT_RIGHT)
        self.update_data(img, self.getContentType(original_id), filename='Original')
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect(self.absolute_url())
    
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'flip_vertically')
    def flip_vertically(self, REQUEST=None):
        """ Flip image top-botton.
        """
        original_id = self._getDisplayId()
        img = self._transpose(Image.FLIP_TOP_BOTTOM)
        self.update_data(img, self.getContentType(original_id), filename='Original')
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect(self.absolute_url())

    #api
    def getZipData(self):
        display = self._getDisplayId()
        return str(self.get_data(display))

    def get_displays(self):
        #returns a list with all dispays minus 'Thumbnail'
        l = self.displays.keys()
        l.remove('Thumbnail')
        l.sort(lambda x,y,d=self.displays: cmp(d[x][0]*d[x][1], d[y][0]*d[y][1]))
        return l

    @deprecate('NyPhoto.get_displays_edit is deprecated and will be removed in the next version.')
    def get_displays_edit(self):
        #returns a list with all dispays minus 'Thumbnail'
        l = self.displays.keys()
        l.sort(lambda x,y,d=self.displays: cmp(d[x][0]*d[x][1], d[y][0]*d[y][1]))
        return l

    def is_generated(self, display, watermark=False):
        #return whether display has been generated
        display = self._getDisplayId(display, watermark)
        return display in self.objectIds()

    @deprecate('NyPhoto.get_display_info is deprecated and will be removed in the next version.')
    def get_display_info(self, display):
        #returns widht, height, size of the specified display
        display_id = self._getDisplayId(display)
        photo = self._getDisplay(display)
        if photo:
            return (photo.width(display), photo.height(display), photo.get_size(display_id))
        else:
            return (None, None, None)

    @deprecate('NyPhoto.get_display_js is deprecated and will be removed in the next version.')
    def get_display_js(self):
        #get code for picture displays
        js_data = []
        js_data.append('<script type="text/javascript"><!--')
        js_data.append('function img_display(display) { document.frmDisplay.imgDisplay.src = "%s" + "/view?display=" + display }' % self.absolute_url())
        js_data.append('// --></script>')
        return '\n'.join(js_data)

    security.declareProtected(view_management_screens, 'manageDisplays')
    def manageDisplays(self, display=None, width=None, height=None, REQUEST=None):
        """ """
        if display and width and height:
            for x,y,z in zip(display,width,height):
                self.displays[x] = (int(y), int(z))
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_displays_html?save=ok')

    security.declareProtected(view_management_screens, 'manageGenerateDisplays')
    def manageGenerateDisplays(self, REQUEST=None):
        """ """
        self.managePurgeDisplays()
        map(lambda x: self.__generate_display(x), self.displays.keys())
        
        if REQUEST: REQUEST.RESPONSE.redirect('manage_displays_html?save=ok')

    security.declareProtected(view_management_screens, 'managePurgeDisplays')
    def managePurgeDisplays(self, REQUEST=None):
        """ """
        original = self._getDisplayId()
        to_delete = [x for x in self.objectIds() if x != original]
        self.manage_delObjects(to_delete)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_displays_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """

        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        if schema_raw_data.get('sortorder', '') == '':
            schema_raw_data['sortorder'] = DEFAULT_SORTORDER
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)

        _file = schema_raw_data.pop('file', '')

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
                return
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

        # upload image
        if getattr(_file, 'filename', ''):
            self.saveUpload(_file, _lang)

        if self.discussion:
            self.open_for_comments()
        else:
            self.close_for_comments()
        self._p_changed = 1

        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveUpload')
    def saveUpload(self, file='', lang=None, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        if file != '':
            if hasattr(file, 'filename'):
                if file.filename != '':
                    self.update_data(file)
        if lang is None: lang = self.get_default_language()
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(view_permission, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        display = self._getDisplayId()
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        self.REQUEST.RESPONSE.setHeader('Content-Length', self.get_size(display))
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.id)
        return self.view(REQUEST=REQUEST)

    security.declareProtected(view_permission, 'view')
    def view(self, REQUEST, display='', **kwargs):
        """ """
        if not self.displays.has_key(display):
            if not LISTING_DISPLAYS.has_key(display):
                display = 'Original'
        if not self.check_view_photo_permission(display):
            raise Unauthorized
        if self.aq_parent.watermark_text:
            watermark = True
        else:
            watermark = False
        photo = self._getDisplay(display, watermark)
        return photo.index_html(REQUEST=REQUEST)
    
    def check_view_photo_permission(self, display):
        if display == 'Original':
            restrict_original = getattr(self, 'restrict_original', False)
            if restrict_original and not self.checkPermissionEditObject():
                return False
        return True

    security.declareProtected(view_permission, 'previous')
    def previous(self):
        """ Returns previous photo in parent"""
        album = self.getParentNode()
        photos = album.getSortedObjectIds()
        try:
            index = photos.index(self.getId()) - 1
            if index < 0:
                return ''
            return '/'.join((album.absolute_url(), photos[index]))
        except (ValueError, IndexError):
            return ''
    
    security.declareProtected(view_permission, 'next')
    def next(self):
        """ Returns next photo in parent """
        album = self.getParentNode()
        photos = album.getSortedObjectIds()
        try:
            index = photos.index(self.getId()) + 1
            return '/'.join((album.absolute_url(), photos[index]))
        except (ValueError, IndexError):
            return ''
    
    security.declareProtected(view_permission, 'getAlbumTitle')
    def getAlbumTitle(self):
        return self.getParentNode().title_or_id()
    
    def _fix_after_cut_copy(self, item):
        item_id = item.getId()
        if item_id.startswith('copy') and item_id not in item.objectIds():
            original_id = re.sub(r'^copy\d*_of_', '', item.getId())
            item.update_data(item.get_data(original_id))
        return item
    
    #zmi pages
    security.declareProtected(view_management_screens, 'manage_displays_html')
    manage_displays_html = PageTemplateFile('zpt/photo_manage_displays', globals())

    #site pages
    security.declareProtected(view_permission, 'index_html')
    index_html = PageTemplateFile('zpt/photo_index', globals())
    
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/photo_edit', globals())

    def _delete_watermarked_photos(self):
        self.manage_delObjects\
            ([photo_id for photo_id in self.objectIds() if photo_id.startswith('watermark-')])

    _minimap_template = PageTemplateFile('zpt/minimap', globals())
    def minimap(self):
        if self.geo_location not in (None, Geo()):
            simplepoints = [{'lat': self.geo_location.lat, 'lon': self.geo_location.lon}]
        elif self.aq_parent.geo_location not in (None, Geo()):
            simplepoints = [{'lat': self.aq_parent.geo_location.lat, 'lon': self.aq_parent.geo_location.lon}]
        else:
            return ""
        json_simplepoints = json.dumps(simplepoints, default=json_encode)
        return self._minimap_template(points=json_simplepoints)

def json_encode(ob):
    """ try to encode some known value types to JSON """
    if isinstance(ob, Decimal):
        return float(ob)
    raise ValueError

InitializeClass(NyPhoto)
