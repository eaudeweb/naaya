import datetime
import io
import unittest

from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from edw.circaimport import backupdata
from edw.circaimport.fixes import fix_exceptions

INDEX_HEADER = ['FILENAME', 'TITLE', 'ABSTRACT', 'OWNER', 'CREATED',
                'UPLOADDATE', 'KEYWORDS', 'REFERENCE', 'STATUS', 'RANKING']


def make_index(rows):
    """Build a tab separated CIRCA index as a text stream."""
    lines = ['\t'.join(INDEX_HEADER)] + ['\t'.join(row) for row in rows]
    return io.StringIO('\r\n'.join(lines) + '\r\n', newline='')


INDEX_ROWS = [
    ['lib/docs/', 'Documents', 'Main folder', 'alice@circa', '02/03/2009',
     '', '', '', '', ''],
    ['lib/docs/_private/', 'Private', '', 'bob@circa', '', '', '', '', '',
     ''],
    ['lib/docs/report.dpl/EN_1/report.pdf', 'Report', 'n/a', 'alice@circa',
     '', '15/06/2010', 'water, air', 'REF-1', 'Final', 'Public'],
    ['lib/docs/caf\xe9.dpl/FR_1/caf\xe9.txt', 'Caf\xe9', 'Menu', 'bob@circa',
     '', '2011-01-05', '', 'n/a', 'Draft', 'Restricted'],
    ['lib/docs/link.dpl/EN_1/link.url', 'Link', '', 'alice@circa', '',
     '01/01/2012', '', '', 'n/a', 'Public'],
]

URL_DATA = b'[InternetShortcut]\r\nURL=http://example.com/page\r\n'


class RecordingActor(object):
    def __init__(self, context):
        self.context = context
        self.calls = []
        self.warnings = []

    def folder_entry(self, *args):
        self.calls.append(('folder',) + args)

    def document_entry(self, *args):
        self.calls.append(('document',) + args)

    def url_entry(self, *args):
        self.calls.append(('url',) + args)

    def warn(self, msg):
        self.warnings.append(msg)


class HelpersTest(unittest.TestCase):

    def test_sanitize_folder_path(self):
        f = backupdata.sanitize_folder_path
        self.assertEqual(f('lib/_hidden/x'), 'lib/~hidden/x')
        self.assertEqual(f('lib/aq_parent'), 'lib/aq~parent')
        self.assertEqual(f('lib/description/x'), 'lib/description-folder/x')
        self.assertEqual(f('lib/description'), 'lib/description-folder')
        self.assertEqual(f('lib/plain'), 'lib/plain')

    def test_sanitize_id(self):
        f = backupdata.sanitize_id
        self.assertEqual(f('_doc'), 'file_doc')
        self.assertEqual(f('aq_doc'), 'file_aq_doc')
        self.assertEqual(f('doc__'), 'doc__file')
        self.assertEqual(f('tags_x'), 'file_tags_x')
        self.assertEqual(f('coverage_x'), 'file_coverage_x')
        self.assertEqual(f('report'), 'report')

    def test_parse_date(self):
        f = backupdata.parse_date
        self.assertEqual(f('02/03/2009'), datetime.date(2009, 3, 2))
        self.assertEqual(f('2011-01-05'), datetime.date(2011, 1, 5))
        self.assertEqual(f(''), datetime.date.today())
        self.assertRaises(ValueError, f, '00/00/0000')

    def test_parse_userid(self):
        self.assertEqual(backupdata.parse_userid('alice@circa'), 'alice')
        self.assertEqual(backupdata.parse_userid(' bob '), 'bob')

    def test_read_index(self):
        warnings = []
        lines = list(backupdata.read_index(make_index(INDEX_ROWS[:1]),
                                           warnings.append))
        self.assertEqual(lines, [dict(zip(INDEX_HEADER, INDEX_ROWS[0]))])
        self.assertEqual(warnings, [])

    def test_convert_index(self):
        out = io.StringIO()
        backupdata.convert_index(
            io.StringIO('A\tB\r\nx y\tcaf\xe9\r\n', newline=''), out)
        self.assertEqual(out.getvalue(), 'A,B\r\nx y,caf\xe9\r\n')


