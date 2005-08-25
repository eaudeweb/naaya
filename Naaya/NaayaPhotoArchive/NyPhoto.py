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
# Dragos Chirila, Finsiel Romania

#Python imports
from cStringIO import StringIO
import PIL.Image

#Zope imports
from OFS.Image import File, Image, cookId, getImageInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyItem import NyItem
from Products.Naaya.constants import *
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from Products.Localizer.LanguageManager import LanguageManager

manage_addNyPhoto_html = PageTemplateFile('zpt/photo_manage_add', globals())
def addNyPhoto(self, id='', title='', author='', source='', description='', sortorder='',
    topitem='', onfrontfrom='', onfrontto='', file='', precondition='', content_type='',
    quality='', lang=None, REQUEST=None):
    """ """
    id, title = cookId(id, title, file)
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYPHOTO + self.utGenRandomId(6)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if topitem: topitem = 1
    else: topitem = 0
    onfrontfrom = self.utConvertStringToDateTimeObj(onfrontfrom)
    onfrontto = self.utConvertStringToDateTimeObj(onfrontto)
    try: quality = abs(int(quality))
    except: quality = DEFAULT_QUALITY
    if quality <= 0 or quality > 100: quality = DEFAULT_QUALITY
    displays = self.displays.copy()
    if self.checkPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    releasedate = self.utGetTodayDate()
    if lang is None: lang = self.gl_get_selected_language()
    content_type, width, height = getImageInfo(file)
    ob = NyPhoto(id, title, author, source, description, sortorder, topitem,
        onfrontfrom, onfrontto, file, precondition, content_type, width, height,
        quality, displays, approved, approved_by, releasedate, lang)
    self.gl_add_languages(ob)
    self._setObject(id, ob)
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'manage_addNyPhoto_html' or l_referer.find('manage_addNyPhoto_html') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'photo_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/note_html' % self.getSitePath())

