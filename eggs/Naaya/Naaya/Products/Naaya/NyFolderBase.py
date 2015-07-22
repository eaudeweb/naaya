import operator
import logging

from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view

from Products.Naaya.constants import METATYPE_FOLDER, LABEL_NYFOLDER, PERMISSION_ADD_FOLDER
from Products.NaayaBase.NyPermissions import NyPermissions
from Products.NaayaBase.constants import PERMISSION_COPY_OBJECTS, PERMISSION_DELETE_OBJECTS, PERMISSION_PUBLISH_OBJECTS, MESSAGE_SAVEDCHANGES, MESSAGE_ERROROCCURRED
from Products.Naaya.interfaces import IObjectView
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.Naaya.adapters import FolderMetaTypes


logger = logging.getLogger(__name__)


class NyFolderBase(Folder, NyPermissions):
    """
    The base class for a `folderish` content type.
    Implements the functionality to display the listing for the folder.

    """

    security = ClassSecurityInfo()

    _dynamic_content_types = {}

    folder_meta_types = ()

    def contained_objects(self):
        return [o for o in self.objectValues(self.get_meta_types())
                if getattr(o, 'submitted', 0) == 1]

    def contained_folders(self):
        return [f for f in self.objectValues(METATYPE_FOLDER)
                if getattr(f, 'submitted', 0) == 1]


    security.declarePublic('getPublishedFolders')
    def getPublishedFolders(self):
        folders = []
        if not self.checkPermissionView():
            return folders
        for obj in self.objectValues(self.get_naaya_containers_metatypes()):
            if not getattr(obj, 'approved', False):
                continue
            if not getattr(obj, 'submitted', False):
                continue
            folders.append(obj)
        folders.sort(key=lambda obj: getattr(obj, 'sortorder', 100))
        return folders

    def getPublishedObjects(self, items=0):
        doc_metatypes = [m for m in self.get_meta_types()
                         if m not in self.get_naaya_containers_metatypes()]
        result = []
        for obj in self.objectValues(doc_metatypes):
            if not getattr(obj, 'approved', False):
                continue
            if not getattr(obj, 'submitted', False):
                continue
            result.append(obj)

        if items:
            result = result[:items]

        return result

    def getPublishedContent(self):
        r = self.getPublishedFolders()
        r.extend(self.getPublishedObjects())
        return r

    def getPendingFolders(self): return [x for x in self.objectValues(METATYPE_FOLDER) if x.approved==0 and x.submitted==1]
    def getPendingObjects(self): return [x for x in self.contained_objects() if x.approved==0 and x.submitted==1]
    def getPendingContent(self):
        r = self.getPendingFolders()
        r.extend(self.getPendingObjects())
        return r

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processPendingContent')
    def processPendingContent(self, appids=[], delids=[], REQUEST=None):
        """
        Process the pending content inside this folder.

        Objects with ids in appids list will be approved.

        Objects with ids in delids will be deleted.
        """
        for id in self.utConvertToList(appids):
            ob = self._getOb(id, None)
            if not ob:
                continue
            if hasattr(ob.aq_base, 'approveThis'):
                ob.approveThis()
            if hasattr(ob.aq_base, 'takeEditRights'):
                ob.takeEditRights()
            if hasattr(ob.aq_base, 'inherit_view_permission'):
                ob.inherit_view_permission()
            ob.releasedate = self.utGetTodayDate()
            self.recatalogNyObject(ob)

        for id in self.utConvertToList(delids):
            try: self._delObject(id)
            except: pass
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processPublishedContent')
    def processPublishedContent(self, appids=[], delids=[], REQUEST=None):
        """
        Process the published content inside this folder.

        Objects with ids in appids list will be unapproved.

        Objects with ids in delids will be deleted.
        """
        for id in self.utConvertToList(appids):
            ob = self._getOb(id, None)
            if not ob:
                continue
            if hasattr(ob.aq_base, 'approveThis'):
                ob.approveThis(0, None)
            if hasattr(ob.aq_base, 'giveEditRights'):
                ob.giveEditRights()
            if hasattr(ob.aq_base, 'dont_inherit_view_permission'):
                ob.dont_inherit_view_permission()
            self.recatalogNyObject(ob)
        for id in self.utConvertToList(delids):
            try: self._delObject(id)
            except: pass
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)


    def listed_folders_info(self, skey='sortorder', rkey=0,
                            sort_on='title', sort_order=0):
        sorted_folders = self.utSortObjsListByAttr(self.contained_folders(),
                                                   sort_on, sort_order)
        sorted_folders = self.utSortObjsListByAttr(sorted_folders, skey, rkey)

        ret = []
        for f in sorted_folders:
            f_view = IObjectView(f)
            versionable, editable = f_view.version_status()
            info = {
                'view_permission': f.checkPermissionView(),
                'del_permission': f.checkPermissionDeleteObject(),
                'copy_permission': f.checkPermissionCopyObject(),
                'edit_permission': f.checkPermissionEditObject(),
                'approved': f.approved,
                'versionable': versionable,
                'editable': editable,
                'self': f,
                'view': f_view,
            }

            if info['approved'] or info['del_permission'] or \
                    info['copy_permission'] or info['edit_permission']:
                ret.append(info)

        return ret

    def listed_objects_info(self, skey='sortorder', rkey=0,
                            sort_on='title', sort_order=0):
        sorted_objects = self.utSortObjsListByAttr(self.contained_objects(),
                                                   sort_on, sort_order)
        sorted_objects = self.utSortObjsListByAttr(sorted_objects, skey, rkey)

        ret = []
        for o in sorted_objects:
            o_view = IObjectView(o)
            versionable, editable = o_view.version_status()
            info = {
                'view_permission': o.checkPermissionView(),
                'del_permission': o.checkPermissionDeleteObject(),
                'copy_permission': o.checkPermissionCopyObject(),
                'edit_permission': o.checkPermissionEditObject(),
                'approved': o.approved,
                'versionable': versionable,
                'editable': editable,
                'self': o,
                'view': o_view,
            }
            if info['view_permission'] and (
                    info['approved'] or info['del_permission'] or
                    info['copy_permission'] or info['edit_permission']):
                ret.append(info)

        return ret


    security.declareProtected(view, 'folder_listing_info')
    def folder_listing_info(self, skey='sortorder', rkey=0,
                            sort_on='title', sort_order=0):
        """ This function is called on the folder listing and checks whether to
        display various buttons in the form it is called.

        """
        folders_info = self.listed_folders_info(skey, rkey, sort_on, sort_order)
        objects_info = self.listed_objects_info(skey, rkey, sort_on, sort_order)

        if skey == 'modif_date':
            def modif_date_getter(info):
                return IObjectView(info['self']).get_modification_date()
            folders_info.sort(key=modif_date_getter, reverse=bool(rkey))
            objects_info.sort(key=modif_date_getter, reverse=bool(rkey))

        infos = []
        infos.extend(folders_info)
        infos.extend(objects_info)

        can_be_deleted = set([i['self'] for i in infos if i['del_permission']])
        can_be_copied = set([i['self'] for i in infos if i['copy_permission']])
        can_be_edited = set([i['self'] for i in infos if i['edit_permission']])

        can_be_selected = can_be_deleted.union(can_be_copied)
        can_be_cut = can_be_deleted.intersection(can_be_copied)

        can_be_operated = can_be_selected.union(can_be_edited)

        ret = {'folders': folders_info, 'objects': objects_info}
        ret['btn_select'] = len(can_be_selected) > 0
        ret['btn_delete'] = len(can_be_deleted) > 0
        ret['btn_copy'] = len(can_be_copied) > 0
        ret['btn_cut'] = len(can_be_cut) > 0
        ret['btn_paste'] = self.cb_dataValid() and self.checkPermissionPasteObjects()
        ret['can_operate'] = len(can_be_operated) > 0

        return ret

    security.declareProtected(view, 'folder_listing_ratings')
    def folder_listing_ratings(self):
        """ This function is called on the folder listing and it checks
        whether there is at least one object that provides ratings

        """

        folders_info = self.listed_folders_info()
        objects_info = self.listed_objects_info()

        infos = []
        infos.extend(folders_info)
        infos.extend(objects_info)

        for info in infos:
            try:
                ratable = info['self'].is_ratable()
                if ratable: return True
            except: pass
        return False

    security.declareProtected(view, 'item_has_title')
    def item_has_title(self, object, obj_title=''):
        """
        Checks if the object has no display title and if it
        has a title in at least one of the portal languages
        """

        if isinstance(object, str): return 0

        if obj_title == '':
            for lang in self.gl_get_languages():
                if object.getLocalProperty('title', lang):
                    return 1

    security.declareProtected(view, 'copyObjects')
    def copyObjects(self, REQUEST=None, **kwargs):
        """ """
        ids = self.utConvertToList(kwargs.get('id', []))

        if not self.checkPermissionCopyObjects(ids):
            raise Unauthorized

        if not REQUEST:
            return self.manage_copyObjects(ids)

        kwargs.update(REQUEST.form)
        ids = self.utConvertToList(kwargs.get('id', []))
        if not ids:
            self.setSessionErrorsTrans('Please select one or more items to copy.')
        else:
            try: self.manage_copyObjects(ids, REQUEST)
            except: self.setSessionErrorsTrans('Error while copy data.')
            else: self.setSessionInfoTrans('Item(s) copied.')
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(view, 'cutObjects')
    def cutObjects(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)
        id_list = self.utConvertToList(kwargs.get('id', []))

        if not self.checkPermissionDeleteObjects(id_list):
            raise Unauthorized

        if not REQUEST:
            return self.manage_cutObjects(id_list)
        elif not id_list:
            self.setSessionErrorsTrans('Please select one or more items to cut.')
        else:
            try: self.manage_cutObjects(id_list, REQUEST)
            except: self.setSessionErrorsTrans('Error while cut data.')
            else: self.setSessionInfoTrans('Item(s) cut.')
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(view, 'pasteObjects')
    def pasteObjects(self, REQUEST=None, **kwargs):
        """ """
        if not REQUEST:
            cp = kwargs.get('cp_data', None)
            return self.manage_pasteObjects(cp)

        if not self.checkPermissionPasteObjects():
            self.setSessionErrorsTrans('You are not allowed to paste objects in this context.')
        else:
            try: self.manage_pasteObjects(None, REQUEST)
            except: self.setSessionErrorsTrans('Error while pasting data.')
            else: self.setSessionInfoTrans('Item(s) pasted.')
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(view, 'deleteObjects')
    def deleteObjects(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)
        id_list = self.utConvertToList(kwargs.get('id', []))

        if not self.checkPermissionDeleteObjects(id_list):
            raise Unauthorized

        if not REQUEST:
            return self.manage_delObjects(id_list)
        elif not id_list:
            self.setSessionErrorsTrans('Please select one or more items to delete.')
        else:
            try:
                self.manage_delObjects(id_list)
            except Exception, err:
                self.setSessionErrorsTrans('Error while deleting data.')
                logger.exception("Exception when deleting objects")
            else:
                self.setSessionInfoTrans('Item(s) deleted.')
        return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declarePublic('get_meta_types')
    def get_meta_types(self, folder=0):
        """
        returns a list with objects metatypes
        """
        res = []
        if folder==1:
            res.append(METATYPE_FOLDER)
        res.extend(self._dynamic_content_types.keys())
        res.extend(self.get_pluggable_installed_meta_types())
        return res


    security.declarePublic('get_meta_type_label')
    def get_meta_type_label(self, meta_type=None):
        """
        returns label from meta_type
        """
        if not meta_type:
            return ''
        # Folder
        if meta_type == METATYPE_FOLDER:
            return LABEL_NYFOLDER
        # Plugable content
        pc = self.get_pluggable_content()
        meta_item = pc.get(meta_type, {})
        schema = self.getSchemaTool().getSchemaForMetatype(meta_type)
        if schema:
            return schema.title_or_id()
        # Plugable content, no schema
        pluggable_content = self.get_pluggable_content()
        if meta_type in pluggable_content:
            return pluggable_content[meta_type]['label']
        # Dynamic meta types
        meta_item = self._dynamic_content_types.get(meta_type, ())
        if len(meta_item) <= 1 or not meta_item[1]:
            return meta_type
        return meta_item[1]

    def process_submissions(self):
        """Returns info meta_types and their constructors views that can be
        added inside a folder.

        [(FUNC_NAME, LABEL), (...), ...]

        """

        folder_meta_types = FolderMetaTypes(self).get_values()

        r = []
        ra = r.append

        #check for adding folders
        if METATYPE_FOLDER in folder_meta_types:
            if self.checkPermission(PERMISSION_ADD_FOLDER):
                ra(('folder_add_html', LABEL_NYFOLDER))

        # check for adding dynamic registered content types
        for dynamic_key, dynamic_value in self._dynamic_content_types.items():
            if dynamic_key in folder_meta_types:
                if self.checkPermission(dynamic_value[2]):
                    ra(dynamic_value[:2])

        #check pluggable content
        pc = self.get_pluggable_content()
        schema_tool = self.getSchemaTool()

        for k in self.get_pluggable_installed_meta_types():
            if k not in folder_meta_types:
                continue
            if k not in pc:
                continue
            if not self.checkPermission(pc[k]['permission']):
                continue

            schema = schema_tool.getSchemaForMetatype(k)
            if schema is not None:
                meta_label = schema.title_or_id()
            else:
                meta_label = pc[k]['label']
            ra((pc[k]['add_form'], meta_label))

        return r

    def _verifyObjectPaste(self, object, validate_src=1):
        if validate_src == 2:   # paste after cut
            if not object.checkPermissionDeleteObject():
                raise Unauthorized
            validate_src = 1 # let super validate as in paste after copy
        return super(NyFolderBase, self)._verifyObjectPaste(object, validate_src)


class ObjectListingPortlet(object):

    title = 'List contained objects'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        return self.template.__of__(context)()

    template = NaayaPageTemplateFile('zpt/listing_portlet', globals(), 'naaya.core.folder.listing_portlet')
