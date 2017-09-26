import csv
import datetime

from fixes import fix_exceptions

def convert_index(i, o):
    reader = csv.reader(i, dialect='excel-tab')
    writer = csv.writer(o)
    for line in reader:
        writer.writerow([c.decode('latin-1').encode('utf-8') for c in line])

def read_index(f, warn):
    #reader = csv.DictReader(f, dialect='excel-tab')
    reader = csv.reader(f, dialect='excel-tab')
    names = reader.next()
    n = 0
    for line in reader:
        n += 1
        print n
        fix_exceptions(names, line, warn)
        yield dict( (names[i], line[i].decode('latin-1'))
                    for i in range(len(names)) )

def parse_date(s):
    if not s:
        return datetime.date.today()
    else:
        return datetime.date(*map(int, reversed(s.split('/'))))

def parse_userid(s):
    if s.endswith('@circa'):
        s = str(s[:-len('@circa')])
    assert s
    return s

def walk_backup(index_file, open_backup_file, actor):
    known_folders = set()

    def handle_folder(line):
        title = line['TITLE']
        description = line['ABSTRACT']
        date = parse_date(line['CREATED'])
        userid = parse_userid(line['OWNER'])
        folder_path =  line['FILENAME'][:-1].encode('utf-8')
        assert line['LANGUAGE'] == 'EN'

        if '/' in folder_path:
            parent_path, folder_id = folder_path.rsplit('/', 1)
            assert parent_path in known_folders
        else:
            parent_path = None
            folder_id = folder_path
        known_folders.add(folder_path)

        actor.folder_entry(parent_path, folder_id,
                           title, description, date, userid)

    def handle_file(line):
        title = line['TITLE']
        description = line['ABSTRACT']
        date = parse_date(line['UPLOADDATE'])
        userid = parse_userid(line['OWNER'])
        doc_zip_path = line['FILENAME']
        doc_split_path = doc_zip_path.split('/')
        doc_filename = doc_split_path[-1].encode('utf-8')
        doc_langver = doc_split_path[-2]
        doc_dpl_name = str(doc_split_path[-3])
        parent_path = '/'.join(doc_split_path[:-3]).encode('utf-8')
        doc_id = doc_dpl_name[:-len('.dpl')]
        if doc_id.startswith('_'):
            doc_id = 'file' + doc_id
        if line['RANKING'] != 'Public':
            actor.warn('RANKING != PUBLIC: %r' % line)

        assert parent_path in known_folders

        doc_data_file = open_backup_file(doc_zip_path.encode('latin-1'))

        if doc_filename.endswith('.url'):
            url = doc_data_file.read()
            assert url.startswith('http://'), "bad url: %r" % url
            actor.url_entry(parent_path, doc_id,
                            doc_filename, url,
                            title, description, date, userid)
        else:
            actor.document_entry(parent_path, doc_id,
                                 doc_filename, doc_data_file,
                                 title, description, date, userid)

    for line in read_index(index_file, actor.warn):
        filename = line['FILENAME']
        if filename.endswith('/'):
            handle_folder(line)
        else:
            handle_file(line)
