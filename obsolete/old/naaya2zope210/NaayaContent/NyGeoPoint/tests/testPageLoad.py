from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaContent.NyGeoPoint.NyGeoPoint import addNyGeoPoint
from Products.NaayaCore.SchemaTool.widgets.geo import Geo

class PageLoadTests(NaayaTestCase):
    def afterSetUp(self):
        portal = self.app.portal
        portal.manage_install_pluggableitem('Naaya GeoPoint')
        addNyFolder(portal, 'test_folder')
        addNyGeoPoint(portal.test_folder, id='test_point', title='test_point', geo_location=Geo('13', '13'))

    def beforeTearDown(self):
        portal = self.app.portal
        self.app.portal.test_folder.manage_delObjects('test_point')
        self.app.portal.manage_delObjects('test_folder')
        portal.manage_uninstall_pluggableitem('Naaya GeoPoint')

    def test_page_load(self):
        """
        Try to render some basic pages; if they raise exceptions the test will fail.
        """
        test_folder = self.app.portal.test_folder
        test_point = self.app.portal.test_folder.test_point

        test_folder.geopoint_add_html()
        test_point.index_html()
        test_point.edit_html()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PageLoadTests))
    return suite
