#Python imports

#Zope imports
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.interface import Interface, implements
from zope.component import adapts, provideAdapter
from OFS.interfaces import IItem

#Product imports
from Products.Naaya.constants import METATYPE_FOLDER
from Products.NaayaBase.NyPermissions import NyPermissions
from naaya.content.base.interfaces import INyContentObject
from interfaces import IObjectView
from Products.NaayaBase.constants import PERMISSION_COPY_OBJECTS, PERMISSION_DELETE_OBJECTS
from Products.Naaya.interfaces import INySite
from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile


class NyContentTypeViewAdapter(object):
    adapts(INyContentObject)
    implements(IObjectView)

    def __init__(self, ob):
        self.ob = ob

    def version_status_html(self):
        return self.ob.version_status()
provideAdapter(NyContentTypeViewAdapter)

class GenericViewAdapter(object):
    adapts(IItem)
    implements(IObjectView)

    def __init__(self, ob):
        self.ob = ob

    def version_status_html(self):
        editable = self.ob.checkPermissionEditObject()
        pt = PageTemplateFile('zpt/generic_version_status', globals())
        return pt.__of__(self.ob)(editable=editable)
provideAdapter(GenericViewAdapter)

class NyFolderBase(Folder, NyPermissions):
    """
    The base class for a folder-ish content type.
    Implements the functionality to display the listing for the folder.
    """

    security = ClassSecurityInfo()

    def contained_objects(self):
        return [o for o in self.objectValues(self.get_meta_types())
                if o.submitted==1]

    def contained_folders(self):
        return [f for f in self.objectValues(METATYPE_FOLDER)
                if f.submitted==1]


    def listed_folders_info(self, sort_on='title', sort_order=0):
        sorted_folders = self.utSortObjsListByAttr(self.contained_folders(), sort_on, sort_order)
        sorted_folders = self.utSortObjsListByAttr(sorted_folders, 'sortorder', 0)

        ret = []
        for f in sorted_folders:
            info = {
                    'del_permission': f.checkPermissionDeleteObject(),
                    'copy_permission': f.checkPermissionCopyObject(),
                    'edit_permission': f.checkPermissionEditObject(),
                    'approved': f.approved,
                    'self': f,
                    'object_view': IObjectView(f),
                    }

            if info['approved'] or info['del_permission'] or info['copy_permission'] or info['edit_permission']:
                ret.append(info)

        return ret

    def listed_objects_info(self, sort_on='title', sort_order=0):
        sorted_objects = self.utSortObjsListByAttr(self.contained_objects(), sort_on, sort_order)
        sorted_objects = self.utSortObjsListByAttr(sorted_objects, 'sortorder', 0)

        ret = []
        for o in sorted_objects:
            info = {
                    'del_permission': o.checkPermissionDeleteObject(),
                    'copy_permission': o.checkPermissionCopyObject(),
                    'edit_permission': o.checkPermissionEditObject(),
                    'approved': o.approved,
                    'self': o,
                    'object_view': IObjectView(o),
                    }

            if info['approved'] or info['del_permission'] or info['copy_permission'] or info['edit_permission']:
                ret.append(info)

        return ret


    security.declareProtected(view, 'folder_listing_info')
    def folder_listing_info(self, sort_on='title', sort_order=0):
        """ This function is called on the folder listing and it checkes whether or not
            to display the various buttons on that form
        """
        folders_info = self.listed_folders_info(sort_on, sort_order)
        objects_info = self.listed_objects_info(sort_on, sort_order)

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

    security.declareProtected(view, 'item_has_comments')
    def item_has_comments(self, object):
        """
        Checks if the object can have comments
        """
        if hasattr(object, 'aq_self'):
            real_object = object.aq_self
        else:
            real_object = object

        if hasattr(real_object, 'is_open_for_comments'):
            return real_object.is_open_for_comments()
        else:
            return False


    security.declareProtected(PERMISSION_COPY_OBJECTS, 'copyObjects')
    def copyObjects(self, REQUEST=None, **kwargs):
        """ """
        if not REQUEST:
            ids = self.utConvertToList(kwargs.get('id', []))
            return self.manage_copyObjects(ids)

        kwargs.update(REQUEST.form)
        ids = self.utConvertToList(kwargs.get('id', []))
        if not ids:
            self.setSessionErrors(['Please select one or more items to copy.'])
        else:
            try: self.manage_copyObjects(ids, REQUEST)
            except: self.setSessionErrors(['Error while copy data.'])
            else: self.setSessionInfo(['Item(s) copied.'])
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
            self.setSessionErrors(['Please select one or more items to cut.'])
        else:
            try: self.manage_cutObjects(ids, REQUEST)
            except: self.setSessionErrors(['Error while cut data.'])
            else: self.setSessionInfo(['Item(s) cut.'])
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(view, 'pasteObjects')
    def pasteObjects(self, REQUEST=None, **kwargs):
        """ """
        if not REQUEST:
            cp = kwargs.get('cp_data', None)
            return self.manage_pasteObjects(cp)

        if not self.checkPermissionPasteObjects():
            self.setSessionErrors(['You are not allowed to paste objects in this context.'])
        else:
            try: self.manage_pasteObjects(None, REQUEST)
            except: self.setSessionErrors(['Error while paste data.'])
            else: self.setSessionInfo(['Item(s) pasted.'])
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
            self.setSessionErrors(['Please select one or more items to delete.'])
        else:
            try:
                self.manage_delObjects(id_list)
            except Exception, err:
                self.setSessionErrors(['Error while delete data.'])
                zLOG.LOG("NyFolder.deleteObjects", zLOG.DEBUG, err)
            else:
                self.setSessionInfo(['Item(s) deleted.'])
        return REQUEST.RESPONSE.redirect('index_html')

class ObjectListingPortlet(object):
    implements(INyPortlet)
    adapts(INySite)

    title = 'List contained objects'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        return self.template.__of__(context)()

    template = NaayaPageTemplateFile('zpt/listing_portlet', globals(), 'naaya.core.folder.listing_portlet')

