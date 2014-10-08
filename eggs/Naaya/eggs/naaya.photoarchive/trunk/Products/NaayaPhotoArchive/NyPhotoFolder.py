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
# David Batranu, Eau de Web

#Python imports
from string import rfind
try:
    from PIL import Image
except ImportError:
    # PIL installed as an egg
    import Image

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Globals import InitializeClass
from NyPhoto import json_encode
from Products.Naaya.constants import DEFAULT_SORTORDER
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyContentType import NyContentType, NyContentData, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyRoleManager import NyRoleManager
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from Products.NaayaBase.constants import PERMISSION_COPY_OBJECTS
from Products.NaayaBase.constants import PERMISSION_DELETE_OBJECTS
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaBase.constants import PERMISSION_ZIP_EXPORT
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.NaayaCore.managers.utils import batch_utils, ZZipFile, make_id
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from cStringIO import StringIO
from constants import DEFAULT_DISPLAYS
from constants import DEFAULT_QUALITY
from constants import METALABEL_NYPHOTOFOLDER
from constants import METATYPE_NYPHOTO
from constants import METATYPE_NYPHOTOFOLDER
from constants import METATYPE_NYPHOTOGALLERY
from constants import NUMBER_OF_RESULTS_PER_LINE
from constants import NUMBER_OF_RESULTS_PER_PAGE
from constants import PREFIX_NYPHOTOFOLDER
from permissions import PERMISSION_ADD_PHOTO
from photo_archive import photo_archive_base
from zope.deprecation import deprecate
import NyPhoto
import simplejson as json
import zLOG

DEFAULT_SCHEMA = {}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

DEFAULT_SCHEMA.update({
    'author':           dict(sortorder=100, widget_type='String', label='Author', localized=True),
    'source':           dict(sortorder=110, widget_type='String', label='Source', localized=True),
    'max_photos':       dict(sortorder=120, widget_type='String', data_type='int', default='100', label='Maximum number of photos in album'),
    'photos_per_page':  dict(sortorder=130, widget_type='String', data_type='int', default='50', label='Maximum number of photos per page'),
    'restrict_original':dict(sortorder=140, widget_type='Checkbox', data_type='bool',
                            label='Restrict original images'),
    'watermark_text':   dict(sortorder=150, widget_type='String', label='Watermark images with following text'),
    'geo_location':     dict(sortorder=160, widget_type='Geo', data_type='geo', label='Geographic location', visible=True),
})

_photofolder_add_html = PageTemplateFile('zpt/photofolder_add', globals())
def photofolder_add_html(self, REQUEST):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_NYPHOTOFOLDER)
    return _photofolder_add_html.__of__(self)(REQUEST, form_helper=form_helper)


def addNyPhotoFolder(self, id='', REQUEST=None, contributor=None,
        _klass=None, **kwargs):
    """
    Create a PhotoFolder type of object.
    """
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    if _klass is None:
        _klass = NyPhotoFolder
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))
    _cover = schema_raw_data.pop('cover', '')
    _file = schema_raw_data.pop('file', None)

    folder_id = make_id(self, id=id, title=schema_raw_data['title'], prefix=PREFIX_NYPHOTOFOLDER)
    if contributor is None:
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _klass(folder_id, contributor)
    self.gl_add_languages(ob)
    self._setObject(folder_id, ob)

    ob = self._getOb(folder_id)
    if getattr(_file, 'filename', None):
        kwargs_ = {}
        for k, v in schema_raw_data.iteritems():
            if k in ob.inherit_fields:
                kwargs_[k] = v
            elif '.' in k and k.split('.')[0] in ob.inherit_fields:
                kwargs_[k] = v
        ob.uploadPhotoOrZip(_file, **kwargs_)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/photofolder_add_html' % self.absolute_url())
            return

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 1, None
    ob._setPropValue('cover', _cover)

    ob.approveThis(approved, approved_by)
    ob.submitThis()
    if ob.discussion:
        ob.open_for_comments()
    else:
        ob.close_for_comments()
    self.recatalogNyObject(ob)

    #redirect if case
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url())
    return ob.getId()

