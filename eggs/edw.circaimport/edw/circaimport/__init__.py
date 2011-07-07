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

def tsv2csv():
    backupdata.convert_index(sys.stdin, sys.stdout)
