import re
from unittest import TestSuite, makeSuite
from StringIO import StringIO
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
try:
    import xlrd
    import xlwt
    excel_available = True
except:
    excel_available = False

class make_id_TestCase(NaayaFunctionalTestCase):
    """ TestCase for the make_id function """

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
        if excel_available:
            self.browser.go('http://localhost/portal/myfolder/csv_export/export?meta_type=Naaya%20News&file_type=Excel&as_attachment=True')
            excel = self.browser.get_html()
            wb = xlrd.open_workbook(file_contents=excel)
            ws = wb.sheets()[0]
            self.assertEqual(ws.cell(1,0).value, 'The News')
