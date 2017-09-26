import sys
from StringIO import StringIO
from zipfile import ZipFile

import backupdata

def demo():
    from actors import DemoActor
    actor = DemoActor()

    if len(sys.argv) > 1 and sys.argv[1] == '-i':
        index_file = sys.stdin
        def open_backup_file(name):
            return StringIO('http://in-case-this-is-a-url')

    else:
        zf = ZipFile(sys.stdin)
        index_file = StringIO(zf.read('index.txt'))
        def open_backup_file(name):
            return StringIO(zf.read(name))

    backupdata.walk_backup(index_file, open_backup_file, actor)

    actor.finished()

def work_in_zope(context, name, root_path):
    """
    Call this method from a Zope ExternalMethod. It assumes a local
    folder that has CIRCA-exported Zip files (using the "save" method,
    not "download"). Call it from the Web and pass in a "name" parameter
    which is the filename you want to import. Make sure you call the
    external method in the context of a folder where you want the files
    to be imported.

    Example external method code::
        from edw.circaimport import work_in_zope
        def do_import(self, REQUEST):
            name = REQUEST.get('name')
            return work_in_zope(self, name, '/path/to/downloads/folder')
    """
    from actors import ZopeActor
    assert '/' not in name and name != '..'
    zip_path = root_path + '/' + name
    zip_fs_file = open(zip_path, 'rb')
    report = StringIO()

    zf = ZipFile(zip_fs_file)
    index_file = StringIO(zf.read('index.txt'))
    actor = ZopeActor(context, report)
    def open_backup_file(name):
        return StringIO(zf.read(name))

    backupdata.walk_backup(index_file, open_backup_file, actor)

    actor.finished()

    zip_fs_file.close()
    return report.getvalue()

def tsv2csv():
    backupdata.convert_index(sys.stdin, sys.stdout)
