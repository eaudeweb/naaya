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

#Python imports
import re
from cStringIO import StringIO
import PIL.Image

#Zope imports
from OFS.Image import getImageInfo, cookId, Pdata
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, ftp_access
from AccessControl.Permissions import view as view_permission
#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyFSContainer import NyFSContainer
from Products.Naaya.constants import *
from Products.Localizer.LocalPropertyManager import LocalProperty
from photo_archive import photo_archive

def addNyPhoto(self, id='', title='', description='', coverage='', keywords='',
               sortorder=100, releasedate='', lang=None, author='', source='',
               content_type='', discussion=0, file='', REQUEST=None, **kwargs):
    """
    Create a Photo type of object.
    """
    if self.is_full():
        return None
    
    #process parameters
    id, title = cookId(id, title, file)
    id = self.utCleanupId(id) or self.utGenObjectId(title)
    if not id or self._getOb(id, None):
        id = PREFIX_NYPHOTO + self.utGenRandomId(6)
    try:
        sortorder = abs(int(sortorder))
    except:
        sortorder = DEFAULT_SORTORDER
    displays = self.displays.copy()
    if file != '':
        if hasattr(file, 'filename'):
            if file.filename == '': file = ''
    releasedate = self.process_releasedate(releasedate)
    if lang is None:
        lang = self.gl_get_selected_language()

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    #create object
    
    # Fallback from album
    discussion = discussion or getattr(self, 'discussion', 0)
    
    ob = NyPhoto(id, title, lang,
                 description=description, coverage=coverage, keywords=keywords,
                 sortorder=sortorder, releasedate=releasedate, author=author,
                 source=source, content_type=content_type, displays=displays,
                 discussion=discussion, approved=approved, approved_by=approved_by)

    self.gl_add_languages(ob)
    self._setObject(id, ob)
    #extra settings
    ob = self._getOb(id)
    ob.update_data(file)
    ob.submitThis()
    self.recatalogNyObject(ob)
    #redirect if case
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url())
    return ob.getId()

