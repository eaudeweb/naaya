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
from photo_archive import photo_archive
import NyPhoto
import zLOG

def manage_addNyPhotoFolder(self, id='', title='', description='', coverage='',
                            keywords='', sortorder=100, releasedate='', 
                            lang=None, author='', source='', discussion=0,
                            file=None, REQUEST=None, **kwargs):
    """
    Create a PhotoFolder type of object.
    """
    #process parameters
    id = self.utCleanupId(id) or self.utGenObjectId(title)
    if not id or self._getOb(id, None):
        id = PREFIX_NYPHOTOFOLDER + self.utGenRandomId(6)

    releasedate = self.process_releasedate()
    if lang is None:
        lang = self.gl_get_selected_language()
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None

    #create object
    ob = NyPhotoFolder(id, title, lang,
                       description=description, coverage=coverage,
                       keywords=keywords, sortorder=sortorder,
                       releasedate=releasedate, author=author, source=source,
                       discussion=discussion, 
                       approved=approved, approved_by=approved_by)

    self.gl_add_languages(ob)
    self._setObject(id, ob)
    #extra settings
    ob = self._getOb(id)
    # file
    if getattr(file, 'filename', None):
        ob.uploadPhotoOrZip(file)
    
    ob.submitThis()
    self.recatalogNyObject(ob)
    
    #redirect if case
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url())
    return ob.getId()

