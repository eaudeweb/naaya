import sys
import io
from zipfile import ZipFile
import Zope2
from zExceptions import BadRequest, NotFound
from naaya.core.zope2util import get_site_manager
from Products.NaayaCore.managers.zip_import_export import RecursiveZipBuilder
from Products.NaayaCore.managers.interfaces import IZipExportObject

from . import backupdata


def tsv2csv():
    backupdata.convert_index(
        io.TextIOWrapper(sys.stdin.buffer, encoding='latin-1', newline=''),
        sys.stdout)


def do_export():
    """
    Export the contents of container found at the path found in args as a zip
    file in the location found as last argument.
    """
    save_path = sys.argv[-1]
    site_path = sys.argv[-2]
    if 'library' not in site_path:
        raise BadRequest("library not in requested path")
    zipname = site_path.replace('/', '#')
    if zipname.startswith('#'):
        zipname = zipname[1:]
    my_container = Zope2.app().unrestrictedTraverse(site_path)
    catalog = my_container.getSite().getCatalogTool()
    folders = len(catalog({'path': 'eea-eionet-day/library/',
                           'meta_type': 'Naaya Folder'}))
    files = len(catalog({'path': 'eea-eionet-day/library/',
                         'meta_type': 'Naaya Blob File'}))
    meetings = len(catalog({'path': 'eea-eionet-day/library/',
                           'meta_type': 'Naaya Meeting'}))
    count = "Folders: %s\nFiles: %s\nMeetings: %s" % (folders, files,
                                                      meetings)
    # zip_path = my_container.getId() + '/'
    export_file = open(save_path + zipname + '.zip', 'w+b')
    zip_file = ZipFile(export_file, mode='w', allowZip64=True)
    errors = []
    sm = get_site_manager(my_container)
    builder = RecursiveZipBuilder(zip_file, errors, sm)
    zip_adapter = sm.queryAdapter(my_container, IZipExportObject)
    if zip_adapter is None:
        raise NotFound("The object has no zip adapter")
    builder.recurse(my_container, zip_adapter.filename)
    builder.write_index()
    builder.zip_file.writestr('count.txt' , count)
    zip_file.close()
