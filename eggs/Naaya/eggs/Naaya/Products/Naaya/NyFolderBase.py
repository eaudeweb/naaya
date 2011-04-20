
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import Interface, implements
from zope.component import adapts, provideAdapter
from OFS.interfaces import IItem
import zLOG

from Products.Naaya.constants import METATYPE_FOLDER, LABEL_NYFOLDER, PERMISSION_ADD_FOLDER
from Products.NaayaBase.NyPermissions import NyPermissions
from Products.NaayaBase.constants import PERMISSION_COPY_OBJECTS, PERMISSION_DELETE_OBJECTS
from Products.Naaya.interfaces import INySite, IObjectView
from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile


class NyFolderBase(Folder, NyPermissions):
    """
    The base class for a `folderish` content type.
    Implements the functionality to display the listing for the folder.

    """

    security = ClassSecurityInfo()

    _dynamic_content_types = {}

    def contained_objects(self):
        return [o for o in self.objectValues(self.get_meta_types())
                if getattr(o, 'submitted', 0) == 1]

    def contained_folders(self):
        return [f for f in self.objectValues(METATYPE_FOLDER)
                if getattr(f, 'submitted', 0) == 1]


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
                'del_permission': f.checkPermissionDeleteObject(),
                'copy_permission': f.checkPermissionCopyObject(),
                'edit_permission': f.checkPermissionEditObject(),
                'approved': f.approved,
                'versionable': versionable,
                'editable': editable,
                'self': f,
                'view': f_view,
            }

            if info['approved'] or info['del_permission'] or info['copy_permission'] or info['edit_permission']:
                ret.append(info)

        return ret

    def listed_objects_info(self, skey='sortorder', rkey=0,
                            sort_on='title', sort_order=0):
        sorted_objects = self.utSortObjsListByAttr(self.contained_objects(),
                                                   sort_on, sort_order)
        sorted_objects = self.utSortObjsListByAttr(sorted_objects, skey, rkey)

        ret = []
        site_url = self.getSite().absolute_url()
        for o in sorted_objects:
            o_view = IObjectView(o)
            versionable, editable = o_view.version_status()
            info = {
                'del_permission': o.checkPermissionDeleteObject(),
                'copy_permission': o.checkPermissionCopyObject(),
                'edit_permission': o.checkPermissionEditObject(),
                'approved': o.approved,
                'versionable': versionable,
                'editable': editable,
                'self': o,
                'view': o_view,
            }

            if info['approved'] or info['del_permission'] or info['copy_permission'] or info['edit_permission']:
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

    security.declareProtected(PERMISSION_COPY_OBJECTS, 'copyObjects')
    def copyObjects(self, REQUEST=None, **kwargs):
        """ """
        if not REQUEST:
            ids = self.utConvertToList(kwargs.get('id', []))
            return self.manage_copyObjects(ids)

        kwargs.update(REQUEST.form)
        ids = self.utConvertToList(kwargs.get('id', []))
        if not ids:
            self.setSessionErrorsTrans('Please select one or more items to copy.')
        else:
            try: self.manage_copyObjects(ids, REQUEST)
            except: self.setSessionErrorsTrans('Error while copy data.')
            else: self.setSessionInfoTrans('Item(s) copied.')
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'cutObjects')
    def cutObjects(self, REQUEST=None, **kwargs):
        """ """
        if not REQUEST:
            ids = self.utConvertToList(kwargs.get('id', []))
            return self.manage_cutObjects(ids)

        kwargs.update(REQUEST.form)
        ids = self.utConvertToList(kwargs.get('id', []))
        if not ids:
            self.setSessionErrorsTrans('Please select one or more items to cut.')
        else:
            try: self.manage_cutObjects(ids, REQUEST)
            except: self.setSessionErrorsTrans('Error while cut data.')
            else: self.setSessionInfoTrans('Item(s) cut.')
        return REQUEST.RESPONSE.redirect(self.absolute_url())

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
            except: self.setSessionErrorsTrans('Error while paste data.')
            else: self.setSessionInfoTrans('Item(s) pasted.')
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteObjects')
    def deleteObjects(self, REQUEST=None, **kwargs):
        """ """
        if not REQUEST:
            ids = self.utConvertToList(kwargs.get('id', []))
            return self.manage_delObjects(ids)

        kwargs.update(REQUEST.form)
        id_list = self.utConvertToList(kwargs.get('id', []))
        if not id_list:
            self.setSessionErrorsTrans('Please select one or more items to delete.')
        else:
            try:
                self.manage_delObjects(id_list)
            except Exception, err:
                self.setSessionErrorsTrans('Error while delete data.')
                zLOG.LOG("NyFolder.deleteObjects", zLOG.DEBUG, err)
            else:
                self.setSessionInfoTrans('Item(s) deleted.')
        return REQUEST.RESPONSE.redirect('index_html')



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

        if hasattr(self, 'folder_meta_types'):
            folder_meta_types = self.folder_meta_types
        else:
            folder_meta_types = [METATYPE_FOLDER,
                                 'Naaya Forum', 'Naaya Mega Survey',
                                 'Naaya Photo Gallery', 'Naaya Photo Folder',
                                 'Naaya TalkBack Consultation']
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

class ObjectListingPortlet(object):

    title = 'List contained objects'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        return self.template.__of__(context)()

    template = NaayaPageTemplateFile('zpt/listing_portlet', globals(), 'naaya.core.folder.listing_portlet')
