from Products.NaayaCore.managers.zip_import_export import IZipExportObject

from interfaces import INyBFile

class BFileZipAdapter(object):
    implements(IZipExportObject)
    adapts(INyBFile)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        zip_data = self.context.current_version.open().read()
        zip_filename = self.context.current_version.filename
        return zip_data, zip_filename
