import sys
from StringIO import StringIO
from zipfile import ZipFile
import datetime

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
