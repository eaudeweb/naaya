"""Adapters for content view and zip import/export"""

from Products.Naaya.adapters import NyContentTypeViewAdapter
from Products.NaayaCore.managers.zip_export_adapters import DefaultZipAdapter
from naaya.core.utils import pretty_size, icon_for_content_type
from naaya.core.zope2util import DT2dt, ensure_tzinfo
import os.path

#from interfaces import INyBFile


class BFileZipAdapter(DefaultZipAdapter):

    @property
    def data(self):
        return self.context.current_version.open().read()

    @property
    def extension(self):
        return os.path.splitext(self.context.current_version.filename)[1]


class GenericViewer(object):
    """Generic view for all mime types"""

    def __init__(self, bfile):
        self.bfile = bfile

    def __call__(self, context):
        request = context.REQUEST
        return self.bfile.send_data(
            request.RESPONSE, as_attachment=False, REQUEST=request)


class ZipViewer(object):
    """Display a zip file contents into a html page"""

    def __init__(self, bfile):
        self.bfile = bfile

    def __call__(self, context):
        from zipfile import ZipFile
        zfile = ZipFile(self.bfile.open())
        return context.getFormsTool()['bfile_quickview_zipfile'](
            namelist=zfile.namelist())


class BFileViewAdapter(NyContentTypeViewAdapter):
    def get_modification_date(self):
        version = self.ob.current_version
        if version is None:
            return DT2dt(self.ob.releasedate)
        else:
            return ensure_tzinfo(version.timestamp)

    def get_info_text(self):
        trans = self.ob.getPortalI18n().get_translation
        container = self.ob._versions
        # OBS: for localizedbfile count langs, v is str (the key of the lang)
        versions = [v for v in container if not getattr(v, 'removed', True)]
        version_count = len(versions)
        if version_count > 1:
            msg = trans("${number} versions", number=str(version_count))
            return "(%s)" % msg
        else:
            return ""

    def get_icon(self):
        version = self.ob.current_version

        if version is not None:
            return icon_for_content_type(version.content_type, self.ob.approved)

        return super(BFileViewAdapter, self).get_icon()

    def get_size(self):
        version = self.ob.current_version
        if version is not None:
            return pretty_size(version.size)
        else:
            return ""

    def get_download_url(self):
        return self.ob.current_version_download_url()

