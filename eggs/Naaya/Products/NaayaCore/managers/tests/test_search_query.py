from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.managers.catalog_tool import plain_words_query
from naaya.content.document.document_item import addNyDocument


class SearchOperatorsTest(NaayaTestCase):
    """ searches with and/or/not or parentheses in the text """

    def test_plain_words_query(self):
        self.assertEqual(plain_words_query('salt AND (pepper or Not)'),
                         'salt pepper')
        self.assertEqual(plain_words_query('(and)'), '')

    def test_site_search(self):
        addNyDocument(self.portal.info, id='doc1', title='Salt and pepper',
                      body='salt pepper', submitted=1, contributor='admin')
        self.portal.info.doc1.approveThis()
        self.portal.recatalogNyObject(self.portal.info.doc1)

        def found(q):
            return [ob.getId() for ob in
                    self.portal.query_objects_ex(q=q, lang='en')]
        self.assertIn('doc1', found('salt and pepper'))
        self.assertIn('doc1', found('(salt'))
        self.assertIn('doc1', found('pepper not'))
        self.assertEqual(found('and or ('), [])

    def test_map_search(self):
        self.portal.manage_install_pluggableitem('Naaya GeoPoint')
        pt_id = self.portal.info.addNyGeoPoint(
            id='pt', title='Salt mine',
            **{'geo_location.lat': '45', 'geo_location.lon': '25'})
        pt = self.portal.info._getOb(pt_id)
        pt.approveThis()
        self.portal.portal_map.recatalogNyObject(pt)
        found = self.portal.portal_map.search_geo_objects(
            query='salt and (mine', geo_types=[''])
        self.assertEqual([ob.getId() for ob in found], [pt_id])

    def test_text_file_body_search(self):
        from naaya.content.file.file_item import addNyFile
        file_id = addNyFile(self.portal.info, id='notes', title='Notes',
                            submitted=1, contributor='admin')
        ob = self.portal.info._getOb(file_id)
        ob.update_data(b'unusualword in the text', 'text/plain')
        ob.approveThis()
        self.portal.recatalogNyObject(ob)
        found = [o.getId() for o in
                 self.portal.query_objects_ex(q='unusualword')]
        self.assertEqual(found, [file_id])

    def add_file(self, file_id, data, content_type, filename):
        from naaya.content.file.file_item import addNyFile
        file_id = addNyFile(self.portal.info, id=file_id, title=file_id,
                            submitted=1, contributor='admin')
        ob = self.portal.info._getOb(file_id)
        ob.update_data(data, content_type, filename=filename)
        ob.approveThis()
        self.portal.recatalogNyObject(ob)
        return ob

    def found(self, word):
        catalog = self.portal.getCatalogTool()
        return [b.getPath().split('/')[-1]
                for b in catalog(PrincipiaSearchSource=word)]

    def test_office_and_pdf_file_search(self):
        import shutil
        from naaya.core.tests import text_fixtures as fx
        self.add_file('report', fx.make_docx('docxword'), 'application/'
                      'vnd.openxmlformats-officedocument.wordprocessingml.'
                      'document', 'report.docx')
        self.add_file('sheet', fx.make_odf('odsword', 'spreadsheet'),
                      'application/vnd.oasis.opendocument.spreadsheet',
                      'sheet.ods')
        self.assertEqual(self.found('docxword'), ['report'])
        self.assertEqual(self.found('odsword'), ['sheet'])
        if shutil.which('pdftotext'):
            self.add_file('paper', fx.make_pdf('pdfword here'),
                          'application/pdf', 'paper.pdf')
            self.assertEqual(self.found('pdfword'), ['paper'])

    def test_file_text_cached(self):
        from unittest import mock
        from naaya.core import text_extraction
        from naaya.core.tests import text_fixtures as fx
        with mock.patch.object(text_extraction, 'try_extract_text',
                               wraps=text_extraction.try_extract_text) as ex:
            ob = self.add_file('report', fx.make_docx('firstword'), '',
                               'report.docx')
            self.portal.recatalogNyObject(ob)
            self.portal.recatalogNyObject(ob)
            self.assertEqual(ex.call_count, 1)
            ob.update_data(fx.make_docx('secondword'), '',
                           filename='report.docx')
            self.portal.recatalogNyObject(ob)
            self.portal.recatalogNyObject(ob)
            self.assertEqual(ex.call_count, 2)
        self.assertEqual(self.found('firstword'), [])
        self.assertEqual(self.found('secondword'), ['report'])
