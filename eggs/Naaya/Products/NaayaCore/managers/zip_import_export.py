# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web

# Python imports
from zipfile import ZipFile
from StringIO import StringIO
from copy import copy

# Zope imports
from Acquisition import Implicit
from OFS.SimpleItem import Item
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import transaction
from zope.event import notify
from Products.NaayaCore.events import ZipImportEvent
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
from DateTime import DateTime

# Naaya imports
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.NyFolder import NyFolder
from naaya.content.file.interfaces import INyFile
from naaya.content.document.interfaces import INyDocument
from naaya.content.contact.interfaces import INyContact
from naaya.content.event.interfaces import INyEvent
from naaya.content.news.interfaces import INyNews
from naaya.content.story.interfaces import INyStory
try:
    from naaya.content.bfile.bfile_item import addNyBFile as add_bfile
    def add_file(location_obj, id, file):
        return add_bfile(location_obj, id=id, title='',
                           uploaded_file=file, _send_notifications=False)
except ImportError:
    from naaya.content.file.file_item import addNyFile as add_ny_file
    def add_file(location_obj, id, file):
        return add_ny_file(location_obj, id=id, title=id,
                           file=file.getvalue(), _send_notifications=False)


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

        try:
            zip = ZipFile(data)
        except Exception, e:
            errors.append(str(e))

        if not errors:
            sorted_namelist = self.sorted_nlist(zip.namelist())
            root = self.make_folder_named_after_zip(data)

            for name in sorted_namelist:
                nlist = name.split('/')[:-1]

                try:
                    if self.is_folder(name):
                        self.make_folder_structure(copy(nlist), root)

                    elif self.is_file(name):
                        f_content = zip.read(name)
                        fname = name.split('/')[-1]
                        f = self.make_file_object_from_string(f_content, fname)
                        container = self.get_folder(copy(nlist), root)
                        add_file(container, id=fname, file=f)
                except Exception, e:
                    errors.append(str(e))

        my_container = self.getParentNode()

        if REQUEST is not None:
            if errors:
                transaction.abort()
                self.setSessionErrors(errors)
                return self.index_html(REQUEST)
            else:
                self.setSessionInfo(['Zip archive successfully imported'])
                notify(ZipImportEvent(my_container, root, sorted_namelist))
                return REQUEST.RESPONSE.redirect(my_container.absolute_url())
        else:
            if not errors:
                notify(ZipImportEvent(my_container, root, sorted_namelist))
            return errors


    def is_file(self, name):
        return not name.endswith('/')

    def is_folder(self, name):
        return name.endswith('/')

    def get_folder(self, nlist, root):
        if len(nlist) == 0:
            return root
        folder = root[nlist.pop(0)]
        return self.get_folder(nlist, folder)

    def make_folder_structure(self, nlist, root):
        if len(nlist) == 0:
            return
        new = nlist.pop(0)
        if not root._getOb(new, None):
            addNyFolder(root, id=new, title='', _send_notifications=False)
        root = root[new]
        self.make_folder_structure(nlist, root)

    def make_folder_named_after_zip(self, data):
        location_obj = self.getParentNode()
        filename = data.filename.split('.')[0]
        folder_id = addNyFolder(location_obj, id=filename, title='',
                                _send_notifications=False)
        return location_obj[folder_id]

    def make_file_object_from_string(self, string, fname):
        f = StringIO(string)
        setattr(f, 'filename', fname)
        return f

    def sorted_nlist(self, nlist):
        files, folders = [], []
        for x in nlist:
            if x.startswith('_'):
                continue
            if self.is_file(x):
                files.append(x)
            else:
                folders.append(x)
        return folders + files

    def has_many_objects_in_root(self, sorted_namelist):
        result = []
        for x in sorted_namelist:
            if x.endswith('/'):
                result.append(x[:-1])
            else:
                result.append(x)

        if len([x for x in result if '/' not in x]) > 1:
            return True

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'index_html')
    index_html = PageTemplateFile('../zpt/zip_import', globals())

InitializeClass(ZipImportTool)


class ZipExportTool(Implicit, Item):
    title = "Zip export"

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    security.declareProtected(view, 'do_export')
    def do_export(self, REQUEST=None):
        """ """
        if REQUEST and not self.getParentNode().checkPermissionPublishObjects():
            raise Unauthorized

        errors = []

        my_container = self.getParentNode()

        objects_to_archive = self.gather_objects(my_container)

        file_like_object = StringIO()
        zip_file = ZipFile(file_like_object, 'w')
        archive_files = []
        try:
            for obj in objects_to_archive:
                added_path = None
                if self.user_has_view_permission(obj):
                    added_path = self.add_object_to_zip(obj, zip_file)
                if added_path:
                    archive_files.append((obj.title_or_id(),
                                          getattr(obj, 'meta_label',
                                                  obj.meta_type),
                                          added_path))

            self.add_index(zip_file, archive_files)
            zip_file.close()
        except Exception, e:
            errors.append(str(e))

        if REQUEST is not None:
            if errors:
                transaction.abort()
                self.setSessionErrors(errors)
            else:
                response = REQUEST.RESPONSE
                response.setHeader('content-type', 'application/zip')
                response.setHeader('content-disposition',
                                   'attachment; filename=%s.zip' %
                                   my_container.getId())
                return file_like_object.getvalue()
            return REQUEST.RESPONSE.redirect(my_container.absolute_url())
        else:
            if not errors:
                return file_like_object
            return errors

    def gather_objects(self, container):
        objects = []
        for obj in container.objectValues():
            objects.append(obj)
            if isinstance(obj, NyFolder):
                objects.extend(self.gather_objects(obj))
        return objects

    def add_object_to_zip(self, obj, zip_file):
        def file_has_no_extension(path):
            return not len(path.split('/')[-1].split('.')) > 1
        zip_path = self.get_zip_path(obj)
        if isinstance(zip_path, unicode):
            zip_path = zip_path.encode('utf-8')
        object_zip_data, object_zip_filename = self.get_zip_content(obj)
        if isinstance(obj, NyFolder):
            object_zip_data = 'Naaya Folder'
        else:
            if file_has_no_extension(zip_path):
                zip_path = '%s.%s' % (zip_path,
                                      object_zip_filename.split('.')[-1])
        if object_zip_data:
            if isinstance(object_zip_data, unicode):
                object_zip_data = object_zip_data.encode('utf-8')
            zip_file.writestr(zip_path, object_zip_data)
            return zip_path

    def add_index(self, zip_file, archive_files):
        index_content = [('Title', 'Type', 'Path')]
        index_content.extend(archive_files)
        index_content = ['\t'.join(row).encode('utf-8') for \
                         row in index_content]
        index_content = '\n'.join(index_content)
        zip_file.writestr('index.txt', index_content)

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

    def get_zip_content(self, obj):
        try:
            export_adapter = IZipExportObject(obj)
            return export_adapter()
        except TypeError:
            return ('', '')

    def user_has_view_permission(self, obj):
        return obj.checkPermissionView()

InitializeClass(ZipExportTool)

class IZipExportObject(Interface):
    def __call__():
        """Return data (as `str`) and filename, as a tuple
        """

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
        filename = self.context.utCleanupId(filename)
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