class WalkBackupTest(NaayaTestCase):

    def afterSetUp(self):
        addNyFolder(self.portal, 'importroot', title='Import root')
        self.context = self.portal['importroot']

    def walk(self, rows):
        actor = RecordingActor(self.context)
        opened = []

        def open_backup_file(name):
            opened.append(name)
            if name.endswith('.url'):
                return io.BytesIO(URL_DATA)
            return io.BytesIO(b'data')

        backupdata.walk_backup(make_index(rows), open_backup_file,
                               lambda name: datetime.date(2000, 1, 1), actor)
        return actor, opened

    def test_walk_backup(self):
        actor, opened = self.walk(INDEX_ROWS)
        folders = [c for c in actor.calls if c[0] == 'folder']
        self.assertEqual(folders, [
            ('folder', '', 'docs', 'Documents', 'Main folder',
             datetime.date(2009, 3, 2), 'alice'),
            ('folder', 'docs', '~private', 'Private', '',
             datetime.date.today(), 'bob'),
        ])

        documents = [c for c in actor.calls if c[0] == 'document']
        self.assertEqual(len(documents), 2)
        (kind, parent, ob_id, filename, data_file, title, description,
         keywords, date, userid, lang) = documents[0]
        self.assertEqual((parent, ob_id, filename, title), (
            'docs', 'report', 'report.pdf', 'Report'))
        self.assertEqual(description, '<p>Reference: REF-1</p>\n'
                                      '<p>Status: Final</p>\n')
        self.assertEqual(keywords, 'water, air')
        self.assertEqual(date, datetime.date(2010, 6, 15))
        self.assertEqual((userid, lang), ('alice', 'en'))
        self.assertEqual(data_file.read(), b'data')

        (kind, parent, ob_id, filename, data_file, title, description,
         keywords, date, userid, lang) = documents[1]
        self.assertEqual((parent, ob_id, filename, title, description), (
            'docs', 'caf\xe9', 'caf\xe9.txt', 'Caf\xe9', 'Menu'))
        self.assertEqual((date, userid), (datetime.date(2011, 1, 5), 'bob'))
        self.assertEqual(lang, 'en')

        urls = [c for c in actor.calls if c[0] == 'url']
        self.assertEqual(urls, [
            ('url', 'docs', 'link', 'link.url', 'http://example.com/page',
             'Link', '', '', datetime.date(2012, 1, 1), 'alice'),
        ])

        self.assertEqual(opened, [row[0] for row in INDEX_ROWS[2:]])
        self.assertEqual(actor.warnings, [
            "non-english (fr) content: 'FR_1' at 'docs/caf\xe9'. "
            "Will be imported as English",
            "ranking is 'Restricted' for 'docs/caf\xe9'",
        ])

    def test_walk_backup_date_fallback(self):
        rows = [['lib/docs/', 'Documents', '', 'alice@circa', '00/00/0000',
                 '', '', '', '', '']]
        actor, opened = self.walk(rows)
        self.assertEqual(actor.calls[0][5], datetime.date(2000, 1, 1))

    def test_walk_backup_bad_url(self):
        rows = [INDEX_ROWS[0], INDEX_ROWS[4]]
        actor = RecordingActor(self.context)
        with self.assertRaises(AssertionError):
            backupdata.walk_backup(make_index(rows),
                                   lambda name: io.BytesIO(b'not a url'),
                                   None, actor)


FIX_NAMES = ['FILENAME', 'TITLE', 'ABSTRACT', 'OWNER', 'CREATED', 'UPLOADDATE',
             'ISSUEDATE', 'KEYWORDS', 'REFERENCE', 'STATUS', 'RANKING']