class NyPhotoFolder(NyAttributes, photo_archive, NyContainer):
    """ """

    meta_type = METATYPE_NYPHOTOFOLDER
    meta_label = METALABEL_NYPHOTOFOLDER
    icon = 'misc_/NaayaPhotoArchive/NyPhotoFolder.gif'

    manage_options = (
        NyContainer.manage_options[0:2]
        +
        (
            {'label': 'Displays', 'action': 'manage_displays_html'},
        )
        +
        NyContainer.manage_options[3:8]
    )

    meta_types = (
        {'name': METATYPE_NYPHOTO, 'action': 'photo_add_html'},
    )
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    security.declareProtected(PERMISSION_ADD_PHOTO, 'addNyPhoto')
    addNyPhoto = NyPhoto.addNyPhoto

    title = LocalProperty('title')
    author = LocalProperty('author')
    source = LocalProperty('source')
    cover = ''
    max_photos = 100
    photos_per_page = 50

    def __init__(self, id, title, lang, approved=0, approved_by='', **kwargs):
        self.id = id
        self.quality = 100
        self.displays = DEFAULT_DISPLAYS.copy()
        self.approved = approved
        self.approved_by = approved_by
        NyContainer.__dict__['__init__'](self)
        self.save_properties(title, lang, **kwargs)
        
    def save_properties(self, title='', lang=None, 
                        description='', coverage='', keywords='', sortorder=100,
                        releasedate='', discussion=0, author='', source='',
                        cover='', max_photos=100, photos_per_page=50, **kwargs):
        if not lang:
            lang = self.gl_get_selected_language()
        
        self._setPropValue('cover', cover)
        self._setPropValue('max_photos', max_photos)
        self._setPropValue('photos_per_page', photos_per_page)
        self._setLocalPropValue('author', lang, author)
        self._setLocalPropValue('source', lang, source)
        photo_archive.save_properties(self, title, description, coverage,
                                      keywords, sortorder, releasedate, lang)
        
        if discussion:
            self.open_for_comments()
        else:
            self.close_for_comments()
        self._p_changed = 1

    security.declarePrivate('open_for_comments')
    def open_for_comments(self):
        """
        Enable(open) comments.
        """
        NyContainer.open_for_comments(self)
        for photo in self.getObjects():
            photo.open_for_comments()
            
    security.declarePrivate('close_for_comments')
    def close_for_comments(self):
        """
        Disable(close) comments.
        """
        NyContainer.close_for_comments(self)
        for photo in self.getObjects():
            photo.close_for_comments()

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
    def get_photofolder_object(self):
        return self

    def get_photofolder_path(self, p=0):
        return self.absolute_url(p)

    def getObjects(self):
        return [x for x in self.objectValues(METATYPE_NYPHOTO) if x.submitted==1]
    
    def getObjectIds(self):
        return [x for x, y in self.objectItems(METATYPE_NYPHOTO) if y.submitted==1]
    
    def getSortedObjects(self, query=''):
        if not query:
            return self.sort_objects(self.getObjects())
        return self.query_photos(query)[1]
    
    def getSortedObjectIds(self):
        return [x.getId() for x in self.getSortedObjects()]

    def getPendingObjects(self):
        return [x for x in self.getObjects() if x.approved==0 and x.submitted==1]

    def getPendingContent(self):
        return self.getPendingObjects()

    def getPublishedObjects(self):
        return [x for x in self.getObjects() if x.approved==1 and x.submitted==1]

    def getPendingFolders(self):
        return []

    def getPublishedFolders(self):
        return []

    def getObjectsForValidation(self):
        return []

    def count_notok_objects(self):
        return 0

    def count_notchecked_objects(self):
        return 0

    def checkPermissionAddPhotos(self):
        return self.checkPermission(PERMISSION_ADD_PHOTO)

    security.declareProtected(view, 'get_cover')
    def get_cover(self):
        """ Returns photo folder cover image as a string
        """
        photos = self.getSortedObjects()
        # No photo in album, no cover available
        if not photos:
            return ''
        # self.cover is not set, return first photo as default cover
        if not self.cover:
            return photos[0].getId()
        # self.cover is not in album anymore, return first photo as default
        if self.cover and self.cover not in self.objectIds():
            return photos[0].getId()
        return self.cover
    
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

    def _page_result(self, p_result, p_start, batch=False):
        #Returns results with paging information
        l_paging_information = (0, 0, 0, -1, -1, 0, NUMBER_OF_RESULTS_PER_PAGE, [0])
        try: p_start = abs(int(p_start))
        except: p_start = 0
        if not batch:
            return (l_paging_information, p_result)
        
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

    def get_archive_listing(self, p_objects):
        """ """
        results = []
        select_all, delete_all, flag = 0, 0, 0
        for x in p_objects:
            del_permission = x.checkPermissionDeleteObject()
            edit_permission = x.checkPermissionEditObject()
            if del_permission and flag == 0:
                select_all, delete_all, flag = 1, 1, 1
            if edit_permission and flag == 0:
                flag, select_all = 1, 1
            if ((del_permission or edit_permission) and not x.approved) or x.approved:
                results.append((del_permission, edit_permission, x))
        return (select_all, delete_all, results)

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
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)
        
        lang = kwargs.setdefault('lang', self.gl_get_selected_language())
        releasedate = kwargs.get('releasedate', '')
        kwargs['releasedate'] = self.process_releasedate(releasedate)
        
        max_photos = kwargs.setdefault('max_photos', 100)
        try:
            max_photos = int(max_photos)
        except (ValueError, TypeError):
            max_photos = 100
        kwargs['max_photos'] = max_photos
        
        photos_per_page = kwargs.setdefault('photos_per_page', 50)
        try:
            photos_per_page = int(photos_per_page)
        except (ValueError, TypeError):
            photos_per_page = 50
        kwargs['photos_per_page'] = photos_per_page
        
        self.save_properties(**kwargs)
        self.recatalogNyObject(self)
        
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    def downloadAllObjects(self, REQUEST=None):
        #Download all pictures in a zip file.
        return self.utGenerateZip(
            name=self.id + '.zip',
            objects=self.getPublishedObjects(),
            RESPONSE=REQUEST.RESPONSE
        )
    
    def downloadSelectedObjects(self, ids=None, REQUEST=None):
        # Download photos from ids
        return self.utGenerateZip(
            name=self.id + '.zip',
            objects=map(self._getOb, self.utConvertToList(ids)),
            RESPONSE=REQUEST.RESPONSE
        )

    security.declareProtected(view, 'downloadObjects')
    def downloadObjects(self, ids=(), download="all", REQUEST=None, **kwargs):
        """
        Download pictures.
        """
        if download == 'all':
            return self.downloadAllObjects(REQUEST)
        return self.downloadSelectedObjects(ids, REQUEST)

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
                return REQUEST.RESPONSE.redirect(self.absolute_url())
        return err
    
    def is_full(self):
        if len(self.objectIds([METATYPE_NYPHOTO])) >= self.max_photos:
            return True
        return False

    security.declareProtected(PERMISSION_ADD_PHOTO, 'uploadPhotoOrZip')
    def uploadPhotoOrZip(self, upload_file=None, REQUEST=None, **kwargs):
        """ Upload one image or a zipped folder of images
        """
        # File not empty
        filename = getattr(upload_file, 'filename', None)
        if not filename:
            err = 'Please select a valid zip or image to upload'
        else:
            # Try to upload from zip
            err = self.uploadZip(upload_file)
            if err:
                # Add image
                zLOG.LOG('NyPhotoFolder', zLOG.DEBUG, err)
                upload_file.seek(0)
                is_image = self.isValidImage(upload_file.read())
                if not is_image:
                    err = 'Please select a valid zip or image to upload'
                else:
                    upload_file.seek(0)
                    self.addNyPhoto(title=filename, file=upload_file,
                                    lang=self.gl_get_selected_language())
                    err = ''
 
        # Return
        if self.is_full():
            err = "You've reached the maximum number of photos allowed in this album !"
        if not REQUEST:
            return err
        # Handle errors
        if err:
            self.setSessionErrors([err])
        else:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
        # Redirect
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'setSortOrder')
    def setSortOrder(self, REQUEST=None, **kwargs):
        """ Update objects order
        """
        if REQUEST:
            kwargs.update(REQUEST.form)
        for key, value in kwargs.items():
            if key not in self.getObjectIds():
                continue
            photo = self._getOb(key)
            try:
                value = int(value)
            except (ValueError, TypeError):
                continue
            else:
                photo._setPropValue('sortorder', value)
        if REQUEST:
            self.setSessionInfo(['Sort order updated on %s' % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/sortorder_html' % self.absolute_url())
        return True

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'changeCover')
    def changeCover(self, cover='', REQUEST=None, **kwargs):
        """ Update album cover
        """
        # Update cover image property

        # Handle invalid cover id
        err = ''
        if cover and cover not in self.objectIds(METATYPE_NYPHOTO):
            err = 'Invalid cover id %s' % cover
            cover = ''
        
        self.cover = cover
        
        if not REQUEST:
            return err

        if err:
            self.setSessionErrors([err])
            return REQUEST.RESPONSE.redirect('%s/changecover_html' % self.absolute_url())

        self.setSessionInfo(['Album cover updated on %s' % self.utGetTodayDate()])
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def isValidImage(self, file):
        """
        Test if the specified uploaded B{file} is a valid image.
        """
        try:
            Image.open(StringIO(file))
        except: # Python Imaging Library doesn't recognize it as an image
            return 0
        else:
            return 1

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
        if REQUEST: REQUEST.RESPONSE.redirect(self.absolute_url())

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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'restrict_html')
    def restrict_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_restrict')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'setRestrictions')
    def setRestrictions(self, access='all', roles=[], REQUEST=None):
        """
        Restrict access to current folder for given roles.
        """
        msg = err = ''
        if access == 'all':
            #remove restrictions
            try:
                self.manage_permission(view, roles=[], acquire=1)
            except Exception, error:
                err = error
            else:
                msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        else:
            #restrict for given roles
            try:
                roles = self.utConvertToList(roles)
                roles.extend(['Manager', 'Administrator'])
                self.manage_permission(view, roles=roles, acquire=0)
            except Exception, error:
                err = error
            else:
                msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '': self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/restrict_html' % self.absolute_url())

    #zmi pages
    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteObjects')
    security.declareProtected(PERMISSION_COPY_OBJECTS, 'copyObjects')
    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'cutObjects')
    security.declareProtected(view, 'pasteObjects')
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'updateSessionFrom')
    
    security.declareProtected(view_management_screens, 'manage_displays_html')
    manage_displays_html = PageTemplateFile('zpt/photofolder_manage_displays', globals())

    #site pages
    security.declareProtected(PERMISSION_ADD_PHOTOFOLDER, 'photofolder_add_html')
    photofolder_add_html = PageTemplateFile('zpt/photofolder_add', globals())
    
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/photofolder_index', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/photofolder_edit', globals())
    
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'sortorder_html')
    sortorder_html = PageTemplateFile('zpt/photoarchive_sortorder', globals())
    
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'changecover_html')
    changecover_html = PageTemplateFile('zpt/photoarchive_cover', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'basketofapprovals_html')
    basketofapprovals_html = PageTemplateFile('zpt/photofolder_basketofapprovals', globals())

    security.declareProtected(PERMISSION_ADD_PHOTO, 'photo_add_html')
    photo_add_html = PageTemplateFile('zpt/photo_add', globals())

InitializeClass(NyPhotoFolder)
