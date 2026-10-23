import shutil
from io import BytesIO
from unittest import mock

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.bfile.bfile_item import addNyBFile
from naaya.core import text_extraction
from naaya.core.tests import text_fixtures as fx


def upload(data, filename):
    f = BytesIO(data)
    f.filename = filename
    f.headers = {'content-type': 'application/octet-stream'}
    return f


class BFileSearchTextTest(NaayaTestCase):

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Blob File')

    def add(self, data, filename):
        addNyBFile(self.portal.info, id='bf', title='Blob file', submitted=1,
                   contributor='admin', uploaded_file=upload(data, filename))
        ob = self.portal.info.bf
        ob.approveThis()
        self.portal.recatalogNyObject(ob)
        return ob

    def found(self, word):
        catalog = self.portal.getCatalogTool()
        return [b.getPath().split('/')[-1]
                for b in catalog(PrincipiaSearchSource=word)]

    def test_search_versions_and_languages(self):
        ob = self.add(fx.make_docx('firstword'), 'a.docx')
        self.assertEqual(self.found('firstword'), ['bf'])
        ob._save_file(upload(fx.make_xlsx('newword'), 'b.xlsx'),
                      language='en', contributor='admin')
        ob._save_file(upload(fx.make_odf('frenchword'), 'c.odt'),
                      language='fr', contributor='admin')
        self.portal.recatalogNyObject(ob)
        self.assertEqual(self.found('firstword'), [])
        self.assertEqual(self.found('newword'), ['bf'])
        self.assertEqual(self.found('frenchword'), ['bf'])
        if shutil.which('pdftotext'):
            ob._save_file(upload(fx.make_pdf('pdfword'), 'd.pdf'),
                          language='en', contributor='admin')
            self.portal.recatalogNyObject(ob)
            self.assertEqual(self.found('pdfword'), ['bf'])

    def test_text_cached_per_version(self):
        with mock.patch.object(text_extraction, 'try_extract_text',
                               wraps=text_extraction.try_extract_text) as ex:
            ob = self.add(fx.make_docx('firstword'), 'a.docx')
            self.portal.recatalogNyObject(ob)
            self.portal.recatalogNyObject(ob)
            self.assertEqual(ex.call_count, 1)
            ob._save_file(upload(fx.make_docx('secondword'), 'a.docx'),
                          language='en', contributor='admin')
            self.portal.recatalogNyObject(ob)
            self.portal.recatalogNyObject(ob)
            self.assertEqual(ex.call_count, 2)
        self.assertEqual(self.found('secondword'), ['bf'])

    def test_missing_converter_not_cached(self):
        text_extraction._missing_binaries.clear()
        try:
            with mock.patch('shutil.which', return_value=None):
                ob = self.add(fx.make_pdf('pdfword'), 'a.pdf')
            self.assertIsNone(ob.current_version._search_text)
        finally:
            text_extraction._missing_binaries.clear()
        if shutil.which('pdftotext'):
            self.portal.recatalogNyObject(ob)
            self.assertEqual(self.found('pdfword'), ['bf'])

    def test_broken_file(self):
        ob = self.add(b'PK\x03\x04broken', 'a.docx')
        self.assertEqual(ob.current_version._search_text, '')
        self.assertEqual(self.found('broken'), [])
