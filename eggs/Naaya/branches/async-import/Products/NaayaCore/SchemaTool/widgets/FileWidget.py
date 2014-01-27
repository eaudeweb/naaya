from Globals import InitializeClass
from zExceptions import NotFound
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from naaya.content.bfile.NyBlobFile import NyBlobFile, make_blobfile
from Widget import Widget, manage_addWidget

def addFileWidget(container, id="", title="File Widget", REQUEST=None, **kwargs):
    """ Contructor for File Widget"""
    return manage_addWidget(FileWidget, container, id, title, REQUEST, **kwargs)

class FileWidget(Widget):
    """ File Widget """

    meta_type = "Naaya Schema File Widget"
    meta_label = "file input"
    meta_description = "File input box"

    _constructors = (addFileWidget,)

    def parseFormData(self, data):
        if data is None or not getattr(data, 'filename', ''):
            return None
        return make_blobfile(data)

    def new_value(self, prev_prop_value, prop_value):
        # if the new value is None and the old value exists, don't overwrite.
        if prop_value is None:
            return prev_prop_value
        else:
            return prop_value

    template = PageTemplateFile('../zpt/property_widget_file', globals())

InitializeClass(FileWidget)


def download_file(context, request):
    prop_name = request.form.get('name', None)
    if not prop_name:
        raise NotFound

    schema = context._get_schema()
    try:
        widget = schema.getWidget(prop_name)
    except KeyError:
        raise NotFound

    value = getattr(context.aq_base, prop_name)
    if not isinstance(value, NyBlobFile):
        raise NotFound

    return value.send_data(REQUEST=request, RESPONSE=request.RESPONSE)