class NyPhotoFolder(NyRoleManager, NyContentData, NyAttributes, photo_archive_base, NyContainer, NyContentType):
    """ """

    meta_type = METATYPE_NYPHOTOFOLDER
    meta_label = METALABEL_NYPHOTOFOLDER
    icon = '++resource++naaya.photoarchive/NyPhotoFolder.gif'
    icon_marked = '++resource++naaya.photoarchive/NyPhotoFolder_marked.gif'

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
        {
            'name': METATYPE_NYPHOTO,
            'action': 'photo_add_html',
            'permission': PERMISSION_ADD_PHOTO,
        },
    )
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    security.declareProtected(PERMISSION_ADD_PHOTO, 'addNyPhoto')
    addNyPhoto = NyPhoto.addNyPhoto

    cover = ''
    max_photos = 100
    photos_per_page = 50
    inherit_fields = set(['author', 'source', 'geo_location'])

    restrict_original = False
    watermark_text = ''

    def __init__(self, id, contributor):
        self.id = id
        self.contributor = contributor
        self.displays = DEFAULT_DISPLAYS.copy()
        NyContainer.__init__(self)
        NyContentData.__init__(self)


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
                approved, approved_by = 1, None
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
    @deprecate('NyPhotoFolder.get_photofolder_object is deprecated and will be removed in the next version.')
    def get_photofolder_object(self):
        return self

    @deprecate('NyPhotoFolder.get_photofolder_path is deprecated and will be removed in the next version.')
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

    @deprecate('NyPhotoFolder.count_notok_objects is deprecated and will be removed in the next version.')
    def count_notok_objects(self):
        return 0

    @deprecate('NyPhotoFolder.count_notchecked_objects is deprecated and will be removed in the next version.')
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

    @deprecate('NyPhotoFolder.get_displays_edit is deprecated and will be removed in the next version.')
    def get_displays_edit(self):
        #returns a list with all dispays minus 'Thumbnail'
        l = self.displays.keys()
        l.sort(lambda x,y,d=self.displays: cmp(d[x][0]*d[x][1], d[y][0]*d[y][1]))
        return l

    @deprecate('NyPhotoFolder.process_querystring is deprecated and will be removed in the next version.')
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

    @deprecate('NyPhotoFolder._page_result is deprecated and will be removed in the next version.')
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

    @deprecate('NyPhotoFolder.query_photos is deprecated and will be removed in the next version.')
    def query_photos(self, q='', f='', p_start=0):
        #query/filter photos
        lang = self.gl_get_selected_language()
        if q == '': q = None
        if f == '': f = None
        else: f = 1
        return self._page_result(self.query_objects_ex(meta_type=METATYPE_NYPHOTO, q=q, lang=lang, path='/'.join(self.getPhysicalPath()), topitem=f, approved=1, sort_on='releasedate', sort_order='reverse'), p_start)

    @deprecate('NyPhotoFolder.get_archive_listing is deprecated and will be removed in the next version.')
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

    @deprecate('NyPhotoFolder._page_result_admin is deprecated and will be removed in the next version.')
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

    @deprecate('NyPhotoFolder.query_photos_admin is deprecated and will be removed in the next version.')
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
        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs

        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _cover = schema_raw_data.pop('cover', '')

        initial_watermark = self.watermark_text
        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

        if self.discussion:
            self.open_for_comments()
        else:
            self.close_for_comments()
        if initial_watermark != self.watermark_text:
            for photo in self.objectValues():
                photo._delete_watermarked_photos()
        self._setPropValue('cover', _cover)

        self._p_changed = 1

        self.saveProperties_hook(schema_raw_data)

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    security.declarePrivate('saveProperties_hook')
    def saveProperties_hook(self, schema_raw_data):
        pass

    security.declareProtected(PERMISSION_ZIP_EXPORT, 'downloadAllObjects')
    def downloadAllObjects(self, REQUEST=None):
        #Download all pictures in a zip file.
        return self.utGenerateZip(
            name=self.id + '.zip',
            objects=self.getPublishedObjects(),
            RESPONSE=REQUEST.RESPONSE
        )

    security.declareProtected(PERMISSION_ZIP_EXPORT, 'downloadSelectedObjects')
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

    def _add_photo(self, *args, **kwargs):
        self.addNyPhoto(*args, **kwargs)

    security.declareProtected(PERMISSION_ADD_PHOTO, 'uploadZip')
    def uploadZip(self, file='', REQUEST=None, **kwargs):
        """
        Expand a zipfile into a number of Photos.
        Go through the zipfile and for each file create a I{Naaya Photo} object.
        """
        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs

        err = ''
        title = None
        if 'title' in schema_raw_data.keys():
            title = schema_raw_data.get('title')
            del schema_raw_data['title']
        try:
            if type(file) is not type('') and hasattr(file,'filename'):
                # According to the zipfile.py ZipFile just needs a file-like object
                zf = ZZipFile(file)
                for name in zf.namelist():
                    zf.setcurrentfile(name)
                    content = zf.read()
                    if self.isValidImage(content):
                        id = name[max(rfind(name,'/'), rfind(name,'\\'), rfind(name,':'))+1:]
                        if title:
                            photo_title = title
                        else:
                            photo_title = name
                        self._add_photo(id=id, title=photo_title, file=content,
                            lang=self.gl_get_selected_language(), **schema_raw_data)
            else:
                err = 'Invalid zip file.'
        except Exception, error:
            err = str(error)
        if REQUEST:
            if err != '':
                self.setSessionErrorsTrans([err])
                return REQUEST.RESPONSE.redirect('%s/uploadzip_html' % self.absolute_url())
            else:
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
                return REQUEST.RESPONSE.redirect(self.absolute_url())
        return err

    def is_full(self):
        if len(self.objectIds()) >= self.max_photos:
            return True
        return False

    security.declareProtected(PERMISSION_ADD_PHOTO, 'uploadPhotoOrZip')
    def uploadPhotoOrZip(self, upload_file=None, REQUEST=None, **kwargs):
        """ Upload one image or a zipped folder of images
        """
        schema_raw_data = kwargs
        if REQUEST is not None:
            schema_raw_data.update(REQUEST.form)

        # File not empty
        filename = getattr(upload_file, 'filename', None)
        if not filename:
            err = 'Please select a valid zip or image to upload'
        else:
            # Try to upload from zip
            err = self.uploadZip(upload_file, **schema_raw_data)
            if err:
                # Add image
                zLOG.LOG('NyPhotoFolder', zLOG.DEBUG, err)
                upload_file.seek(0)
                the_file = upload_file.read()
                is_image = self.isValidImage(the_file)
                if not is_image:
                    err = 'Please select a valid zip or image to upload'
                else:
                    if not schema_raw_data.get('title', None):
                        schema_raw_data['title'] = filename

                    self._add_photo(id=filename, file=the_file,
                                    lang=self.gl_get_selected_language(),
                                    **schema_raw_data)
                    err = ''

        # Return
        if self.is_full():
            err = "You've reached the maximum number of photos allowed in this album !"
        if not REQUEST:
            return err
        # Handle errors
        if err:
            self.setSessionErrorsTrans([err])
        else:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
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
            self.setSessionInfoTrans('Sort order updated on ${date}', date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/sortorder_html' % self.absolute_url())
        return True

    def _list_photos(self):
        return self.objectIds(METATYPE_NYPHOTO)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'changeCover')
    def changeCover(self, cover='', REQUEST=None, **kwargs):
        """ Update album cover
        """
        # Update cover image property

        # Handle invalid cover id
        err = ''
        if cover and cover not in self._list_photos():
            err = 'Invalid cover id %s' % cover
            cover = ''

        self.cover = cover

        if not REQUEST:
            return err

        if err:
            self.setSessionErrorsTrans([err])
            return REQUEST.RESPONSE.redirect('%s/changecover_html' % self.absolute_url())

        self.setSessionInfoTrans('Album cover updated on ${date}', date=self.utGetTodayDate())
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
    @deprecate('NyPhotoFolder.setTopPhotoObjects is deprecated and will be removed in the next version.')
    def setTopPhotoObjects(self, REQUEST=None):
        """ """
        try:
            for item in self.objectValues():
                if hasattr(item, 'topitem'): item.topitem = 0
                if REQUEST.has_key('topitem_' + item.id):
                    item.topitem = 1
                item._p_changed = 1
                self.recatalogNyObject(item)
        except: self.setSessionErrorsTrans('Error while updating data.')
        else: self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
        if REQUEST: REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processPendingContent')
    @deprecate('NyPhotoFolder.processPendingContent is deprecated and will be removed in the next version.')
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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/basketofapprovals_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processPublishedContent')
    @deprecate('NyPhotoFolder.processPublishedContent is deprecated and will be removed in the next version.')
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
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/basketofapprovals_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'restrict_html')
    #@deprecate('NyPhotoFolder.restrict_html is deprecated and will be removed in the next version.')
    def restrict_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_restrict')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'setRestrictions')
    #@deprecate('NyPhotoFolder.setRestrictions is deprecated and will be removed in the next version.')
    def setRestrictions(self, access='all', roles=[], REQUEST=None):
        """
        Restrict access to current folder for given roles.
        """
        err = ''
        success = False
        if access == 'all':
            #remove restrictions
            try:
                self.manage_permission(view, roles=[], acquire=1)
            except Exception, error:
                err = error
            else:
                success = True
        else:
            #restrict for given roles
            try:
                roles = self.utConvertToList(roles)
                roles.extend(['Manager', 'Administrator'])
                self.manage_permission(view, roles=roles, acquire=0)
            except Exception, error:
                err = error
            else:
                success = True
        if REQUEST:
            if err != '': self.setSessionErrorsTrans([err])
            if success: self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/restrict_html' % self.absolute_url())

    photo_metatype = METATYPE_NYPHOTO
    parent_metatype = METATYPE_NYPHOTOGALLERY
    security.declareProtected(PERMISSION_ADD_PHOTO, 'upload_html')
    _upload_html = PageTemplateFile('zpt/photofolder_upload', globals())
    _upload_html.cc_license_template = PageTemplateFile('zpt/cc_license', globals())
    def upload_html(self, REQUEST):
        """ Upload form for photo or zip file """
        from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
        def value_callback(prop_name):
            if prop_name in self.inherit_fields:
                return getattr(self, prop_name)
        form_helper = get_schema_helper_for_metatype(self, self.photo_metatype, value_callback)
        def fields_filter(item):
            return item['name'] in self.inherit_fields.union(['title'])
        form_items = list(filter(fields_filter, form_helper.form_items()))
        return self._upload_html(REQUEST, form_items=form_items)

    #zmi pages
    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteObjects')
    security.declareProtected(PERMISSION_COPY_OBJECTS, 'copyObjects')
    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'cutObjects')
    security.declareProtected(view, 'pasteObjects')
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'updateSessionFrom')

    security.declareProtected(view_management_screens, 'manage_displays_html')
    manage_displays_html = PageTemplateFile('zpt/photofolder_manage_displays', globals())

    #macros
    security.declareProtected(view, 'images_macro')
    images_macro = PageTemplateFile('zpt/photofolder_images', globals())

    #site pages
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
    photo_add_html = NyPhoto.photo_add_html

    _minimap_template = PageTemplateFile('zpt/minimap', globals())
    def minimap(self):
        if self.geo_location not in (Geo(), None):
            simplepoints = [{'lat': self.geo_location.lat, 'lon': self.geo_location.lon}]
            json_simplepoints = json.dumps(simplepoints, default=json_encode)
            return self._minimap_template(points=json_simplepoints)
        simplepoints = [{'lat': photo.geo_location.lat, 'lon': photo.geo_location.lon}\
                        for photo in self.objectValues("Naaya Photo") if photo.geo_location is not None]
        if simplepoints != []:
            json_simplepoints = json.dumps(simplepoints, default=json_encode)
            return self._minimap_template(points=json_simplepoints)
        else:
            return ""

    def parent_is_gallery(self):
        return self.getParentNode().meta_type == self.parent_metatype

InitializeClass(NyPhotoFolder)
