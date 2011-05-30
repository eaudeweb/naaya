"""Adapters for content view and zip import/export"""

from Products.Naaya.adapters import NyContentTypeViewAdapter
from naaya.core.zope2util import DT2dt, ensure_tzinfo, icon_for_content_type
from naaya.core.utils import pretty_size

from interfaces import INyBFile

class BFileZipAdapter(object):
    def __init__(self, context):
        self.context = context

    def __call__(self):
        zip_data = self.context.current_version.open().read()
        zip_filename = self.context.current_version.filename
        return zip_data, zip_filename

class GenericViewer(object):
    """Generic view for all mime types"""

    def __init__(self, bfile):
        self.bfile = bfile

    def __call__(self, context):
        request = context.REQUEST
        return self.bfile.send_data(request.RESPONSE,as_attachment=False,
                                    REQUEST=request)

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
        trans = self.ob.getPortalTranslations().trans
        version_count = len(self.ob._versions)
        if version_count > 1:
            msg = trans("${number} versions", number=str(version_count))
            return "(%s)" % msg
        else:
            return ""

    def get_icon(self):
        if self.ob.approved:
            version = self.ob.current_version

            if version is not None:
                return icon_for_content_type(self.ob, version.content_type)

        return super(BFileViewAdapter, self).get_icon()

    def get_size(self):
        version = self.ob.current_version
        if version is not None:
            return pretty_size(version.size)
        else:
            return ""

    def get_download_url(self):
        return self.ob.current_version_download_url()


