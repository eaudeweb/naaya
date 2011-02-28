"""Adapters for content view and zip import/export"""

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
