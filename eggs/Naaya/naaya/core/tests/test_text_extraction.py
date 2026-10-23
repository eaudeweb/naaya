import shutil
import unittest
from unittest import mock

from naaya.core import text_extraction
from naaya.core.text_extraction import extract_text, try_extract_text
from .text_fixtures import make_docx, make_odf, make_pdf, make_pptx, make_xlsx

HAS_PDFTOTEXT = shutil.which('pdftotext') is not None


class TextExtractionTest(unittest.TestCase):

    def setUp(self):
        text_extraction._missing_binaries.clear()

    @unittest.skipUnless(HAS_PDFTOTEXT, 'pdftotext is not installed')
    def test_pdf(self):
        text = extract_text(make_pdf('Hello pdfword'), 'application/pdf',
                            'a.pdf')
        self.assertEqual(text, 'Hello pdfword')

    def test_office(self):
        self.assertEqual(extract_text(make_docx('docxword'), '', 'a.docx'),
                         'docxword\nsecond')
        self.assertEqual(extract_text(make_xlsx('xlsxword'), '', 'a.xlsx'),
                         'xlsxword\ninline')
        self.assertEqual(extract_text(make_pptx('pptxword'), '', 'a.pptx'),
                         'pptxword')
        self.assertEqual(extract_text(make_odf('odtword'), '', 'a.odt'),
                         'odtword end')
        self.assertEqual(
            extract_text(make_odf('odsword', 'spreadsheet'), '', 'a.ods'),
            'odsword end')

    def test_text_html_rtf(self):
        self.assertEqual(extract_text('caf\xe9 text', 'text/plain', 'a.txt'),
                         'caf\xe9 text')
        self.assertEqual(extract_text(b'caf\xe9', 'text/plain', 'a.txt'),
                         'caf\xe9')
        self.assertEqual(
            extract_text(b'<p>A&amp;B</p><script>x()</script>', 'text/html',
                         'a.html'), 'A&B')
        self.assertEqual(
            extract_text(b"{\\rtf1{\\fonttbl{\\f0 Arial;}}caf\\'e9\\par x}",
                         'application/rtf', 'a.rtf'), 'caf\xe9\nx')

    def test_unsupported_and_limits(self):
        self.assertEqual(extract_text(b'\x89PNG....', 'image/png', 'a.png'),
                         '')
        with mock.patch.object(text_extraction, 'MAX_FILE_SIZE', 4):
            self.assertEqual(extract_text(b'too long', 'text/plain'), '')
        with mock.patch.object(text_extraction, 'MAX_TEXT_LENGTH', 3):
            self.assertEqual(extract_text(b'abcdef', 'text/plain'), 'abc')

    def test_broken_file(self):
        with self.assertLogs(text_extraction.log, 'WARNING'):
            self.assertEqual(extract_text(b'PK\x03\x04broken', '', 'a.docx'),
                             '')
        if HAS_PDFTOTEXT:
            with self.assertLogs(text_extraction.log, 'WARNING'):
                self.assertEqual(
                    extract_text(b'%PDF-1.4 garbage', 'application/pdf'), '')

    def test_missing_binary(self):
        with mock.patch('shutil.which', return_value=None), \
                self.assertLogs(text_extraction.log, 'WARNING') as logs:
            pdf = make_pdf('x')
            self.assertIsNone(try_extract_text(pdf, 'application/pdf'))
            self.assertIsNone(try_extract_text(pdf, 'application/pdf'))
            self.assertEqual(extract_text(pdf, 'application/pdf'), '')
            self.assertIsNone(try_extract_text(b'\xd0\xcf\x11\xe0', '',
                                               'old.doc'))
        # one warning per missing binary
        self.assertEqual(len(logs.output), 2)
