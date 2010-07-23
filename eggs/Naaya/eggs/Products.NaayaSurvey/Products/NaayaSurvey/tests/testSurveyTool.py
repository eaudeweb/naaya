# Pythons imports
from unittest import TestSuite, makeSuite

# Zope imports
from Testing import ZopeTestCase

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

# Survey imports
from Products.NaayaSurvey.SurveyTool import SurveyTool, manage_addSurveyTool

ZopeTestCase.installProduct('NaayaWidgets')
ZopeTestCase.installProduct('NaayaSurvey')

class SurveyToolTestCase(NaayaTestCase):
    """Survey Tool test cases"""

    def afterSetUp(self):
        self.login()

    def beforeTearDown(self):
        self.logout()

    def testAddSurveyTool(self):
        """Add Survey Tool - manage_addSurveyTool"""
        id = manage_addSurveyTool(self.getPortal())
        self.assertEqual(id, SurveyTool.portal_id)
        ob = self.getPortal()._getOb(id, None)
        self.assertNotEqual(ob, None)
        self.assert_(isinstance(ob, SurveyTool))

        # catalog
        indexes = self.getPortal().getCatalogTool().indexes()
        self.assert_('respondent' in indexes)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(SurveyToolTestCase))
    return suite
