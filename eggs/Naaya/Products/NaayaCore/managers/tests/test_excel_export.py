import datetime
import unittest
from io import BytesIO

import openpyxl

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from naaya.core.zope2util import XLSX_CONTENT_TYPE


class ExcelExportTestCase(NaayaFunctionalTestCase):
    """ Excel export of a folder, produced as .xlsx """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.news.news_item import addNyNews
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyNews(self.portal.myfolder, id='mynews', submitted=1, contributor='contributor', title='The News')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_excel_export(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/csv_export/export?meta_type=Naaya%20News&file_type=Excel&as_attachment=True')
        response = self.browser.result
        self.assertEqual(response.headers['content-type'], XLSX_CONTENT_TYPE)
        self.assertTrue(response.headers['content-disposition']
                        .strip('"').endswith('.xlsx'))
        ws = openpyxl.load_workbook(BytesIO(response.content)).worksheets[0]
        header = [c.value for c in ws[1]]
        self.assertEqual(header[:2], ['ID', 'Title'])
        self.assertTrue(ws['A1'].font.b)
        row = [c.value for c in ws[2]]
        self.assertEqual(row[0], 'mynews')
        self.assertEqual(row[1], 'The News')


class GenerateExcelTestCase(unittest.TestCase):
    """ generate_excel writes a bold header, the rows and dd/mm/yyyy dates """

    def test_layout(self):
        from Products.NaayaCore.managers.import_export import generate_excel
        data = generate_excel(['ID', 'Title', 'Date'],
                              [['a', '=not a formula', '31/01/2020'],
                               ['b', 'caf\xe9', '']])
        wb = openpyxl.load_workbook(BytesIO(data))
        self.assertEqual(wb.sheetnames, ['Sheet 1'])
        ws = wb.worksheets[0]
        self.assertEqual([c.value for c in ws[1]], ['ID', 'Title', 'Date'])
        self.assertTrue(all(c.font.b for c in ws[1]))
        self.assertEqual(ws['B2'].value, '=not a formula')
        self.assertEqual(ws['B2'].data_type, 's')
        self.assertEqual(ws['C2'].value, datetime.datetime(2020, 1, 31))
        self.assertEqual(ws['C2'].number_format, 'dd/mm/yyyy')
        self.assertEqual(ws['B3'].value, 'caf\xe9')
        self.assertFalse(ws['A2'].font.b)

    def test_template_without_rows(self):
        from Products.NaayaCore.managers.import_export import generate_excel
        data = generate_excel(['ID', 'Title'], [[]])
        ws = openpyxl.load_workbook(BytesIO(data)).worksheets[0]
        self.assertEqual([c.value for c in ws[1]], ['ID', 'Title'])
