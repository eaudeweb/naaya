from naaya.core.zope2util import DT2dt
from naaya.core.utils import pretty_size, icon_for_content_type

def _get_icon_url(ob):
    site = ob.getSite()
    scheme = site.getLayoutTool().getCurrentSkinScheme()
    name = ob.meta_type.replace(' ', '_')
    skin_icon = scheme._getOb(name + '-icon', None)
    skin_icon_marked = scheme._getOb(name + '-icon-marked', None)
    if skin_icon is None:
        skin_icon = scheme.aq_parent._getOb(name + '-icon', None)
    if skin_icon_marked is None:
        skin_icon_marked = scheme.aq_parent._getOb(name + '-icon-marked', None)

    if not ob.approved and skin_icon_marked is not None:
        return skin_icon_marked.absolute_url()

    elif skin_icon is not None:
        # even if object is unapproved, choose the customized icon
        return skin_icon.absolute_url()

    elif ob.approved:
        return ob.icon

    else:
        return ob.icon_marked


class GenericViewAdapter(object):
    def __init__(self, ob):
        self.ob = ob

    def version_status(self):
        return False, False

    def get_modification_date(self):
        return DT2dt(getattr(self.ob.aq_base, 'last_modification', self.ob.bobobase_modification_time()))

    def get_info_text(self):
        return ""

    def get_icon(self):
        if self.ob.icon:
            if hasattr(self.ob.aq_base, 'get_meta_label'):
                title = self.ob.get_meta_label()
            else:
                title = self.ob.meta_type
            if not getattr(self.ob.aq_base, 'approved', True):
                title = 'This %s is not approved' % title
            return {
                'url': _get_icon_url(self.ob),
                'title': title,
            }
        else:
            return None

    def get_download_url(self):
        """ A direct download url """
        return ""

    def get_size(self):
        return ""


class NyContentTypeViewAdapter(GenericViewAdapter):

    def version_status(self):
        return self.ob.version_status()

class NyFileViewAdapter(NyContentTypeViewAdapter):
    def get_icon(self):
        return icon_for_content_type(self.ob.content_type, self.ob.approved)

    def get_size(self):
        return pretty_size(self.ob.size)

    def get_download_url(self):
        """ A direct download url """
        return self.ob.getDownloadUrl()


class NyExFileViewAdapter(NyContentTypeViewAdapter):
    def get_icon(self):
        return icon_for_content_type(self.ob.content_type(), self.ob.approved)

    def get_size(self):
        return pretty_size(self.ob.size())

    def get_download_url(self):
        """ A direct download url """
        return self.ob.getDownloadUrl()


class NyFolderViewAdapter(NyContentTypeViewAdapter):
    def get_info_text(self):
        if not (self.ob.display_subobject_count
                or (self.ob.display_subobject_count_for_admins
                    and self.ob.checkPermissionEditObject())):
            return ""

        trans = self.ob.getPortalI18n().get_translation
        msg = []

        lenfol = len(self.ob.listed_folders_info())
        if lenfol > 0:
            if lenfol > 1:
                txt = trans('${number} subfolders', number=str(lenfol))
            else:
                txt = trans('1 subfolder')
            msg.append(txt)

        lenobj = len(self.ob.listed_objects_info())
        if lenobj > 0:
            if lenobj > 1:
                txt = trans('${number} items', number=str(lenobj))
            else:
                txt = trans('1 item')
            msg.append(txt)

        if msg:
            return "(" + ', '.join(msg) + ")"
        else:
            return trans("folder contains no sub-items")


class FolderMetaTypes(object):
    """
    This is a wrapper for *NyFolder*, allowing you to manage the
    subobjects list (or folder meta types).

    By default, a folder uses default subobjects setting, available in
    *Portal Properties*, or inherit the settings of its parent at creation.

    To make a folder use default subobjects, just call `set_values` with None.

    Please be aware that calling `set_values` with a specific list, `add`
    or `remove` methods will make the folder stop using the default subobjects.

    """

    def __init__(self, nyfolder):
        """ Wrapper for NyFolder """
        # cross import issue
        from Products.Naaya.NyFolderBase import NyFolderBase
        assert(isinstance(nyfolder, NyFolderBase))
        self.context = nyfolder

    def get_values(self):
        """
        Returns meta types that can be present as subobjects.
        Uses the `use default` logic, always returns list-type

        """
        folder_meta_types = getattr(self.context, 'folder_meta_types', ())
        if folder_meta_types is None:
            # None means use global settings
            return list(self.context.getSite().adt_meta_types)
        else:
            return list(folder_meta_types)

    def set_values(self, meta_types):
        """
        Set folder subobject meta_types.
        Calling this with `meta_types`=None,
        makes this folder's subobject meta types synced
        with global ones (the `use default` logic).

        """
        assert(meta_types is None or isinstance(meta_types, list))
        self.context.folder_meta_types = meta_types

    def add(self, meta_type):
        """ Adds meta type """
        existing = self.get_values()
        if meta_type not in existing:
            existing.append(meta_type)
            self.set_values(existing)

    def remove(self, meta_type):
        """ Removes a folder meta type """
        existing = self.get_values()
        if meta_type in existing:
            existing.remove(meta_type)
            self.set_values(existing)

    @property
    def has_custom_value(self):
        """
        Returns True if folder subobjects setting is customized.
        If False, folder uses default meta types of subobjects,
        as specified in Portal Properties.
        Uses the `use default` logic.

        """
        return self.context.folder_meta_types is not None
