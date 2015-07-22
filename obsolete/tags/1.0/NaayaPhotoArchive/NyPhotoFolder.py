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
from string import rfind
from PIL import Image
from cStringIO import StringIO

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyContainer import NyContainer
from Products.Naaya.constants import *
from Products.NaayaCore.managers.utils import batch_utils, ZZipFile
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
import NyPhoto

manage_addNyPhotoFolder_html = PageTemplateFile('zpt/photofolder_manage_add', globals())
def manage_addNyPhotoFolder(self, id='', title='', quality='', discussion='',
    lang=None, REQUEST=None):
    """
    Create a PhotoFolder type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYPHOTOFOLDER + self.utGenRandomId(6)
    try: quality = abs(int(quality))
    except: quality = DEFAULT_QUALITY
    if quality <= 0 or quality > 100: quality = DEFAULT_QUALITY
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    releasedate = self.process_releasedate()
    if lang is None: lang = self.gl_get_selected_language()
    #create object
    ob = NyPhotoFolder(id, title, quality, approved, approved_by, releasedate, lang)
    self.gl_add_languages(ob)
    self._setObject(id, ob)
    #extra settings
    ob = self._getOb(id)
    ob.submitThis()
    if discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    #redirect if case
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class NyPhotoFolder(NyAttributes, LocalPropertyManager, NyContainer):
    """ """

    meta_type = METATYPE_NYPHOTOFOLDER
    icon = 'misc_/NaayaPhotoArchive/NyPhotoFolder.gif'

    manage_options = (
        NyContainer.manage_options[0:2]
        +
        (
            {'label': 'Properties', 'action': 'manage_edit_html'},
            {'label': 'Displays', 'action': 'manage_displays_html'},
        )
        +
        NyContainer.manage_options[3:8]
    )

    meta_types = (
        {'name': METATYPE_NYPHOTO, 'action': 'manage_addNyPhoto_html'},
    )
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'manage_addNyPhoto_html')
    manage_addNyPhoto_html = NyPhoto.manage_addNyPhoto_html

    security.declareProtected(PERMISSION_ADD_PHOTO, 'addNyPhoto')
    addNyPhoto = NyPhoto.addNyPhoto

    title = LocalProperty('title')

    def __init__(self, id, title, quality, approved, approved_by, releasedate, lang):
        """ """
        self.id = id
        NyContainer.__dict__['__init__'](self)
        self._setLocalPropValue('title', lang, title)
        self.quality = quality
        self.displays = DEFAULT_DISPLAYS.copy()
        self.approved = approved
        self.approved_by = approved_by
        self.releasedate = releasedate

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self.getLocalProperty('title', lang)])

    #FTP/WebDAV support
    def PUT_factory(self, name, typ, body):
        """ Create Photo objects by default for image types. """
        if typ[:6] == 'image/':
            if self.glCheckPermissionPublishObjects():
                approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
            else:
                approved, approved_by = 0, None
            ob = NyPhoto.NyPhoto(name, '', '', '', '', DEFAULT_SORTORDER, 0,
                None, None, '', typ, DEFAULT_QUALITY,
                self.displays.copy(), approved, approved_by,
                self.process_releasedate(),
                self.gl_get_selected_language())
            self.gl_add_languages(ob)
            ob.submitThis()
            return ob
        return None

    #api
    def get_photofolder_object(self): return self
    def get_photofolder_path(self, p=0): return self.absolute_url(p)
    def getObjects(self): return [x for x in self.objectValues(METATYPE_NYPHOTO) if x.submitted==1]
    def getPendingObjects(self): return [x for x in self.getObjects() if x.approved==0 and x.submitted==1]
    def getPendingContent(self): return self.getPendingObjects()
    def getPublishedObjects(self): return [x for x in self.getObjects() if x.approved==1 and x.submitted==1]
    def getPendingFolders(self): return []
    def getPublishedFolders(self): return []

    def getObjectsForValidation(self): return []
    def count_notok_objects(self): return 0
    def count_notchecked_objects(self): return 0

    def checkPermissionAddPhotos(self):
        return self.checkPermission(PERMISSION_ADD_PHOTO)

    def get_displays_edit(self):
        #returns a list with all dispays minus 'Thumbnail'
        l = self.displays.keys()
        l.sort(lambda x,y,d=self.displays: cmp(d[x][0]*d[x][1], d[y][0]*d[y][1]))
        return l

    def process_querystring(self, p_querystring):
        #eliminates empty values and the 'start' key
        if p_querystring:
            l_qsparts = p_querystring.split('&')
            for i in range(len(l_qsparts)):
                if l_qsparts[i] != '':
                    l_qsparts_tuple = l_qsparts[i].split('=', 1)
                    l_key = self.utUnquote(l_qsparts_tuple[0])
                    l_value = self.utUnquote(l_qsparts_tuple[1])
                    if l_value == '' or l_key == 'start':
                        l_qsparts[i] = ''
            return '&'.join(filter(None, l_qsparts))
        else:
            return ''

    def _page_result(self, p_result, p_start):
        #Returns results with paging information
        l_paging_information = (0, 0, 0, -1, -1, 0, NUMBER_OF_RESULTS_PER_PAGE, [0])
        try: p_start = abs(int(p_start))
        except: p_start = 0
        if len(p_result) > 0:
            l_paging_information = batch_utils(NUMBER_OF_RESULTS_PER_PAGE, len(p_result), p_start).butGetPagingInformations()
        if len(p_result) > 0:
            return (l_paging_information,
                self.utSplitSequence(p_result[l_paging_information[0]:l_paging_information[1]], NUMBER_OF_RESULTS_PER_LINE))
        else:
            return (l_paging_information, self.utSplitSequence([], NUMBER_OF_RESULTS_PER_LINE))

    def query_photos(self, q='', f='', p_start=0):
        #query/filter photos
        lang = self.getLocalizer().get_selected_language()
        if q == '': q = None
        if f == '': f = None
        else: f = 1
        return self._page_result(self.query_objects_ex(meta_type=METATYPE_NYPHOTO, q=q, lang=lang, path='/'.join(self.getPhysicalPath()), topitem=f, approved=1, sort_on='releasedate', sort_order='reverse'), p_start)

    def _page_result_admin(self, p_result, p_start):
        #Returns results with paging information
        l_paging_information = (0, 0, 0, -1, -1, 0, NUMBER_OF_RESULTS_PER_PAGE, [0])
        try: p_start = abs(int(p_start))
        except: p_start = 0
        if len(p_result) > 0:
            l_paging_information = batch_utils(NUMBER_OF_RESULTS_PER_PAGE, len(p_result), p_start).butGetPagingInformations()
        if len(p_result) > 0:
            return (l_paging_information, self.get_archive_listing(p_result[l_paging_information[0]:l_paging_information[1]]))
        else:
            return (l_paging_information, self.get_archive_listing([]))

    def query_photos_admin(self, q='', f='', p_start=0):
        #query/filter photos
        lang = self.getLocalizer().get_selected_language()
        if q == '': q = None
        if f == '': f = None
        else: f = 1
        return self._page_result_admin(self.query_objects_ex(meta_type=METATYPE_NYPHOTO, q=q, lang=lang, path='/'.join(self.getPhysicalPath()), topitem=f, approved=1, sort_on='releasedate', sort_order='reverse'), p_start)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', quality='', approved='', releasedate='',
        discussion='', REQUEST=None):
        """ """
        try: quality = abs(int(quality))
        except: quality = DEFAULT_QUALITY
        if quality <= 0 or quality > 100: quality = DEFAULT_QUALITY
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self.quality = quality
        if approved != self.approved:
            self.approved = approved
            if approved == 0: self.approved_by = None
            else: self.approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.releasedate = releasedate
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
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
        map(lambda x: x.manageGenerateDisplays(), self.getObjects())
        if REQUEST: REQUEST.RESPONSE.redirect('manage_displays_html?save=ok')

    security.declareProtected(view_management_screens, 'managePurgeDisplays')
    def managePurgeDisplays(self, REQUEST=None):
        """ """
        map(lambda x: x.managePurgeDisplays(), self.getObjects())
        if REQUEST: REQUEST.RESPONSE.redirect('manage_displays_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', quality='', discussion='', lang=None,
        REQUEST=None):
        """ """
        try: quality = abs(int(quality))
        except: quality = DEFAULT_QUALITY
        if quality <= 0 or quality > 100: quality = DEFAULT_QUALITY
        if lang is None: lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self.quality = quality
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(view, 'downloadAllObjects')
    def downloadAllObjects(self, REQUEST=None):
        """
        Download all pictures in a zip file.
        """
        return self.utGenerateZip(
            name=self.id,
            objects=self.getPublishedObjects(),
            RESPONSE=REQUEST.RESPONSE
        )

    security.declareProtected(view, 'downloadObjects')
    def downloadObjects(self, ids=None, REQUEST=None):
        """
        Download selected pictures in a zip file.
        """
        return self.utGenerateZip(
            name=self.id,
            objects=map(self._getOb, self.utConvertToList(ids)),
            RESPONSE=REQUEST.RESPONSE
        )

    security.declareProtected(PERMISSION_ADD_PHOTO, 'uploadZip')
    def uploadZip(self, file='', REQUEST=None):
        """
        Expand a zipfile into a number of Photos.
        Go through the zipfile and for each file create a I{Naaya Photo} object.
        """
        err = ''
        try:
            if type(file) is not type('') and hasattr(file,'filename'):
                # According to the zipfile.py ZipFile just needs a file-like object
                zf = ZZipFile(file)
                for name in zf.namelist():
                    zf.setcurrentfile(name)
                    content = zf.read()
                    if self.isValidImage(content):
                        id = name[max(rfind(name,'/'), rfind(name,'\\'), rfind(name,':'))+1:]
                        ob = self._getOb(id, None)
                        if ob: id = '%s_%s' % (PREFIX_NYPHOTO + self.utGenRandomId(6), id)
                        self.addNyPhoto(id=id, title=name, file=content, lang=self.gl_get_selected_language())
            else:
                err = 'Invalid zip file.'
        except Exception, error:
            err = str(error)
        if REQUEST:
            if err != '':
                self.setSessionErrors([err])
                return REQUEST.RESPONSE.redirect('%s/uploadzip_html' % self.absolute_url())
            else:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                return REQUEST.RESPONSE.redirect('%s/admin_html' % self.absolute_url())

    def isValidImage(self, file):
        """
        Test if the specified uploaded B{file} is a valid image.
        """
        try:
            Image.open(StringIO(file))
            return 1
        except IOError: # Python Imaging Library doesn't recognize it as an image
            return 0

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteObjects')
    def deleteObjects(self, ids=None, REQUEST=None):
        """ """
        if ids is None: ids = []
        else: ids = self.utConvertToList(ids)
        try: self.manage_delObjects(ids)
        except: error = 1
        else: error = 0
        if REQUEST:
            if error: self.setSessionErrors(['Error while delete data.'])
            else: self.setSessionInfo(['Item(s) deleted.'])
            REQUEST.RESPONSE.redirect('%s/admin_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'setTopPhotoObjects')
    def setTopPhotoObjects(self, REQUEST=None):
        """ """
        try:
            for item in self.objectValues():
                if hasattr(item, 'topitem'): item.topitem = 0
                if REQUEST.has_key('topitem_' + item.id):
                    item.topitem = 1
                item._p_changed = 1
                self.recatalogNyObject(item)
        except: self.setSessionErrors(['Error while updating data.'])
        else: self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
        if REQUEST: REQUEST.RESPONSE.redirect('%s/admin_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processPendingContent')
    def processPendingContent(self, appids=[], delids=[], REQUEST=None):
        """
        Process the pending content inside this folder.

        Objects with ids in appids list will be approved.

        Objects with ids in delids will be deleted.
        """
        for id in self.utConvertToList(appids):
            try:
                ob = self._getOb(id)
                ob.approveThis()
                self.recatalogNyObject(ob)
            except:
                pass
        for id in self.utConvertToList(delids):
            try: self._delObject(id)
            except: pass
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/basketofapprovals_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processPublishedContent')
    def processPublishedContent(self, appids=[], delids=[], REQUEST=None):
        """
        Process the published content inside this folder.

        Objects with ids in appids list will be unapproved.

        Objects with ids in delids will be deleted.
        """
        for id in self.utConvertToList(appids):
            try:
                ob = self._getOb(id)
                ob.approveThis()
                ob.approved = 0
                ob.approved_by = None
                self.recatalogNyObject(ob)
            except:
                pass
        for id in self.utConvertToList(delids):
            try: self._delObject(id)
            except: pass
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/basketofapprovals_html' % self.absolute_url())

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/photofolder_manage_edit', globals())

    security.declareProtected(view_management_screens, 'manage_displays_html')
    manage_displays_html = PageTemplateFile('zpt/photofolder_manage_displays', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/photofolder_index', globals())

    security.declareProtected(view, 'admin_html')
    admin_html = PageTemplateFile('zpt/photofolder_admin', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/photofolder_edit', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'basketofapprovals_html')
    basketofapprovals_html = PageTemplateFile('zpt/photofolder_basketofapprovals', globals())

    security.declareProtected(PERMISSION_ADD_PHOTO, 'photo_add_html')
    photo_add_html = PageTemplateFile('zpt/photo_add', globals())

    security.declareProtected(PERMISSION_ADD_PHOTO, 'uploadzip_html')
    uploadzip_html = PageTemplateFile('zpt/photofolder_uploadzip', globals())

InitializeClass(NyPhotoFolder)
