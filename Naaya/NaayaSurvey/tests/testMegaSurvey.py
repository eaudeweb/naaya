# Pythons imports
from unittest import TestSuite, makeSuite

# Zope imports
from Testing import ZopeTestCase

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

# Survey imports
from Products.NaayaSurvey.MegaSurvey import manage_addMegaSurvey
from Products.NaayaSurvey.SurveyReport import SurveyReport
from Products.NaayaSurvey.SurveyTool import SurveyTool, manage_addSurveyTool
from Products.NaayaWidgets.widgets import AVAILABLE_WIDGETS

ZopeTestCase.installProduct('NaayaWidgets')
ZopeTestCase.installProduct('NaayaSurvey')

class MegaSurveyTestCase(NaayaTestCase):
    """Mega Survey test cases"""

    def afterSetUp(self):
        self.login()
        manage_addSurveyTool(self.getPortal())
        id = manage_addMegaSurvey(self.getPortal(), title='Testing survey')
        self.survey = self.getPortal()._getOb(id)

    def testAddQuestions(self):
        """Add questions"""
        for widget_class in AVAILABLE_WIDGETS:
            id = self.survey.addWidget(title='A question', meta_type=widget_class.meta_type)
            w = self.survey._getOb(id, None)
            self.assertNotEqual(w, None)
            self.assert_(isinstance(w, widget_class))

    def testAddReport(self):
        """Add report"""
        id = self.survey.addReport(title='A report')
        report = self.survey._getOb(id, None)
        self.assertNotEqual(report, None)
        self.assert_(isinstance(report, SurveyReport))

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(MegaSurveyTestCase))
    return suite
