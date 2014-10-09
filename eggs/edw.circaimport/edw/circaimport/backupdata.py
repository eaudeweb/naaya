import csv
import datetime
import re

from naaya.core.zope2util import relative_object_path, ofs_walk
from Products.Naaya.interfaces import INyFolder

from fixes import fix_exceptions


def sanitize_folder_path(folder_zope_path):
    folder_zope_path = folder_zope_path.replace('/_', '/~')
    folder_zope_path = folder_zope_path.replace('/aq_', '/aq~')
    folder_zope_path = folder_zope_path.replace('/description/',
                                                '/description-folder/')
    folder_zope_path = re.sub(r'/description$', '/description-folder',
                              folder_zope_path)
    return folder_zope_path


def sanitize_id(doc_id):
    if doc_id.startswith('_'):
        doc_id = 'file' + doc_id
    if doc_id.startswith('aq_'):
        doc_id = 'file_' + doc_id
    if doc_id.endswith('__'):
        doc_id = doc_id + 'file'
    if (doc_id.startswith('coverage_') or doc_id.startswith('istranslated_')
            or doc_id.startswith('tags_') or doc_id.startswith(
                'objectkeywords_')):
        doc_id = 'file_' + doc_id
    return doc_id


def convert_index(i, o):
    reader = csv.reader(i, dialect='excel-tab')
    writer = csv.writer(o)
    for line in reader:
        writer.writerow([c.decode('latin-1').encode('utf-8') for c in line])


def read_index(f, warn):
    # reader = csv.DictReader(f, dialect='excel-tab')
    reader = csv.reader(f, dialect='excel-tab')
    names = reader.next()
    n = 0
    for line in reader:
        n += 1
        fix_exceptions(names, line, warn)
        yield dict((names[i], line[i].decode('latin-1'))
                   for i in range(len(names)))


def parse_date(s):
    if not s:
        return datetime.date.today()
    else:
        if '/' in s:
            return datetime.date(*map(int, reversed(s.split('/'))))
        elif '-' in s:
            return datetime.date(*map(int, s.split('-')))


def parse_userid(s):
    if s.endswith('@circa'):
        return str(s[:-len('@circa')]).strip()
    else:
        return str(s).strip()


def walk_backup(index_file, open_backup_file, get_date, actor):
    folders_info = {'root_path': '',
                    'known_folders': {'': None}}

    gen_existing = ofs_walk(actor.context, [INyFolder], [INyFolder])
    for folder in gen_existing:
        rel_path = relative_object_path(folder, actor.context)
        folders_info['known_folders'][rel_path] = None

    def remove_root_path(path):
        assert path.startswith(folders_info['root_path'])
        result = path[len(folders_info['root_path']):]
        if result.startswith('/'):
            result = result[1:]
        return result

    def handle_folder(line):
        title = line.get('TITLE', line['Title'])
        description = line.get('ABSTRACT', line['Abstract'])
        userid = parse_userid(line.get('OWNER', line['Owner']))
        filename = line.get('FILENAME', line['Filename'])
        folder_zip_path = filename[:-1].encode('utf-8')

        # for zope replace starting underscores
        folder_zope_path = sanitize_folder_path(folder_zip_path)

        # use get_date as a backup
        try:
            date = parse_date(line.get('CREATED', line['Created']))
        except ValueError:
            date = get_date(folder_zip_path)

        if '/' in folder_zope_path:
            parent_path, folder_id = folder_zope_path.rsplit('/', 1)
        else:
            parent_path = ''
            folder_id = folder_zope_path

        if len(folders_info['known_folders']) == 1:
            assert folders_info['root_path'] == ''
            if parent_path:
                folders_info['root_path'] = parent_path
            else:
                folders_info['root_path'] = ''

        parent_path = remove_root_path(parent_path)
        folder_zope_path = remove_root_path(folder_zope_path)

        assert parent_path in folders_info['known_folders']

        if folder_zope_path in folders_info['known_folders']:
            created = line.get('CREATED', line['Created'])
            owner = line.get('OWNER', line['Owner'])
            folder_info = folders_info['known_folders'][folder_zope_path]
            try:
                assert created == folder_info.get('CREATED',
                                                  folder_info['Created'])
                assert owner == folder_info.get('OWNER', folder_info['Owner'])
            except:
                pass
            return
        folders_info['known_folders'][folder_zope_path] = line

        actor.folder_entry(parent_path, folder_id,
                           title, description, date, userid)

    def handle_file(line):
        title = line.get('TITLE', line['Title'])
        description = line.get('ABSTRACT', line['Abstract'])
        userid = parse_userid(line.get('OWNER', line['Owner']))
        keywords = line.get('KEYWORDS', line['Keywords'])
        reference = line.get('REFERENCE', line.get('Reference', ''))
        status = line.get('STATUS', line['Status'])
        doc_zip_path = line.get('FILENAME', line['Filename'])

        # for zope replace starting underscores
        doc_zope_path = sanitize_folder_path(doc_zip_path)

        # use get_date as a backup
        try:
            date = parse_date(line.get('UPLOADDATE', line['Uploaddate']))
        except ValueError:
            date = get_date(doc_zip_path)

        doc_split_path = doc_zope_path.split('/')
        doc_filename = doc_split_path[-1].encode('utf-8')
        doc_langver = doc_split_path[-2]
        doc_dpl_name = str(doc_split_path[-3])

        parent_path = '/'.join(doc_split_path[:-3]).encode('utf-8')
        parent_path = remove_root_path(parent_path)
        assert parent_path in folders_info['known_folders']

        doc_id = doc_dpl_name[:-len('.dpl')]
        doc_id = sanitize_id(doc_id)

        full_path = parent_path+'/'+doc_id
        if not doc_langver.startswith('EN_'):
            actor.warn('non-english content: %r at %r' %
                       (doc_langver, full_path))

        ranking = line.get('RANKING', line['Ranking'])
        if ranking != 'Public':
            actor.warn('ranking is %r for %r' %
                       (str(ranking), full_path))

        if description.lower() == 'n/a':
            description = ''
        if status.lower() == 'n/a':
            status = ''
        if reference.lower() == 'n/a':
            reference = ''

        if status not in ('Draft', ''):
            description = (("<p>Status: %s</p>\n" % status)
                           + description)

        if reference:
            description = (("<p>Reference: %s</p>\n" % reference)
                           + description)

        doc_data_file = open_backup_file(doc_zip_path.encode('latin-1'))

        if doc_filename.endswith('.url'):
            url = doc_data_file.read().strip()
            if '\n' in url:
                matched = re.search(r'URL=(.*)', url)
                if matched:
                    url = matched.groups()[0].strip()
            assert (url.startswith('http://') or url.startswith('https://') or
                    url.startswith('ftp://'), "bad url: %r" % url)
            actor.url_entry(parent_path, doc_id,
                            doc_filename, url,
                            title, description, keywords, date, userid)
        else:
            actor.document_entry(parent_path, doc_id,
                                 doc_filename, doc_data_file,
                                 title, description, keywords, date, userid)

    for line in read_index(index_file, actor.warn):
        filename = line.get('FILENAME', line['Filename'])
        if filename.endswith('/'):
            handle_folder(line)
        else:
            handle_file(line)