class NyPhoto(NyAttributes, LocalPropertyManager, NyItem, File):
    """ """

    meta_type = METATYPE_NYPHOTO
    icon = 'misc_/NaayaPhotoArchive/NyPhoto.gif'
    icon_marked = 'misc_/NaayaPhotoArchive/NyPhoto_marked.gif'

    manage_options = (
        (
            {'label': 'Properties', 'action': 'manage_edit_html'},
            {'label': 'Displays', 'action': 'manage_displays_html'},
        )
        +
        (
            File.manage_options[1],
        )
        +
        NyItem.manage_options
        +
        LanguageManager.manage_options
    )

    security = ClassSecurityInfo()

    title = LocalProperty('title')
    author = LocalProperty('author')
    source = LocalProperty('source')
    description = LocalProperty('description')

    def __init__(self, id, title, author, source, description, sortorder,
        topitem, onfrontfrom, onfrontto, file, precondition, content_type,
        width, height, quality, displays, approved, approved_by, releasedate, lang):
        """ """
        File.__dict__['__init__'](self, id, title, file, content_type, precondition)
        self.id = id
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('author', lang, author)
        self._setLocalPropValue('source', lang, source)
        self._setLocalPropValue('description', lang, description)
        self.sortorder = sortorder
        self.topitem = topitem
        self.onfrontfrom = onfrontfrom
        self.onfrontto = onfrontto
        self.width = width
        self.height = height
        self.quality = quality
        self.displays = displays
        self.approved = approved
        self.approved_by = approved_by
        self.releasedate = releasedate
        self.__photos = {}

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self.getLocalProperty('title', lang),
            self.getLocalProperty('author', lang),
            self.getLocalProperty('source', lang),
            self.getLocalProperty('description', lang)])

    #core
    def __get_aspect_ratio_size(self, width, height):
        #return proportional dimensions within desired size
        img_width, img_height = self.width, self.height
        sw = float(width) / img_width
        sh = float(height) / img_height
        if sw <= sh: height = int(sw * img_height + 0.5)
        else: width = int(sh * img_width + 0.5)
        return (width, height)

    def __resize(self, display):
        #resize and resample photo
        width, height = self.displays.get(display, (self.width, self.height))
        width, height = self.__get_aspect_ratio_size(width, height)
        newimg = StringIO()
        img = PIL.Image.open(StringIO(str(self.data)))
        fmt = img.format
        try: img = img.resize((width, height), PIL.Image.ANTIALIAS)
        except AttributeError: img = img.resize((width, height))
        img.save(newimg, fmt, quality=self.quality)
        newimg.seek(0)
        return Image('10', '', newimg)

    def __generate_display(self, display):
        #generates and stores a display
        self.__photos[display] = self.__resize(display)
        self._p_changed = 1

    #api
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
        return self.__photos.has_key(display)

    def get_display_info(self, display):
        #returns widht, height, size of the specified display
        photo = self.__photos.get(display, None)
        if photo:
            return (photo.width, photo.height, photo.size)
        else:
            return (None, None, None)

    def get_display_js(self):
        #get code for picture displays
        js_data = []
        js_data.append('<script language="javascript" type="text/javascript"><!--')
        js_data.append('function img_display(display) { document.frmDisplay.imgDisplay.src = "%s" + "/view?display=" + display }' % self.absolute_url())
        js_data.append('// --></script>')
        return '\n'.join(js_data)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', author='', source='', description='',
        sortorder='', approved='', topitem='', onfrontfrom='', onfrontto='',
        content_type='', quality='', releasedate='', REQUEST=None):
        """ """
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        if topitem: topitem = 1
        else: topitem = 0
        onfrontfrom = self.utConvertStringToDateTimeObj(onfrontfrom)
        onfrontto = self.utConvertStringToDateTimeObj(onfrontto)
        try: quality = abs(int(quality))
        except: quality = DEFAULT_QUALITY
        if quality <= 0 or quality > 100: quality = DEFAULT_QUALITY
        releasedate = self.utConvertStringToDateTimeObj(releasedate)
        if releasedate is None: releasedate = self.releasedate
        lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('author', lang, author)
        self._setLocalPropValue('source', lang, source)
        self._setLocalPropValue('description', lang, description)
        self.sortorder = sortorder
        self.topitem = topitem
        self.onfrontfrom = onfrontfrom
        self.onfrontto = onfrontto
        self.content_type = content_type
        self.quality = quality
        if approved != self.approved:
            self.approved = approved
            if approved == 0: self.approved_by = None
            else: self.approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.releasedate = releasedate
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'manageUpload')
    def manageUpload(self, file='', REQUEST=None):
        """ """
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        self.manage_upload(file)
        self.managePurgeDisplays()
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

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
        self.__photos = {}
        map(lambda x: self.__generate_display(x), self.displays.keys())
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_displays_html?save=ok')

    security.declareProtected(view_management_screens, 'managePurgeDisplays')
    def managePurgeDisplays(self, REQUEST=None):
        """ """
        self.__photos = {}
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_displays_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', author='', source='', description='',
        sortorder='', topitem='', onfrontfrom='', onfrontto='', content_type='',
        quality='', releasedate='', lang=None, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if topitem: topitem = 1
        else: topitem = 0
        onfrontfrom = self.utConvertStringToDateTimeObj(onfrontfrom)
        onfrontto = self.utConvertStringToDateTimeObj(onfrontto)
        try: quality = abs(int(quality))
        except: quality = DEFAULT_QUALITY
        if quality <= 0 or quality > 100: quality = DEFAULT_QUALITY
        releasedate = self.utConvertStringToDateTimeObj(releasedate)
        if releasedate is None: releasedate = self.releasedate
        if lang is None: lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('author', lang, author)
        self._setLocalPropValue('source', lang, source)
        self._setLocalPropValue('description', lang, description)
        self.sortorder = sortorder
        self.topitem = topitem
        self.onfrontfrom = onfrontfrom
        self.onfrontto = onfrontto
        self.content_type = content_type
        self.quality = quality
        self.releasedate = releasedate
        self._p_changed = 1
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
        if lang is None: lang = self.get_default_language()
        self.manage_upload(file)
        self.managePurgeDisplays()
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/photo_manage_edit', globals())

    security.declareProtected(view_management_screens, 'manage_displays_html')
    manage_displays_html = PageTemplateFile('zpt/photo_manage_displays', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/photo_index', globals())

    security.declareProtected(view, 'download')
    def download(self, REQUEST, RESPONSE):
        """ """
        self.REQUEST.RESPONSE.setHeader('Content-Type', self.content_type)
        self.REQUEST.RESPONSE.setHeader('Content-Length', self.size)
        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=' + self.id)
        return NyPhoto.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

    security.declareProtected(view, 'view')
    def view(self, REQUEST, RESPONSE, display=None):
        """ """
        if display and self.displays.has_key(display):
            if not self.is_generated(display):
                self.__generate_display(display)
            return self.__photos[display].index_html(REQUEST, RESPONSE)
        return NyPhoto.inheritedAttribute('index_html')(self, REQUEST, RESPONSE)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/photo_edit', globals())

InitializeClass(NyPhoto)