class FixExceptionsTest(unittest.TestCase):
    """ fix_exceptions repairs malformed CIRCA index lines in place """

    def fix(self, line, names=FIX_NAMES):
        warnings = []
        result = fix_exceptions(names, line, warnings.append)
        return result, warnings

    def row(self, **values):
        line = ['f.txt', 'Title', 'Abstract', 'bob@circa', '01/01/2009',
                '02/02/2009', '', 'kw', 'ref', 'Draft', 'Public']
        for name, value in values.items():
            line[FIX_NAMES.index(name)] = value
        return line

    def test_well_formed(self):
        line = self.row()
        self.assertEqual(self.fix(line), (None, []))
        self.assertEqual(line, self.row())

    def test_short_line(self):
        names = FIX_NAMES + ['OVERWRITE'] + ['X%d' % i for i in range(7)]
        line = ['lib/a/report.pdf', ''] + ['v'] * 12
        result, warnings = self.fix(line, names)
        self.assertEqual(len(line), 19)
        self.assertEqual(line[1], 'report.pdf')
        self.assertEqual(line[11:16], [''] * 5)
        self.assertEqual(len(warnings), 1)
        self.assertTrue(warnings[0].startswith('Very short line'))

    def test_shifted_circa_owner(self):
        # the issue date column is duplicated, which shifts the next columns
        line = self.row(UPLOADDATE='@circa', KEYWORDS='00/00/0000',
                        CREATED='00/00/0000')
        line.insert(FIX_NAMES.index('ISSUEDATE'), 'extra')
        result, warnings = self.fix(line)
        self.assertEqual(len(line), len(FIX_NAMES))
        values = dict(zip(FIX_NAMES, line))
        self.assertEqual((values['ISSUEDATE'], values['UPLOADDATE'],
                          values['OWNER'], values['RANKING']),
                         ('', '', '', 'Public'))
        self.assertEqual(warnings, [])

    def test_missing_owner_and_date(self):
        folder = self.row(FILENAME='lib/docs/', OWNER='', UPLOADDATE='') + ['x']
        self.assertEqual(self.fix(folder), (None, []))
        document = self.row(OWNER='', UPLOADDATE='') + ['x']
        result, warnings = self.fix(document)
        self.assertEqual(len(warnings), 1)
        self.assertTrue(warnings[0].startswith('WEIRD LINE'))

    def test_empty_title(self):
        line = ['f.txt', ' ', 'Public'] + self.row()[2:]
        self.assertEqual(self.fix(line), (True, []))
        self.assertEqual(line, ['f.txt', 'Public'] + self.row()[2:])

    def test_extra_column_before_owner(self):
        line = self.row(CREATED='bob@circa')
        line.insert(1, 'extra')
        self.assertEqual(self.fix(line), (True, []))
        self.assertEqual(len(line), len(FIX_NAMES))
        self.assertEqual(line[1], 'Title')

    def test_tabs_in_abstract(self):
        line = self.row()
        line[2:3] = ['part 1', 'part 2', 'part 3']
        self.assertEqual(self.fix(line), (None, []))
        self.assertEqual(line, self.row(ABSTRACT='part 1\tpart 2\tpart 3'))

    def test_busted_line(self):
        names = ['FILENAME', 'TITLE', 'OWNER', 'UPLOADDATE']
        self.assertRaises(AssertionError, fix_exceptions, names,
                          ['a', 'b', 'c', 'd', 'e'], None)


class ConsoleScriptsTest(unittest.TestCase):
    """ the tsv2csv console script reads bytes from stdin """

    def run_script(self, func, argv, data):
        from unittest import mock
        stdin = io.TextIOWrapper(io.BytesIO(data))
        stdout = io.StringIO()
        with mock.patch('sys.argv', ['script'] + argv), \
                mock.patch('sys.stdin', stdin), \
                mock.patch('sys.stdout', stdout):
            func()
        return stdout.getvalue()

    def test_tsv2csv(self):
        import edw.circaimport
        out = self.run_script(edw.circaimport.tsv2csv, [],
                              b'A\tB\r\nx\tcaf\xe9\r\n')
        self.assertEqual(out, 'A,B\r\nx,caf\xe9\r\n')
