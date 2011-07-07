from naaya.core.zope2util import DT2dt, icon_for_content_type
from naaya.core.utils import pretty_size

class NyContentTypeViewAdapter(object):
    def __init__(self, ob):
        self.ob = ob

    def version_status(self):
        return self.ob.version_status()

    def get_modification_date(self):
        return DT2dt(self.ob.releasedate)

    def get_info_text(self):
        return ""

    def get_icon(self):
        return {
            'url': self.ob.rstk.get_icon_for_object_index(self.ob),
            'title': self.ob.get_meta_label(),
        }

    def get_size(self):
        return ""

    def get_download_url(self):
        """ A direct download url """
        return ""


class NyFileViewAdapter(NyContentTypeViewAdapter):
    def get_icon(self):
        return icon_for_content_type(self.ob, self.ob.getContentType())

    def get_size(self):
        return pretty_size(self.ob.size)

    def get_download_url(self):
        """ A direct download url """
        return self.ob.getDownloadUrl()

class NyExFileViewAdapter(NyContentTypeViewAdapter):
    def get_icon(self):
        return icon_for_content_type(self.ob, self.ob.content_type())

    def get_size(self):
        return pretty_size(self.ob.size())

    def get_download_url(self):
        """ A direct download url """
        return self.ob.getDownloadUrl()

class GenericViewAdapter(object):
    def __init__(self, ob):
        self.ob = ob

    def version_status(self):
        return False, False

    def get_modification_date(self):
        return DT2dt(self.ob.bobobase_modification_time())

    def get_info_text(self):
        return ""

    def get_icon(self):
        if self.ob.icon:
            if hasattr(self.ob.aq_base, 'get_meta_label'):
                title = self.ob.get_meta_label()
            else:
                title = self.ob.meta_type
            return {
                'url': self.ob.icon,
                'title': title,
            }
        else:
            return None

    def get_download_url(self):
        """ A direct download url """
        return ""

    def get_size(self):
        return ""


class NyFolderViewAdapter(NyContentTypeViewAdapter):
    def get_info_text(self):
        if not (self.ob.display_subobject_count
                or (self.ob.display_subobject_count_for_admins
                    and self.ob.checkPermissionEditObject())):
            return ""

        trans = self.ob.getPortalTranslations().trans
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
