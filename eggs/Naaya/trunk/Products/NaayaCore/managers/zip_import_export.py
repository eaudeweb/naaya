from StringIO import StringIO
from zipfile import ZipFile, ZipInfo
import tempfile

from AccessControl import ClassSecurityInfo, Unauthorized
from Acquisition import Implicit
from Globals import InitializeClass
from OFS.SimpleItem import Item
from Products.NaayaCore.events import ZipImportEvent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZPublisher.Iterators import IStreamIterator
from zope.event import notify
import transaction
from zope import interface

from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaBase.constants import (PERMISSION_ZIP_EXPORT)
from Products.NaayaCore.managers.utils import slugify
from naaya.core.utils import force_to_unicode
from naaya.core.zope2util import relative_object_path, get_site_manager
from naaya.content.file.file_item import addNyFile

from interfaces import IZipExportObject

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
        try:
            folder_path = folder_path.decode('utf-8')
        except UnicodeDecodeError:
            folder_path = folder_path.decode('CP437')
        node = folder_tree
        for path_element in folder_path.split('/'):
            for name, contents in node:
                if name == path_element:
                    node = contents
                    break
            else:
                new_node = []
                node.append((path_element, new_node))
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
                add_to_folder_tree(p.rsplit('/', 1)[0])

    def iterate_zipfile_files():
        for file_path in file_paths:
            file_data = zf.read(file_path)
            try:
                file_path = file_path.decode('utf-8')
            except UnicodeDecodeError:
                file_path = file_path.decode('CP437')
            except:
                # try to go forward with the file_path as it is
                pass
            yield file_path, file_data

    return folder_tree, iterate_zipfile_files()


def create_folders(container, folder_tree, report_path, skip_existing=False):
    """
    `container` - reference to a NyFolder object

    `folder_tree` - list of two-tuples; in each tuple, first element is name
    of (current) folder; second element is another list of two-tuples.
    """

    folder_map = {}
    for kid_name, kid_tree in folder_tree:
        if not (skip_existing and container._getOb(slugify(kid_name), None)):
            kid_id = addNyFolder(container, title=kid_name,
                                 _send_notifications=False)
        else:
            kid_id = slugify(kid_name)
        kid_folder = container[kid_id]
        folder_map[kid_name] = kid_folder
        report_path(kid_id + '/')

        kid_report_path = lambda p: report_path('%s/%s' % (kid_id, p))
        kid_folder_map = create_folders(kid_folder, kid_tree, kid_report_path,
                                        skip_existing)
        for sub_kid_name, folder in kid_folder_map.iteritems():
            folder_map['%s/%s' % (kid_name, sub_kid_name)] = folder

    return folder_map


class ZipImportTool(Implicit, Item):
    title = "Zip import"

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    def do_import(self, data, REQUEST=None):
        """ """
        if REQUEST and not self.getParentNode().checkAllowedToZipImport():
            raise Unauthorized

        errors = []
        container = self.getParentNode()
        overwrite = REQUEST.get('overwrite')

        # test if file uploaded is Zip archive
        if data.filename.split('.')[-1] != 'zip':
            errors.append("Error while uploading."
                          "You are not importing a Zip archive file.")
        else:
            try:
                folder_tree, zip_files = read_zipfile_contents(data)
            except ValueError, e:
                errors.append(e)
            else:
                created_file_paths = set()
                folder_map = create_folders(container, folder_tree,
                                            created_file_paths.add, overwrite)
                folder_map[''] = container
                for file_path, file_data in zip_files:
                    if '/' in file_path:
                        file_container_path, file_name = file_path.rsplit('/',
                                                                          1)
                    else:
                        file_container_path, file_name = '', file_path

                    file_name = file_name.encode('utf-8')
                    assert file_container_path in folder_map
                    try:
                        file_container = folder_map[file_container_path]
                        if overwrite:
                            filename = slugify(file_name).rsplit('.', 1)[0]
                            if file_container._getOb(filename, None):
                                file_container.manage_delObjects([filename])
                        file_ob_id = add_file(file_container, file_name,
                                              file_data)
                        file_ob = file_container[file_ob_id]
                    except Exception, e:
                        errors.append((
                            (u"Error while creating file ${file_path}: "
                             "${error}"),
                            {'file_path': file_path,
                             'error': force_to_unicode(str(e))}))
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
                self.setSessionInfoTrans([('imported ${path}',
                                           {'path': pth}, ) for pth in
                                          sorted(created_file_paths)])
                return REQUEST.RESPONSE.redirect(container.absolute_url())

            else:
                return []

    index_html = PageTemplateFile('../zpt/zip_import', globals())

