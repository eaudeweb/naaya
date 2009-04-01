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

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Localizer.LocalPropertyManager import LocalProperty
from AccessControl.Permissions import view_management_screens, view

# Naaya imports
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyContainer import NyContainer

# Self imports
from constants import *
from Products.NaayaBase.constants import *
from NyPhotoFolder import manage_addNyPhotoFolder as m_addNyPhotoFolder
from photo_archive import photo_archive

def manage_addNyPhotoGallery(self, id='', title='Photo Gallery', description='',
                             coverage='', keywords='', sortorder=100, releasedate='',
                            lang=None, discussion=0, REQUEST=None, **kwargs):
    """
    Create a Photo Gallery.
    """
    gallery_id = self.utCleanupId(id) or self.utGenObjectId(title)
    if not gallery_id:
        gallery_id = PREFIX_NYPHOTOGALLERY + self.utGenRandomId(6)

    releasedate = self.process_releasedate()
    lang = lang or self.gl_get_selected_language()
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None

    ob = NyPhotoGallery(gallery_id, title, lang,
                        description=description, coverage=coverage,
                        keywords=keywords, sortorder=sortorder,
                        releasedate=releasedate, discussion=discussion,
                        approved=approved, approved_by=approved_by)
    self.gl_add_languages(ob)
    self._setObject(gallery_id, ob)
    ob = self._getOb(gallery_id)

    ob.submitThis()
    self.recatalogNyObject(ob)

    #redirect if case
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url())
    return ob.getId()

class NyPhotoGallery(NyAttributes, photo_archive, NyContainer):
    """ """

    meta_type = METATYPE_NYPHOTOGALLERY
    meta_label = METALABEL_NYPHOTOGALLERY
    icon = 'misc_/NaayaPhotoArchive/NyPhotoGallery.gif'
    icon_marked = 'misc_/NaayaPhotoArchive/NyPhotoGallery.gif'

    manage_options = NyContainer.manage_options

    all_meta_types = (
        {'name': METATYPE_NYPHOTOFOLDER, 'action': 'photofolder_add_html'},
    )

    security = ClassSecurityInfo()
    title = LocalProperty('title')

    def __init__(self, id, title, lang, approved=0, approved_by='', **kwargs):
        self.id = id
        self.approved = approved
        self.approved_by = approved_by
        NyContainer.__init__(self)
        self.save_properties(title, lang, **kwargs)

    def getObjectsForValidation(self): return [x for x in self.objectValues(self.get_pluggable_metatypes_validation()) if x.submitted==1]
    def count_notok_objects(self): return len([x for x in self.getObjectsForValidation() if x.validation_status==-1 and x.submitted==1])
    def count_notchecked_objects(self): return len([x for x in self.getObjectsForValidation() if x.validation_status==0 and x.submitted==1])

    def save_properties(self, title='', lang=None, description='', coverage='',
                        keywords='', sortorder=100, releasedate='',
                        discussion=0, **kwargs):
        if not lang:
            lang = self.gl_get_selected_language()

        if sortorder:
            try: sortorder = abs(int(sortorder))
            except: sortorder = DEFAULT_SORTORDER

        photo_archive.save_properties(self, title, description, coverage,
                                      keywords, sortorder, releasedate, lang)

        if discussion:
            self.open_for_comments()
        else:
            self.close_for_comments()
        self._p_changed = 1

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)

        lang = kwargs.setdefault('lang', self.gl_get_selected_language())
        releasedate = kwargs.get('releasedate', '')
        kwargs['releasedate'] = self.process_releasedate(releasedate)
        self.save_properties(**kwargs)
        self.recatalogNyObject(self)\

        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

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
            self.setSessionInfo(['Sort order updated on %s' % self.utGetTodayDate()])
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

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'gallery_add_html')
    gallery_add_html = PageTemplateFile('zpt/photogallery_add', globals())

    security.declareProtected(PERMISSION_ADD_PHOTOFOLDER, 'photofolder_add_html')
    photofolder_add_html = PageTemplateFile('zpt/photofolder_add', globals())

InitializeClass(NyPhotoGallery)
