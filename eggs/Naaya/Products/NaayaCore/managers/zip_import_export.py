from StringIO import StringIO
from copy import copy
from zipfile import ZipFile, ZipInfo
import tempfile
import os.path

from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view
from Acquisition import Implicit
from DateTime import DateTime
from Globals import InitializeClass
from OFS.SimpleItem import Item
from Products.NaayaCore.events import ZipImportEvent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZPublisher.Iterators import IStreamIterator
from zope.component import adapts
from zope.event import notify
from zope.interface import Interface
from zope.interface import implements
import transaction

from Products.Naaya.NyFolder import NyFolder
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from naaya.content.contact.interfaces import INyContact
from naaya.content.document.interfaces import INyDocument
from naaya.content.event.interfaces import INyEvent
from naaya.content.file.interfaces import INyFile
from naaya.content.news.interfaces import INyNews
from naaya.content.story.interfaces import INyStory
from naaya.content.url.interfaces import INyURL
from naaya.core.utils import force_to_unicode
from naaya.core.zope2util import relative_object_path
from naaya.content.file.file_item import addNyFile

try:
    from naaya.content.bfile.bfile_item import addNyBFile
    def add_blob_file(location_obj, name, data):
        f = StringIO(data)
        f.filename = name
        if '.' in name:
            name = name.rsplit('.', 1)[0]
        return addNyBFile(location_obj, uploaded_file=f,
                          _send_notifications=False)
except ImportError:
    def add_blob_file(location_obj, name, data):
        raise NotImplementedError


def add_file(location_obj, name, data):
    site = location_obj.getSite()
    installed_meta_types = site.get_pluggable_installed_meta_types()
    if 'Naaya Blob File' in installed_meta_types:
        return add_blob_file(location_obj, name, data)
    elif 'Naaya File' in installed_meta_types:
        return addNyFile(location_obj, id=name, title=name,
                         file=data, _send_notifications=False)
    else:
        raise NotImplementedError

def read_zipfile_contents(data):
    """
    Read the contents of a zip file, and return a tuple
    of ``(folder_tree, files_iterator)``.

    ``folder_tree`` is a recursive data structure describing
    folders that need to be created.

    ``files_iterator`` is an iterator that yields tuples
    of ``(file_path, file_data)``.
    """
    try:
        zf = ZipFile(data)
    except Exception, e:
        raise ValueError(('Error reading Zip file', ))

    file_paths = set()
    folder_tree = []
    def add_to_folder_tree(folder_path):
        node = folder_tree
        for path_element in folder_path.split('/'):
            for name, contents in node:
                if name == path_element:
                    node = contents
                    break
            else:
                new_node = []
                node.append( (path_element, new_node) )
                node = new_node

    for p in zf.namelist():
        if p.startswith('_'):
            continue
        elif p.endswith('/'):
            add_to_folder_tree(p[:-1])
        else:
            if p.rsplit('/')[-1] == '.DS_Store':
                continue
            file_paths.add(p)
            if '/' in p:
                # maybe our parent folder is not listed explicitly
                add_to_folder_tree(p.rsplit('/')[0])

    def iterate_zipfile_files():
        for file_path in file_paths:
            file_data = zf.read(file_path)
            yield file_path, file_data

    return folder_tree, iterate_zipfile_files()


def create_folders(container, folder_tree, report_path):
    """
    `container` - reference to a NyFolder object

    `folder_tree` - list of two-tuples; in each tuple, first element is name
    of (current) folder; second element is another list of two-tuples.
    """

    folder_map = {}
    for kid_name, kid_tree in folder_tree:
        kid_id = addNyFolder(container, title=kid_name,
                             _send_notifications=False)
        kid_folder = container[kid_id]
        folder_map[kid_name] = kid_folder
        report_path(kid_id + '/')

        kid_report_path = lambda p: report_path('%s/%s' % (kid_id, p))
        kid_folder_map = create_folders(kid_folder, kid_tree, kid_report_path)
        for sub_kid_name, folder in kid_folder_map.iteritems():
            folder_map['%s/%s' % (kid_name, sub_kid_name)] = folder

    return folder_map