InitializeClass(ZipImportTool)


class ZipExportTool(Implicit, Item):
    title = "Zip export"

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    security.declareProtected(PERMISSION_ZIP_EXPORT, 'do_export')

    def do_export(self, REQUEST=None):
        """
        Export the contents of the current folder as a Zip file. Returns an
        open file object. Caller should close the file to free temporary
        disk space.
        """

        errors = None
        if REQUEST is not None:
            errors = []
            if not self.getParentNode().checkPermissionView():
                raise Unauthorized

        my_container = self.getParentNode()
        temp_file = tempfile.TemporaryFile()
        zip_file = ZipFile(temp_file, mode='w', allowZip64=True)

        sm = get_site_manager(my_container)
        builder = RecursiveZipBuilder(zip_file, errors, sm)
        zip_adapter = sm.queryAdapter(my_container, IZipExportObject)
        if zip_adapter is None:
            REQUEST.RESPONSE.notFoundError()
        builder.recurse(my_container, zip_adapter.filename)
        builder.write_index()

        zip_file.close()
        temp_file.seek(0)

        if REQUEST is None:
            return temp_file

        if errors:
            transaction.abort()  # TODO use ZODB savepoints
            self.setSessionErrorsTrans(errors)
            return REQUEST.RESPONSE.redirect(my_container.absolute_url())

        response = REQUEST.RESPONSE
        response.setHeader('content-type', 'application/zip')
        response.setHeader('content-disposition',
                           'attachment; filename=%s.zip' %
                           my_container.getId())
        return stream_response(REQUEST.RESPONSE, temp_file)

InitializeClass(ZipExportTool)


class RecursiveZipBuilder(object):

    def __init__(self, zip_file, error_container, sm):
        self.zip_file = zip_file
        self.error_container = error_container
        self.index_txt = StringIO()
        self.index_txt.write('\t'.join(['Title', 'Type', 'Path']) + '\n')
        self.sm = sm

    def recurse(self, obj, parent_path=''):
        for sub_obj in obj.objectValues():
            try:
                self.add_object_to_zip(sub_obj, parent_path)

            except Exception, e:
                if self.error_container is None:
                    raise
                self.error_container.append(e)

    def write_index(self, filename='index.txt'):
        self.zip_file.writestr(filename, self.index_txt.getvalue())

    def add_object_to_zip(self, obj, parent_path):
        target = self.sm.queryAdapter(obj, IZipExportObject)
        if target is None:
            return

        if target.skip:
            return

        target_path = parent_path + target.filename

        if isinstance(target_path, unicode):
            # we could convert target_path to utf-8, but that would just mask
            # a bug elsewhere; better to raise an exception so we fix the
            # original cause.
            raise ValueError("All paths must be byte strings!")

        data = target.data
        if isinstance(data, unicode):
            data = data.encode('utf-8')

        t = target.timestamp
        if t is None:
            zipinfo = ZipInfo(target_path)

        else:
            date_time = (t.year(), t.month(), t.day(),
                         t.hour(), t.minute(), int(t.second()))
            zipinfo = ZipInfo(target_path, date_time)

        if target.export_as_folder:
            # Set external_attr to 16, otherwise empty folders will not be
            # preserved
            zipinfo.external_attr = 16

        self.zip_file.writestr(zipinfo, data)

        index_row = (target.title.encode('utf-8'),
                     target.meta_label, target_path)
        self.index_txt.write('\t'.join(index_row) + '\n')

        if target.export_as_folder:
            self.recurse(obj, target_path)


class FileIterator(object):
    """
    A file-like object that can be streamed by ZServer.
    Copied from ``ZPublisher.Iterators.filestream_iterator`` and modified.
    """

    if issubclass(IStreamIterator, interface.Interface):
        interface.implements(IStreamIterator)
    else:
        # old-stye zope interface (before ZCA)
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
    RESPONSE.setHeader('Content-Length', fi.__len__())
    return fi
