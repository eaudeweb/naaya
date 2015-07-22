"""
DiskFile is a lightweight ZODB object that serves a static file from disk.
From the outside it's like a read-only File object.
"""

import os
from os import path
import sys
import mimetypes
import logging

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.constants import METATYPE_DISKFILE

log = logging.getLogger(__name__)


def remove_excluded(name_list):
    for name in ('.svn',):
        if name in name_list:
            name_list.remove(name)

def list_available_pathspecs():
    out = []
    for allowed_prefix in allowed_path_prefixes:
        root_path = resolve(allowed_prefix)
        for folder_path, folder_names, file_names in os.walk(root_path):
            remove_excluded(folder_names)
            remove_excluded(file_names)
            for name in file_names:
                rel_path = path.join(folder_path, name)[len(root_path):]
                out.append(allowed_prefix + rel_path)
    return out

manage_addDiskFile_html = PageTemplateFile('zpt/disk_file_add', globals())
manage_addDiskFile_html.list_available_pathspecs = list_available_pathspecs

def manage_addDiskFile(self, id='', pathspec='', REQUEST=None):
    """ """
    fs_path = resolve(pathspec)
    if not path.isfile(fs_path):
        raise ValueError("File not found %r (resolved to %r)" %
                         (pathspec, fs_path))

    if id == '':
        id = path.basename(fs_path)

    ob = DiskFile(id, pathspec)
    self._setObject(id, ob)

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


allowed_path_prefixes = set()
def allow_path(prefix):
    assert ':' in prefix
    allowed_path_prefixes.add(prefix)

def resolve(pathspec):
    for allowed_prefix in allowed_path_prefixes:
        if pathspec.startswith(allowed_prefix):
            break
    else:
        raise ValueError("Path not allowed: %r" % pathspec)

    module_name, file_path = pathspec.split(':')
    if '..' in file_path or file_path.startswith('/'):
        raise ValueError("Suspicious path: %r" % file_path)

    if module_name not in sys.modules:
        __import__(module_name)
    module = sys.modules[module_name]
    module_prefix = path.dirname(module.__file__)
    return path.join(module_prefix, file_path)

class DiskFile(SimpleItem):
    meta_type = METATYPE_DISKFILE
    icon = 'misc_/NaayaCore/DiskFile.gif'

    manage_options = ( (
        {'label': 'Contents', 'action': 'manage_main'},
        {'label': 'View', 'action': ''},
    ) + SimpleItem.manage_options)

    security = ClassSecurityInfo()

    @property
    def title(self):
        return self._get_mime_type()

    def __init__(self, id, pathspec):
        self._setId(id)
        self.pathspec = pathspec

    def _get_mime_type(self):
        content_type, content_encoding = mimetypes.guess_type(self.pathspec)
        if content_type is None:
            return  'application/octet-stream'
        else:
            return content_type

    def _get_data(self):
        f = open(resolve(self.pathspec), 'rb')
        data = f.read()
        f.close()
        return data

    security.declarePublic('index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ return the data """
        RESPONSE.setHeader('content-type', self._get_mime_type())
        RESPONSE.write(self._get_data())

    _manage_main = PageTemplateFile('zpt/disk_file_manage', globals())
    security.declareProtected(view_management_screens, 'manage_main')
    def manage_main(self, REQUEST):
        """ """
        options = {
            'fs_path': resolve(self.pathspec),
            'file_data': self._get_data(),
            'mime_type': self._get_mime_type(),
        }
        return self._manage_main(REQUEST, **options)

    def manage_copy_to_database(self, REQUEST):
        """ Copy the file to ZODB for further customization """
        file_id = self.getId()
        parent = self.aq_inner.aq_parent
        parent.manage_delObjects([file_id])

        data_file = open(resolve(self.pathspec), 'rb')
        parent.manage_addFile(id=file_id,
                              file=data_file,
                              content_type=self._get_mime_type())
        data_file.close()
        file_ob = parent[file_id]

        log.info("DiskFile %r uploaded to database by %r",
                 '/'.join(file_ob.getPhysicalPath()),
                 REQUEST.AUTHENTICATED_USER)

        REQUEST.RESPONSE.redirect(file_ob.absolute_url() + '/manage_workspace')
