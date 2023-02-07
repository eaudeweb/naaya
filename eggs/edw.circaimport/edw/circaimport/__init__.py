import sys
from StringIO import StringIO
from zipfile import ZipFile
import datetime
import Zope2
from zExceptions import BadRequest, NotFound
from naaya.core.zope2util import get_site_manager
from Products.NaayaCore.managers.zip_import_export import RecursiveZipBuilder
from Products.NaayaCore.managers.interfaces import IZipExportObject

import backupdata


def demo():
    from actors import DemoActor
    actor = DemoActor()

    if len(sys.argv) > 1 and sys.argv[1] == '-i':
        index_file = sys.stdin

        def open_backup_file(name):
            return StringIO('http://in-case-this-is-a-url')

        def get_date(name):
            return datetime.date.today()

    else:
        zf = ZipFile(sys.stdin)
        index_file = StringIO(zf.read('index.txt'))

        def open_backup_file(name):
            return StringIO(zf.read(name))

        def get_date(name):
            info = zf.getinfo(name)
            return datetime.date(*info.date_time[0:3])

    backupdata.walk_backup(index_file, open_backup_file, get_date, actor)

    actor.finished()


def tsv2csv():
    backupdata.convert_index(sys.stdin, sys.stdout)


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

    zip_file.close()
