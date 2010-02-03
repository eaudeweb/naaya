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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import transaction
from zope.event import notify
from Products.NaayaCore.events import ZipImportEvent

# Naaya imports
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.Naaya.NyFolder import addNyFolder
try:
    from naaya.content.bfile.bfile_item import addNyBFile as add_bfile
    def add_file(location_obj, id, title, file):
        return add_bfile(location_obj, id=id, title=title,
                           uploaded_file=file, _send_notifications=False)
except ImportError:
    from naaya.content.file.file_item import addNyFile as add_ny_file
    def add_file(location_obj, id, title, file):
        return add_ny_file(location_obj, id=id, title=title,
                           file=file.getvalue(), _send_notifications=False)


class ZipImportTool(Implicit, Item):
    title = "Zip import"

    security = ClassSecurityInfo()
    geo_fields = {}

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
                        add_file(container, id=fname, title='', file=f)
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
