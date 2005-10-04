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
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from copy import copy

#Zope imports
from DateTime import DateTime
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
import Products

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyImportExport import NyImportExport
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyProperties import NyProperties
from Products.Localizer.LocalPropertyManager import LocalProperty

manage_addNyFolder_html = PageTemplateFile('zpt/folder_manage_add', globals())
manage_addNyFolder_html.kind = METATYPE_FOLDER
manage_addNyFolder_html.action = 'addNyFolder'

def folder_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_FOLDER, 'action': 'addNyFolder'}, 'folder_add')

def addNyFolder(self, id='', title='', description='', coverage='', keywords='', sortorder='',
    publicinterface='', maintainer_email='', folder_meta_types='', contributor=None,
    releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a Folder type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = PREFIX_FOLDER + self.utGenRandomId(6)
    if publicinterface: publicinterface = 1
    else: publicinterface = 0
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
    if self.checkPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    releasedate = self.process_releasedate(releasedate)
    if folder_meta_types == '': folder_meta_types = self.adt_meta_types
    else: folder_meta_types = self.utConvertToList(folder_meta_types)
    if lang is None: lang = self.gl_get_selected_language()
    #create object
    ob = NyFolder(id, title, description, coverage, keywords, sortorder, publicinterface,
            maintainer_email, contributor, approved, approved_by, folder_meta_types,
            releasedate, lang)
    self.gl_add_languages(ob)
    ob.createDynamicProperties(self.processDynamicProperties(METATYPE_FOLDER, REQUEST, kwargs), lang)
    self._setObject(id, ob)
    #extra settings
    ob = self._getOb(id)
    ob.submitThis()
    ob.createPublicInterface()
    if discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    self.notifyFolderMaintainer(self, ob)
    #redirect if case
    if REQUEST is not None:
        referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if referer == 'folder_manage_add' or referer.find('folder_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif referer == 'folder_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/note_html' % self.getSitePath())

def importNyFolder(self, param, id, attrs, content, properties, discussion, objects):
    #this method is called during the import process
    try: param = abs(int(param))
    except: param = 0
    if param in [0, 1]:
        if param == 1:
            #delete the object if exists
            try: self.manage_delObjects([id])
            except: pass
        publicinterface = abs(int(attrs['publicinterface'].encode('utf-8')))
        meta_types = attrs['folder_meta_types'].encode('utf-8')
        if meta_types == '': meta_types = ''
        else: meta_types = meta_types.split(',')
        #create the object
        addNyFolder(self, id=id,
            sortorder=attrs['sortorder'].encode('utf-8'),
            publicinterface=publicinterface,
            maintainer_email=attrs['maintainer_email'].encode('utf-8'),
            folder_meta_types=meta_types,
            contributor=attrs['contributor'].encode('utf-8'),
            discussion=abs(int(attrs['discussion'].encode('utf-8'))))
        ob = self._getOb(id)
        for property, langs in properties.items():
            for lang in langs:
                ob._setLocalPropValue(property, lang, langs[lang])
        ob.approveThis(abs(int(attrs['approved'].encode('utf-8'))))
        ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
        if publicinterface:
            l_index = ob._getOb('index', None)
            if l_index is not None:
                l_index.pt_edit(text=content, content_type='')
        ob.import_comments(discussion)
        self.recatalogNyObject(ob)
    else:
        ob = self._getOb(id)
    #go on and import sub objects
    for object in objects:
        ob.import_data(object)

class NyFolder(NyAttributes, NyProperties, NyImportExport, NyContainer, utils):
    """ """

    meta_type = METATYPE_FOLDER
    icon = 'misc_/Naaya/NyFolder.gif'
    icon_marked = 'misc_/Naaya/NyFolder_marked.gif'

    manage_options = (
        NyContainer.manage_options[0:2]
        +
        (
            {'label': 'Properties', 'action': 'manage_edit_html'},
            {'label': 'Subobjects', 'action': 'manage_folder_subobjects_html'},
        )
        +
        NyProperties.manage_options
        +
        NyImportExport.manage_options
        +
        NyContainer.manage_options[3:8]
    )

    security = ClassSecurityInfo()

    #constructors
    security.declareProtected(PERMISSION_ADD_FOLDER, 'folder_add_html')
    folder_add_html = folder_add_html
    security.declareProtected(PERMISSION_ADD_FOLDER, 'addNyFolder')
    addNyFolder = addNyFolder

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')

    def all_meta_types(self, interfaces=None):
        """ What can you put inside me? """
        if len(self.folder_meta_types) > 0:
            #filter meta types
            l = list(filter(lambda x: x['name'] in self.folder_meta_types, Products.meta_types))
            #handle uninstalled pluggable meta_types
            pluggable_meta_types = self.get_pluggable_metatypes()
            pluggable_installed_meta_types = self.get_pluggable_installed_meta_types()
            t = copy(l)
            for x in t:
                if (x['name'] in pluggable_meta_types) and (x['name'] not in pluggable_installed_meta_types):
                    l.remove(x)
            return l
        else:
            return self.meta_types

    def __init__(self, id, title, description, coverage, keywords, sortorder,
        publicinterface, maintainer_email, contributor, approved, approved_by,
        folder_meta_types, releasedate, lang):
        """ """
        self.id = id
        NyContainer.__dict__['__init__'](self)
        NyProperties.__dict__['__init__'](self)
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.publicinterface = publicinterface
        self.maintainer_email = maintainer_email
        self.sortorder = sortorder
        self.contributor = contributor
        self.approved = approved
        self.approved_by = approved_by
        self.releasedate = releasedate
        self.folder_meta_types = folder_meta_types

    #overwrite handler
    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        NyContainer.__dict__['manage_beforeDelete'](self, item, container)
        self.uncatalogNyObject(self)
        self.delete_portlet_for_object(item)

    #import/export
    def exportdata_custom(self):
        #exports all the Naaya content in XML format from this folder
        return self.export_this()

    security.declarePrivate('export_this')
    def export_this(self):
        r = []
        ra = r.append
        ra(self.export_this_tag())
        ra(self.export_this_body())
        if self.publicinterface:
            l_index = self._getOb('index', None)
            if l_index is not None:
                ra('<![CDATA[%s]]>' % l_index.document_src())
        for x in self.getObjects():
            ra(x.export_this())
        for x in self.getFolders():
            ra(x.export_this())
        ra('</ob>')
        return ''.join(r)

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'publicinterface="%s" maintainer_email="%s" folder_meta_types="%s"' % \
            (self.utXmlEncode(self.publicinterface),
                self.utXmlEncode(self.maintainer_email),
                self.utXmlEncode(','.join(self.folder_meta_types)))

    security.declarePrivate('createPublicInterface')
    def createPublicInterface(self):
        pt_id = 'index'
        if self.publicinterface and self._getOb(pt_id, None) is None:
            pt_content = self.getFormsTool()._getOb('folder_index').document_src()
            manage_addPageTemplate(self, id=pt_id, title='Custom index for this folder', text='')
            pt_obj = self._getOb(pt_id)
            pt_obj.pt_edit(text=pt_content, content_type='')

    security.declarePrivate('modifyPublicInterface')
    def modifyPublicInterface(self, pt_content):
        pt_id = 'index'
        if self.publicinterface and self._getOb(pt_id, None) is not None:
            try: self._getOb(pt_id).pt_edit(text=pt_content, content_type='')
            except: pass

    def import_data(self, object):
        #import an object
        if object.meta_type == METATYPE_FOLDER:
            importNyFolder(self, object.param, object.id, object.attrs,
                object.content, object.properties, object.discussion,
                object.objects)
        elif object.meta_type in self.get_pluggable_installed_meta_types():
            item = self.get_pluggable_item(object.meta_type)
            c = 'self.import%s(object.param, object.id, object.attrs, \
                object.content, object.properties, object.discussion, \
                object.objects)' % item['module']
            exec(c)
        else:
            self.import_data_custom(self, object)

    def process_submissions(self):
        #returns info regarding the meta_types that ce be added inside the folder
        r = []
        ra = r.append
        #check for adding folders
        if METATYPE_FOLDER in self.folder_meta_types:
            if self.checkPermission(PERMISSION_ADD_FOLDER):
                ra(('folder_add_html', LABEL_NYFOLDER))
        #check pluggable content
        pc = self.get_pluggable_content()
        for k in self.get_pluggable_installed_meta_types():
            if k in self.folder_meta_types:
                if self.checkPermission(pc[k]['permission']):
                    ra((pc[k]['addform'], pc[k]['label']))
        return r

    security.declareProtected(view, 'checkPermissionManageObects')
    def checkPermissionManageObjects(self, p_objects=None):
        """ The optional argument is the list of meta types to be looped by this function """
        if p_objects is None: l = self.getObjects()
        else: l = [x for x in p_objects if x.submitted==1]
        results = []
        select_all, delete_all, flag = 0, 0, 0
        for x in self.utSortObjsListByAttr(l, 'sortorder', 0):
            del_permission = x.checkPermissionDeleteObject()
            edit_permission = x.checkPermissionEditObject()
            if del_permission and flag == 0:
                select_all, delete_all, flag = 1, 1, 1
            if edit_permission and flag == 0:
                select_all, flag = 1, 1
            if ((del_permission or edit_permission) and not x.approved) or x.approved:
                results.append((del_permission, edit_permission, x))
        return (select_all, delete_all, results)

    security.declareProtected(view, 'checkPermissionManageFolders')
    def checkPermissionManageFolders(self, p_objects=None):
        """ The optional argument is the list of meta types to be looped by this function """
        if p_objects is None: l = self.getFolders()
        else: l = [x for x in p_objects if x.submitted==1]
        results = []
        select_all, delete_all, flag = 0, 0, 0
        for x in self.utSortObjsListByAttr(l, 'sortorder', 0):
            del_permission = x.checkPermissionDeleteObject()
            edit_permission = x.checkPermissionEditObject()
            if del_permission and flag == 0:
                select_all, delete_all, flag = 1, 1, 1
            if edit_permission and flag == 0:
                select_all, flag = 1, 1
            if ((del_permission or edit_permission) and not x.approved) or x.approved:
                results.append((del_permission, edit_permission, x))
        return (select_all, delete_all, results)

    def getObjects(self): return [x for x in self.objectValues(self.get_meta_types()) if x.submitted==1]
    def getFolders(self): return [x for x in self.objectValues(METATYPE_FOLDER) if x.submitted==1]
    def hasContent(self): return (len(self.getObjects()) > 0) or (len(self.objectValues(METATYPE_FOLDER)) > 0)

    def getPendingFolders(self): return [x for x in self.objectValues(METATYPE_FOLDER) if x.approved==0 and x.submitted==1]
    def getPublishedFolders(self): return self.utSortObjsListByAttr([x for x in self.objectValues(METATYPE_FOLDER) if x.approved==1 and x.submitted==1], 'sortorder', 0)
    def getPendingObjects(self): return [x for x in self.getObjects() if x.approved==0 and x.submitted==1]
    def getPublishedObjects(self): return [x for x in self.getObjects() if x.approved==1 and x.submitted==1]

    def hasPendingContent(self): return (len(self.getPendingFolders()) > 0) or (len(self.getPendingObjects()) > 0)
    def getPendingContent(self):
        l_result = self.getPendingFolders()
        l_result.extend(self.getPendingObjects())
        return l_result

    def getObjectsForValidation(self): return [x for x in self.objectValues(self.get_pluggable_metatypes_validation()) if x.submitted==1]
    def count_notok_objects(self): return len([x for x in self.getObjectsForValidation() if x.validation_status==-1 and x.submitted==1])
    def count_notchecked_objects(self): return len([x for x in self.getObjectsForValidation() if x.validation_status==0 and x.submitted==1])

    def getSortedFolders(self): return self.utSortObjsListByAttr(self.getFolders(), 'sortorder', 0)
    def getSortedObjects(self): return self.utSortObjsListByAttr(self.getObjects(), 'sortorder', 0)

    #restrictions
    def get_valid_roles(self):
        #returns a list of roles that can be used to restrict this folder
        roles = list(self.valid_roles())
        filter(roles.remove, ['Administrator', 'Anonymous', 'Manager', 'Owner'])
        return roles

    def is_for_all_users(self):
        #check if all users have access to this folder
        print self.rolesOfPermission(view)
        print self.permission_settings(view)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', language='', coverage='',
        keywords='', sortorder='', publicinterface='', maintainer_email='', approved='',
        releasedate='', discussion='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if publicinterface: publicinterface = 1
        else: publicinterface = 0
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.sortorder = sortorder
        self.publicinterface = publicinterface
        self.maintainer_email = maintainer_email
        self.approved = approved
        self.releasedate = releasedate
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_FOLDER, REQUEST, kwargs), lang)
        if approved != self.approved:
            self.approved = approved
            if approved == 0: self.approved_by = None
            else: self.approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        self.createPublicInterface()
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'manageSubobjects')
    def manageSubobjects(self, REQUEST=None):
        """ """
        if REQUEST.get('default', ''):
            self.folder_meta_types = self.adt_meta_types
        else:
            self.folder_meta_types = self.utConvertToList(REQUEST.get('subobjects', []))
            self.folder_meta_types.extend(self.utConvertToList(REQUEST.get('ny_subobjects', [])))
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_folder_subobjects_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', language='', coverage='',
        keywords='', sortorder='', maintainer_email='', releasedate='', discussion='',
        lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        if lang is None: lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.sortorder = sortorder
        self.maintainer_email = maintainer_email
        self.releasedate = releasedate
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_FOLDER, REQUEST, kwargs), lang)
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('edit_html?lang=%s' % lang)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'copyObjects')
    def copyObjects(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_copyObjects(id_list, REQUEST)
        except: self.setSessionErrors(['Error while copy data.'])
        else: self.setSessionInfo(['Item(s) copied.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'cutObjects')
    def cutObjects(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_cutObjects(id_list, REQUEST)
        except: self.setSessionErrors(['Error while cut data.'])
        else: self.setSessionInfo(['Item(s) cut.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(view, 'hasObjectsToPaste')
    def hasObjectsToPaste(self):
        """ """
        return self.cb_dataValid()

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'pasteObjects')
    def pasteObjects(self, REQUEST=None):
        """ """
        try: self.manage_pasteObjects(None, REQUEST)
        except: self.setSessionErrors(['Error while paste data.'])
        else: self.setSessionInfo(['Item(s) pasted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteObjects')
    def deleteObjects(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_delObjects(id_list)
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'setTopStoryObjects')
    def setTopStoryObjects(self, REQUEST=None):
        """ """
        #ids_list = self.utConvertToList(REQUEST.get('id_topstory', []))
        try:
            for item in self.objectValues():
                if hasattr(item, 'topitem'): item.topitem = 0
                if REQUEST.has_key('topstory_' + item.id):
                    item.topitem = 1
                item._p_changed = 1
                self.recatalogNyObject(item)
        except: self.setSessionErrors(['Error while updating data.'])
        else: self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'updateBasketOfApprovals')
    def updateBasketOfApprovals(self, appids=[], delids=[], REQUEST=None):
        """ """
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
            REQUEST.RESPONSE.redirect('basketofapprovals_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'setSortOrder')
    def setSortOrder(self, ids, REQUEST):
        """ """
        for id in self.utConvertToList(ids):
            try: sortorder = abs(int(REQUEST.get('%s__sortorder' % id, 0)))
            except: sortorder = DEFAULT_SORTORDER
            try:
                ob = self._getOb(id)
                ob.sortorder = sortorder
                ob._p_changed = 1
            except:
                pass
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('sortorder_html')

    security.declareProtected(PERMISSION_VALIDATE_OBJECTS, 'updateBasketOfInvalidObjects')
    def updateBasketOfInvalidObjects(self, id=[], REQUEST=None):
        """ """
        ids_list = self.utConvertToList(id)
        validated_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
        checked_details = []
        i=0
        for k in ids_list:
            checked_details.append((k, int(REQUEST.get('radio_' + k, '')), REQUEST.get('comment_' + k, ''), validated_by))
            i += 1
        for item in checked_details:
            try:
                ob = self._getOb(item[0])
                ob.checkThis(item[1], item[2], item[3])
                self.recatalogNyObject(ob)
            except:
                pass
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('basketofvalidation_html')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/folder_manage_edit', globals())

    security.declareProtected(view_management_screens, 'manage_folder_subobjects_html')
    manage_folder_subobjects_html = PageTemplateFile('zpt/folder_manage_subobjects', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if self.publicinterface:
            l_index = self._getOb('index', None)
            if l_index is not None: return l_index()
        return self.getFormsTool().getContent({'here': self}, 'folder_index')

    security.declareProtected(view, 'index_rdf')
    def index_rdf(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getSyndicationTool().syndicateSomething(self.absolute_url(), self.getPublishedObjects())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_edit')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'basketofapprovals_html')
    def basketofapprovals_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_basketofapprovals')

    security.declareProtected(PERMISSION_VALIDATE_OBJECTS, 'basketofvalidation_html')
    def basketofvalidation_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_basketofvalidation')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'sortorder_html')
    def sortorder_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_sortorder')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'restrict_html')
    def restrict_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_restrict')

    security.declareProtected(view, 'menusubmissions')
    def menusubmissions(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_menusubmissions')

    security.declareProtected(view, 'menuactions')
    def menuactions(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_menuactions')

InitializeClass(NyFolder)