class ZipImportTool(Implicit, Item):
    title = "Zip import"

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'do_import')
    def do_import(self, data, REQUEST=None):
        """ """
        if REQUEST and not self.getParentNode().checkPermissionPublishObjects():
            raise Unauthorized

        errors = []
        container = self.getParentNode()

        try:
            folder_tree, zip_files = read_zipfile_contents(data)
        except ValueError, e:
            errors.append(e)
        else:
            created_file_paths = set()
            folder_map = create_folders(container, folder_tree,
                                        created_file_paths.add)
            folder_map[''] = container
            for file_path, file_data in zip_files:
                if '/' in file_path:
                    file_container_path, file_name = file_path.rsplit('/', 1)
                else:
                    file_container_path, file_name = '', file_path

                assert file_container_path in folder_map
                try:
                    file_container = folder_map[file_container_path]
                    file_ob_id = add_file(file_container, file_name, file_data)
                    file_ob = file_container[file_ob_id]
                except Exception, e:
                    errors.append((u"Error while creating file ${file_path}: ${error}",
                    {'file_path': file_path, 'error': force_to_unicode(str(e))}))
                else:
                    p = relative_object_path(file_ob, container)
                    created_file_paths.add(p)

        if errors:
            if REQUEST is not None:
                transaction.abort()
                self.setSessionErrorsTrans(errors)
                return self.index_html(REQUEST)

            else:
                return errors

        else:
            notify(ZipImportEvent(container, sorted(created_file_paths)))

            if REQUEST is not None:
                self.setSessionInfoTrans([('imported ${path}', {'path': pth}, ) for pth in
                                     sorted(created_file_paths)])
                return REQUEST.RESPONSE.redirect(container.absolute_url())

            else:
                return []

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'index_html')
    index_html = PageTemplateFile('../zpt/zip_import', globals())

InitializeClass(ZipImportTool)


class ZipExportTool(Implicit, Item):
    title = "Zip export"

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    security.declareProtected("Naaya - Zip export", 'do_export')
    def do_export(self, REQUEST=None):
        """
        Export the contents of the current folder as a Zip file. Returns an
        open file object. Caller should close the file to free temporary
        disk space.
        """
        if REQUEST and not self.getParentNode().checkPermissionView():
            raise Unauthorized

        errors = []

        my_container = self.getParentNode()

        objects_to_archive = self.gather_objects(my_container)

        temp_file = tempfile.TemporaryFile()
        zip_file = ZipFile(temp_file, 'w')
        archive_files = []
        try:
            for obj in objects_to_archive:
                added_path = None
                if self.is_exportable(obj):
                    added_path = self.add_object_to_zip(obj, zip_file)
                if added_path:
                    archive_files.append((obj.title_or_id(),
                                          getattr(obj, 'meta_label',
                                                  obj.meta_type),
                                          added_path))

            self.add_index(zip_file, archive_files)
            zip_file.close()
        except Exception, e:
            errors.append(e)

        temp_file.seek(0)

        if REQUEST is not None:
            if errors:
                transaction.abort()
                self.setSessionErrorsTrans(errors)
                return REQUEST.RESPONSE.redirect(my_container.absolute_url())
            else:
                response = REQUEST.RESPONSE
                response.setHeader('content-type', 'application/zip')
                response.setHeader('content-disposition',
                                   'attachment; filename=%s.zip' %
                                   my_container.getId())
                return stream_response(REQUEST.RESPONSE, temp_file)
        else:
            if errors:
                return errors
            else:
                return temp_file

    security.declarePrivate('gather_objects')
    def gather_objects(self, container):
        objects = []
        for obj in container.objectValues():
            objects.append(obj)
            if isinstance(obj, NyFolder):
                objects.extend(self.gather_objects(obj))
        return objects

    security.declarePrivate('add_object_to_zip')
    def add_object_to_zip(self, obj, zip_file):
        zip_path = self.get_zip_path(obj)
        if isinstance(zip_path, unicode):
            zip_path = zip_path.encode('utf-8')
        object_zip_data, object_zip_filename = self.get_zip_content(obj)
        if isinstance(obj, NyFolder):
            object_zip_data = 'Naaya Folder'
        else:
            zip_path_ext = os.path.splitext(zip_path)[1]
            original_ext = os.path.splitext(object_zip_filename)[1]
            if zip_path_ext != original_ext:
                zip_path += original_ext
        if object_zip_data:
            if isinstance(object_zip_data, unicode):
                object_zip_data = object_zip_data.encode('utf-8')

            #Add modification datetime
            if hasattr(obj, 'releasedate'):
                date = obj.releasedate
                zipinfo = ZipInfo(filename=zip_path,
                                  date_time=(date.year(), date.month(),
                                             date.day(), date.hour(),
                                             date.minute(),
                                             int(date.second()), ))
            else:
                zipinfo = ZipInfo(filename=zip_path)

            #Set external_attr to 16, otherwise empty folders will not be
            #preserved
            if object_zip_data == 'Naaya Folder':
                zipinfo.external_attr = 16

            zip_file.writestr(zipinfo, object_zip_data)
            return zip_path

    security.declarePrivate('add_index')
    def add_index(self, zip_file, archive_files):
        index_content = [('Title', 'Type', 'Path')]
        index_content.extend(archive_files)
        index_content = ['\t'.join(row).encode('utf-8') for \
                         row in index_content]
        index_content = '\n'.join(index_content)
        zip_file.writestr('index.txt', index_content)

    security.declarePrivate('get_zip_path')
    def get_zip_path(self, obj):
        my_container = self.getParentNode()
        my_container_path = my_container.getPhysicalPath()
        object_path = obj.getPhysicalPath()
        relative_object_path = object_path[len(my_container_path[:-1]):]
        object_zip_path = []
        for path in relative_object_path:
            object_zip_path.append(path)
        if isinstance(obj, NyFolder):
            object_zip_path.append('')
        return '/'.join(object_zip_path)

    security.declarePrivate('get_zip_content')
    def get_zip_content(self, obj):
        try:
            export_adapter = IZipExportObject(obj)
            return export_adapter()
        except TypeError:
            return ('', '')

    security.declarePrivate('user_has_view_permission')
    def user_has_view_permission(self, obj):
        return obj.checkPermissionView()

    security.declarePrivate('is_exportable')
    def is_exportable(self, obj):
        return obj.approved and self.user_has_view_permission(obj)