class NyPhoto(NyAttributes, photo_archive, NyFSContainer):
    """ """

    meta_type = METATYPE_NYPHOTO
    icon = 'misc_/NaayaPhotoArchive/NyPhoto.gif'
    icon_marked = 'misc_/NaayaPhotoArchive/NyPhoto_marked.gif'

    manage_options = ((
        {'label': 'Displays', 'action': 'manage_displays_html'},
        ) + NyFSContainer.manage_options
    )

    security = ClassSecurityInfo()

    author = LocalProperty('author')
    source = LocalProperty('source')

    def __init__(self, id, title, lang, approved=0, approved_by='', **kwargs):
        """ """
        #image stuff
        self.id = id
        self.qulity = 100
        self.content_type = kwargs.get('content_type', '')
        self.displays = kwargs.get('displays', {})
        self.approved = approved
        self.approved_by = approved_by
        NyFSContainer.__init__(self)
        self.save_properties(title, lang, **kwargs)
    
    def _getDisplayId(self, display='Original'):
        """ Returns real display object id.
        """
        if display == 'Original':
            return self.getId()
        return display + '-' + self.getId()
    
    def _getDisplay(self, display='Original'):
        """ Returns display object
        """
        if not self.is_generated(display):
            self.__generate_display(display)
        display = self._getDisplayId(display)
        return self._getOb(display, None)

    def width(self, sid='Original'):
        ob = self._getDisplay(sid)
        return getattr(ob, 'width', 0)
    
    def height(self, sid="Original"):
        ob = self._getDisplay(sid)
        return getattr(ob, 'height', 0)
        
    def save_properties(self, title='', lang=None, **kwargs):
        description = kwargs.get('description', '')
        coverage = kwargs.get('coverage', '')
        keywords = kwargs.get('keywords', '')
        sortorder = kwargs.get('sortorder', 100)
        releasedate = kwargs.get('releasedate', '')
        discussion = kwargs.get('discussion', 0)
        if not lang:
            lang = self.gl_get_selected_language()
        
        photo_archive.save_properties(self, title, description, coverage,
                                      keywords, sortorder, releasedate, lang)
        
        self._setLocalPropValue('author', lang, kwargs.get('author', ''))
        self._setLocalPropValue('source', lang, kwargs.get('source', ''))
        
        if discussion:
            self.open_for_comments()
        else:
            self.close_for_comments()
        self._p_changed = 1
        
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

    def update_data(self, data, content_type=None, size=None, filename='Original', purge=True):
        if purge:
            self.manage_delObjects(self.objectIds())
        
        filename = self.utCleanupId(filename)
        filename = self._getDisplayId(filename)
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
        img = PIL.Image.open(StringIO(str(self.get_data(original_id))))
        fmt = img.format
        try: img = img.resize((width, height), PIL.Image.ANTIALIAS)
        except AttributeError: img = img.resize((width, height))
        
        # Crop if needed
        if crop:
            box = self.__get_crop_box(width, height)
            img = img.crop(box)
            #img.load()
        img.save(newimg, fmt, quality=self.quality)
        newimg.seek(0)
        return newimg

    def __generate_display(self, display):
        #generates and stores a display
        original_id = self._getDisplayId()
        self.update_data(self.__resize(display), self.getContentType(original_id),
                         filename=display, purge=False)
    
    # Image edit
    
    def _transpose(self, method):
        original_id = self._getDisplayId()
        newimg = StringIO()
        img = PIL.Image.open(StringIO(str(self.get_data(original_id))))
        fmt = img.format
        img = img.transpose(method)
        img.save(newimg, fmt, quality=self.quality)
        newimg.seek(0)
        return newimg
        
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'rotate_left')
    def rotate_left(self, REQUEST=None):
        """ Rotate image left.
        """
        original_id = self._getDisplayId()
        img = self._transpose(PIL.Image.ROTATE_90)
        self.update_data(img, self.getContentType(original_id), filename='Original')
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'rotate_right')
    def rotate_right(self, REQUEST=None):
        """ Rotate image right.
        """
        original_id = self._getDisplayId()
        img = self._transpose(PIL.Image.ROTATE_270)
        self.update_data(img, self.getContentType(original_id), filename='Original')
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect(self.absolute_url())
    
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'flip_horizontally')
    def flip_horizontally(self, REQUEST=None):
        """ Flip image left-right.
        """
        original_id = self._getDisplayId()
        img = self._transpose(PIL.Image.FLIP_LEFT_RIGHT)
        self.update_data(img, self.getContentType(original_id), filename='Original')
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect(self.absolute_url())
    
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'flip_vertically')
    def flip_vertically(self, REQUEST=None):
        """ Flip image top-botton.
        """
        original_id = self._getDisplayId()
        img = self._transpose(PIL.Image.FLIP_TOP_BOTTOM)
        self.update_data(img, self.getContentType(original_id), filename='Original')
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
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

    def get_displays_edit(self):
        #returns a list with all dispays minus 'Thumbnail'
        l = self.displays.keys()
        l.sort(lambda x,y,d=self.displays: cmp(d[x][0]*d[x][1], d[y][0]*d[y][1]))
        return l

    def is_generated(self, display):
        #return whether display has been generated
        display = self._getDisplayId(display)
        return display in self.objectIds()

    def get_display_info(self, display):
        #returns widht, height, size of the specified display
        display_id = self._getDisplayId(display)
        photo = self._getDisplay(display)
        if photo:
            return (photo.width(display), photo.height(display), photo.get_size(display_id))
        else:
            return (None, None, None)

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
        
        if REQUEST:
            kwargs.update(REQUEST.form)
        lang = kwargs.setdefault('lang', self.gl_get_selected_language())
        releasedate = kwargs.get('releasedate', '')
        kwargs['releasedate'] = self.process_releasedate(releasedate)
        self.save_properties(**kwargs)

        # upload image
        attached_file = kwargs.get('file', None)
        if getattr(attached_file, 'filename', ''):
            self.saveUpload(attached_file, lang)
        
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

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
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
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
        photo = self._getDisplay(display)
        return photo.index_html(REQUEST=REQUEST)
    
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
    
    security.declareProtected(view_permission, 'getAlbum')
    def getAlbumTitle(self):
        return self.getParentNode().title_or_id()
    
    def _fix_after_cut_copy(self, item):
        item_id = item.getId()
        if item_id.startswith('copy') and item_id not in item.objectIds():
            original_id = re.sub(r'^copy\d*_of_', '', item.getId())
            item.update_data(item.get_data(original_id))
        return item

    def manage_afterClone(self, item):
        self._fix_after_cut_copy(item)
        return NyPhoto.inheritedAttribute("manage_afterClone")(self, item)
    
    def manage_afterAdd(self, item, container):
        self._fix_after_cut_copy(item)
        return NyPhoto.inheritedAttribute("manage_afterAdd")(self, item, container)
    
    #zmi pages
    security.declareProtected(view_management_screens, 'manage_displays_html')
    manage_displays_html = PageTemplateFile('zpt/photo_manage_displays', globals())

    #site pages
    security.declareProtected(view_permission, 'index_html')
    index_html = PageTemplateFile('zpt/photo_index', globals())
    
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/photo_edit', globals())

InitializeClass(NyPhoto)
