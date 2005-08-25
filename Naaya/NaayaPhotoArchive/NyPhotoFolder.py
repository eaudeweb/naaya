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
from Products.NaayaCore.managers.utils import batch_utils
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from Products.Localizer.LanguageManager import LanguageManager
import NyPhoto

manage_addNyPhotoFolder_html = PageTemplateFile('zpt/photofolder_manage_add', globals())
def manage_addNyPhotoFolder(self, id='', title='', quality='', lang=None, REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_NYPHOTOFOLDER + self.utGenRandomId(6)
    try: quality = abs(int(quality))
    except: quality = DEFAULT_QUALITY
    if quality <= 0 or quality > 100: quality = DEFAULT_QUALITY
    if lang is None: lang = self.gl_get_selected_language()
    ob = NyPhotoFolder(id, title, quality, lang)
    self.gl_add_languages(ob)
    self._setObject(id, ob)
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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'addNyPhoto')
    addNyPhoto = NyPhoto.addNyPhoto

    title = LocalProperty('title')

    def __init__(self, id, title, quality, lang):
        """ """
        self.id = id
        self._setLocalPropValue('title', lang, title)
        self.quality = quality
        self.displays = DEFAULT_DISPLAYS.copy()

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self.getLocalProperty('title', lang)])

    #api
    def get_photofolder_object(self): return self
    def get_photofolder_path(self, p=0): return self.absolute_url(p)
    def getObjects(self): return self.objectValues(METATYPE_NYPHOTO)
    def getPendingObjects(self): return self.utFilterObjsListByAttr(self.getObjects(), 'approved', 0)
    def getPendingContent(self): return self.getPendingObjects()

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
            return (l_paging_information, p_result[l_paging_information[0]:l_paging_information[1]])
        else:
            return (l_paging_information, [])

    def query_photos(self, q='', f='', p_start=0):
        #query/filter photos
        lang = self.getLocalizer().get_selected_language()
        if q == '': q = None
        if f == '': f = None
        else: f = 1
        return self._page_result(self.query_objects_ex(meta_type=METATYPE_NYPHOTO, q=q, lang=lang, path=self.absolute_url(1), topitem=f, approved=1, sort_on='releasedate', sort_order='reverse'), p_start)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', quality='', REQUEST=None):
        """ """
        try: quality = abs(int(quality))
        except: quality = DEFAULT_QUALITY
        if quality <= 0 or quality > 100: quality = DEFAULT_QUALITY
        lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self.quality = quality
        self._p_changed = 1
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
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', quality='', lang=None, REQUEST=None):
        """ """
        try: quality = abs(int(quality))
        except: quality = DEFAULT_QUALITY
        if quality <= 0 or quality > 100: quality = DEFAULT_QUALITY
        if lang is None: lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self.quality = quality
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'deleteObjects')
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
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'updateBasketOfApprovals')
    def updateBasketOfApprovals(self, REQUEST=None):
        """ """
        for id in self.utConvertToList(REQUEST.get('app', [])):
            try:
                ob = self._getOb(id)
                ob.approveThis()
                self.recatalogNyObject(ob)
            except:
                pass
        for id in self.utConvertToList(REQUEST.get('del', [])):
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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/photofolder_edit', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'basketofapprovals_html')
    basketofapprovals_html = PageTemplateFile('zpt/photofolder_basketofapprovals', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'photo_add_html')
    photo_add_html = PageTemplateFile('zpt/photo_add', globals())

InitializeClass(NyPhotoFolder)