InitializeClass(ZipExportTool)

class IZipExportObject(Interface):
    def __call__():
        """Return data (as `str`) and filename, as a tuple
        """

class URLZipAdapter(object):
    implements(IZipExportObject)
    adapts(INyURL)

    def __init__(self, context):
        self.context = context

    def __call__(self):
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
        zip_data = '\n'.join(obj_data)
        zip_filename = '%s.html' % self.context.getId()
        return zip_data, zip_filename


class DocumentZipAdapter(object):
    implements(IZipExportObject)
    adapts(INyDocument)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        zip_data = ("<html><body>"
                    "<h1>%(document_title)s</h1>"
                    "<div>%(document_description)s</div>"
                    "<div>%(document_body)s</div>"
                    "</body></html>") % \
                 {'document_title': self.context.title,
                  'document_description': self.context.description,
                  'document_body': self.context.body}

        zip_filename = '%s.html' % self.context.getId()
        return zip_data, zip_filename

class StoryZipAdapter(object):
    implements(IZipExportObject)
    adapts(INyStory)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        zip_data = self.context.body
        zip_filename = '%s.html' % self.context.getId()
        return zip_data, zip_filename

class FileZipAdapter(object):
    implements(IZipExportObject)
    adapts(INyFile)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        zip_data = self.context.get_data()
        filename = self.context.utToUtf8(self.context.downloadfilename())
        filename = self.context.utSlugify(filename)
        zip_filename = filename
        return zip_data, zip_filename

class ContactZipAdapter(object):
    implements(IZipExportObject)
    adapts(INyContact)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        zip_data = self.context.export_vcard()
        zip_filename = '%s.vcf' % self.context.getId()
        return zip_data, zip_filename

class NewsAndEventZipExport(object):

    def export_data_for_zip(self):
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
        zip_data = '\n'.join(obj_data)
        zip_filename = '%s.html' % self.context.getId()
        return zip_data, zip_filename

class EventZipAdapter(NewsAndEventZipExport):
    implements(IZipExportObject)
    adapts(INyEvent)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return self.export_data_for_zip()

class NewsZipAdapter(NewsAndEventZipExport):
    implements(IZipExportObject)
    adapts(INyNews)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return self.export_data_for_zip()

class FileIterator(object):
    """
    A file-like object that can be streamed by ZServer.
    Copied from ``ZPublisher.Iterators.filestream_iterator`` and modified.
    """

    # Old Zope2-style interfaces. Hope this works.
    __implements__ = (IStreamIterator,)

    def __init__(self, data_file):
        self._data_file = data_file

    def next(self):
        data = self._data_file.read(2**16)
        if not data:
            self._data_file.close()
            raise StopIteration
        return data

    def __len__(self):
        data_file = self._data_file
        cur_pos = data_file.tell()
        data_file.seek(0, 2)
        size = data_file.tell()
        data_file.seek(cur_pos, 0)
        return size

def stream_response(RESPONSE, data_file):
    assert hasattr(RESPONSE, '_streaming')
    fi = FileIterator(data_file)
    RESPONSE.setHeader('Content-Length', str(len(fi)))
    return fi
