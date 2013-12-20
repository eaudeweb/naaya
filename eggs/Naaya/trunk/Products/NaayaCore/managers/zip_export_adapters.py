import re
from zope.interface import implements
from interfaces import IZipExportObject


# characters not allowed in filesystem names
illegal_fs_char = re.compile(r'[%s]' % re.escape('?[]/=+<>:;",*^\\\0'))


class DefaultZipAdapter(object):
    """
    Basic implementation of IZipExportObject. Useful to aviod boilerplate code
    (e.g. __init__) and to provide reasonable defaults.

    We define two properties, `extension` and `base_filename`, that are used
    to construct the `filename` property. Basically ``filename =
    base_filename + extension``, unless `base_filename` already ends with
    `extension`. Subclasses should consider providing a fixed value for
    `extension`.
    """
    implements(IZipExportObject)

    data = ''
    export_as_folder = False
    extension = ''

    def __init__(self, context):
        self.context = context

    @property
    def base_filename(self):
        base_name = self.context.title_or_id()
        return illegal_fs_char.sub('_', base_name).encode('utf-8')

    @property
    def filename(self):
        value = self.base_filename
        if not value.endswith(self.extension):
            value += self.extension
        return value

    @property
    def title(self):
        return self.context.title_or_id()

    @property
    def meta_label(self):
        return getattr(self.context, 'meta_label', self.context.meta_type)

    @property
    def timestamp(self):
        return getattr(self.context.aq_base, 'releasedate', None)

    @property
    def skip(self):
        if not self.context.checkPermissionView():
            return True
        elif not (self.context.approved or
            self.context.checkPermissionEditObject()):
            return True
        return False


class FolderZipAdapter(DefaultZipAdapter):
    """ Export a NyFolder """

    export_as_folder = True

    @property
    def filename(self):
        return super(FolderZipAdapter, self).filename + '/'


class URLZipAdapter(DefaultZipAdapter):

    extension = '.html'

    @property
    def data(self):
        obj = self.context
        portal = obj.getSite()
        schema_tool = portal.getSchemaTool()

        schema = schema_tool.getSchemaForMetatype(obj.meta_type)

        obj_data = []
        obj_data.append('<html><body>')
        obj_data.append('<h1>%s</h1>' % obj.title_or_id())

        for widget in schema.listWidgets():
            if widget.prop_name() in ['description', 'locator']:
                obj_widget_value = getattr(obj, widget.prop_name(), '')
                widget_data = widget._convert_to_form_string(obj_widget_value)

                if not widget_data:
                    continue

                obj_data.append('<h2>%s</h2><p><div>%s</div></p>' % (widget.title,
                                                                     widget_data))

        obj_data.append('</body></html>')
        return '\n'.join(obj_data)


class DocumentZipAdapter(DefaultZipAdapter):

    extension = '.html'

    @property
    def data(self):
        return ("<html><body>"
                    "<h1>%(document_title)s</h1>"
                    "<div>%(document_description)s</div>"
                    "<div>%(document_body)s</div>"
                    "</body></html>") % \
                 {'document_title': self.context.title,
                  'document_description': self.context.description,
                  'document_body': self.context.body}


class StoryZipAdapter(DefaultZipAdapter):

    extension = '.html'

    @property
    def data(self):
        return self.context.body


class FileZipAdapter(DefaultZipAdapter):

    @property
    def data(self):
        return self.context.get_data()

    @property
    def filename(self):
        filename = self.context.utToUtf8(self.context.downloadfilename())
        filename = self.context.utSlugify(filename)
        return filename


class ContactZipAdapter(DefaultZipAdapter):

    extension = '.vcf'

    @property
    def data(self):
        return self.context.export_vcard()


class NewsAndEventZipAdapter(DefaultZipAdapter):

    extension = '.html'

    @property
    def data(self):
        obj = self.context
        portal = obj.getSite()
        schema_tool = portal.getSchemaTool()

        schema = schema_tool.getSchemaForMetatype(obj.meta_type)

        obj_data = []
        obj_data.append('<html><body>')
        obj_data.append('<h1>%s</h1>' % obj.title_or_id())

        for widget in schema.listWidgets():
            if widget.prop_name() in ['sortorder', 'topitem', 'title']:
                continue
            if not widget.visible:
                continue
            obj_widget_value = getattr(obj, widget.prop_name(), '')
            widget_data = widget._convert_to_form_string(obj_widget_value)

            if not widget_data:
                continue

            obj_data.append('<h2>%s</h2><p><div>%s</div></p>' % (widget.title,
                                                                 widget_data))

        obj_data.append('</body></html>')
        return '\n'.join(obj_data)
