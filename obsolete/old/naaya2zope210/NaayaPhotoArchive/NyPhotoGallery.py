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

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens, view

# Naaya imports
from Products.NaayaBase.NyContentType import NyContentType, NyContentData, NY_CONTENT_BASE_SCHEMA
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaCore.managers.utils import make_id
from Products.NaayaBase.NyRoleManager import NyRoleManager

# Self imports
from constants import *
from Products.NaayaBase.constants import *
from NyPhotoFolder import manage_addNyPhotoFolder as m_addNyPhotoFolder
from NyPhotoFolder import photofolder_add_html
from photo_archive import photo_archive_base


DEFAULT_SCHEMA = {
    # add NyPhotoGallery-specific properties here
    'restrict_original': dict(sortorder=100, widget_type='Checkbox', data_type='bool',
        label='Restrict original images'),
}
DEFAULT_SCHEMA.update(NY_CONTENT_BASE_SCHEMA)

_gallery_add_html = PageTemplateFile('zpt/photogallery_add', globals())
def gallery_add_html(self, REQUEST):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_NYPHOTOGALLERY)
    return _gallery_add_html.__of__(self)(REQUEST, form_helper=form_helper)

def manage_addNyPhotoGallery(self, id='', REQUEST=None, contributor=None,
        _klass=None, **kwargs):
    """
    Create a Photo Gallery.
    """

    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs

    if _klass is None:
        _klass = NyPhotoGallery
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    gallery_id = make_id(self, id=id, title=schema_raw_data['title'], prefix=PREFIX_NYPHOTOGALLERY)

    ob = _klass(gallery_id, contributor)
    self.gl_add_languages(ob)
    self._setObject(gallery_id, ob)
    ob = self._getOb(gallery_id)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/gallery_add_html' % self.absolute_url())
            return

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 1, None
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

class NyPhotoGallery(NyRoleManager, NyContentData, NyAttributes, photo_archive_base, NyContainer, NyContentType):
    """ """

    meta_type = METATYPE_NYPHOTOGALLERY
    meta_label = METALABEL_NYPHOTOGALLERY
    icon = 'misc_/NaayaPhotoArchive/NyPhotoGallery.gif'
    icon_marked = 'misc_/NaayaPhotoArchive/NyPhotoGallery.gif'

    manage_options = NyContainer.manage_options

    all_meta_types = (
        {
            'name': METATYPE_NYPHOTOFOLDER,
            'action': 'photofolder_add_html',
            'permission': PERMISSION_ADD_PHOTOFOLDER,
        },
    )

    security = ClassSecurityInfo()

    restrict_original = False

    def __init__(self, id, contributor):
        self.id = id
        #self.approved = approved
        #self.approved_by = approved_by
        NyContainer.__init__(self)
        NyContentData.__init__(self)
        #self.save_properties(title, lang, **kwargs)
        self.contributor = contributor

    def getObjectsForValidation(self): return [x for x in self.objectValues(self.get_pluggable_metatypes_validation()) if x.submitted==1]
    def count_notok_objects(self): return len([x for x in self.getObjectsForValidation() if x.validation_status==-1 and x.submitted==1])
    def count_notchecked_objects(self): return len([x for x in self.getObjectsForValidation() if x.validation_status==0 and x.submitted==1])

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs

        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)

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
        self._p_changed = 1

        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    security.declareProtected(view, 'getObjects')
    def getObjects(self):
        # Returns albums
        return [x for x in self.objectValues(METATYPE_NYPHOTOFOLDER) if x.checkPermissionView()]

    def getPublishedObjects(self):
        return []

    def getPublishedFolders(self):
        return self.getObjects()

    def getSortedObjects(self):
        return self.sort_objects(self.getObjects())

    def sort_objects(self, sort_list=(), sort_by='sortorder', reverse=0):
        """ Sort a list of objects by given sort_by attr
        """
        return self.utSortObjsListByAttr(sort_list, sort_by, reverse)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'setSortOrder')
    def setSortOrder(self, REQUEST=None, **kwargs):
        """ Update objects order
        """
        if REQUEST:
            kwargs.update(REQUEST.form)
        for key, value in kwargs.items():
            if key not in self.objectIds(METATYPE_NYPHOTOFOLDER):
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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'restrict_html')
    def restrict_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_restrict')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'setRestrictions')
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

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteObjects')
    security.declareProtected(PERMISSION_COPY_OBJECTS, 'copyObjects')
    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'cutObjects')
    security.declareProtected(view, 'pasteObjects')
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'updateSessionFrom')

    security.declareProtected(PERMISSION_ADD_PHOTOFOLDER, 'manage_addNyPhotoFolder')
    manage_addNyPhotoFolder = m_addNyPhotoFolder

    security.declareProtected(PERMISSION_ADD_PHOTOFOLDER, 'addNyPhotoFolder')
    addNyPhotoFolder = m_addNyPhotoFolder

    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/photogallery_index', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/photogallery_edit', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'sortorder_html')
    sortorder_html = PageTemplateFile('zpt/photoarchive_sortorder', globals())

    security.declareProtected(PERMISSION_ADD_PHOTOFOLDER, 'photofolder_add_html')
    photofolder_add_html = photofolder_add_html

InitializeClass(NyPhotoGallery)
