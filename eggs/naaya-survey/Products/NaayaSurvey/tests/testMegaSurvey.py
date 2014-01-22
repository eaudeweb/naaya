# Pythons imports
import unittest
from mock import Mock, MagicMock

# Zope imports
from Testing import ZopeTestCase
from DateTime import DateTime

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaBase.NyRoleManager import NyRoleManager

# Survey imports
from Products.NaayaSurvey.MegaSurvey import manage_addMegaSurvey
from Products.NaayaSurvey.SurveyQuestionnaire import SurveyQuestionnaire, SurveyQuestionnaireException
from Products.NaayaSurvey.SurveyReport import SurveyReport
from Products.NaayaWidgets.widgets import AVAILABLE_WIDGETS

# stub imports
import stubs

ZopeTestCase.installProduct('NaayaWidgets')
ZopeTestCase.installProduct('NaayaSurvey')

class MegaSurveyTestCase(NaayaTestCase):
    """Mega Survey test cases"""

    def afterSetUp(self):
        self.login()
        id = manage_addMegaSurvey(self.portal, title='Testing survey')
        self.survey = self.portal._getOb(id)
        self.portal.manage_install_pluggableitem('Naaya Mega Survey')

    def beforeTearDown(self):
        self.logout()

    def testAddQuestions(self):
        """Add questions"""
        for widget_class in AVAILABLE_WIDGETS:
            title = 'A question'
            id = self.survey.addWidget(title=title, meta_type=widget_class.meta_type)
            w = self.survey._getOb(id, None)
            self.assertNotEqual(w, None)
            self.assert_(isinstance(w, widget_class))
            self.assertEqual(w.getLocalAttribute('title', self.portal.gl_get_selected_language()), title)

    def testAddReport(self):
        """Add report"""
        title = 'A report'
        id = self.survey.addReport(title=title)
        report = self.survey._getOb(id, None)
        self.assertNotEqual(report, None)
        self.assert_(isinstance(report, SurveyReport))
        self.assertEqual(report.getLocalAttribute('title', self.portal.gl_get_selected_language()), title)

    def testGenerateFullReport(self):
        """Generate full report"""
        title = 'Full report'
        id = self.survey.generateFullReport(title=title)
        report = self.survey._getOb(id, None)
        self.assertNotEqual(report, None)
        self.assert_(isinstance(report, SurveyReport))
        self.assertEqual(report.getLocalAttribute('title', self.portal.gl_get_selected_language()), title)
        self.assertEqual(len(report.getStatistics()), 0) # 0 questions -> 0 statistics

    def test_NyRoleManager_wrappers(self):
        self.assertTrue(SurveyQuestionnaire.manage_addLocalRoles == NyRoleManager.manage_addLocalRoles)
        self.assertTrue(SurveyQuestionnaire.manage_setLocalRoles == NyRoleManager.manage_setLocalRoles)
        self.assertTrue(SurveyQuestionnaire.manage_delLocalRoles == NyRoleManager.manage_delLocalRoles)

    def test_missingLanguageFallback(self):
        self.portal.gl_add_site_language('de', 'Deutsch')
        self.portal.gl_add_site_language('fr', 'French')
        title = 'question'
        req = MagicMock()
        req.form = {'lang': 'fr'}
        for widget_class in AVAILABLE_WIDGETS:
            wId = self.survey.addWidget(REQUEST=req, title=title, meta_type=widget_class.meta_type)
            w = self.survey._getOb(wId, None)
            self.assertNotEqual(w, None)
            self.assert_(isinstance(w, widget_class))
            self.assertEqual(self.portal.gl_get_selected_language(), 'en')
            self.assertEqual(w.getLocalAttribute('title'), '')
            self.assertEqual(w.getLocalAttribute('title', 'en'), '')
            self.assertEqual(w.getLocalAttribute('title', 'de'), '')
            self.assertEqual(w.getLocalAttribute('title', 'fr'), title)
            self.assertEqual(w.getNonEmptyAttribute('title'), title)

class MegaSurveyTestCaseNoLogin(NaayaTestCase):
    """Mega Survey test cases"""

    def afterSetUp(self):
        id = manage_addMegaSurvey(self.portal, title='Testing survey')
        self.survey = self.portal._getOb(id)
        self.portal.manage_install_pluggableitem('Naaya Mega Survey')

    def testTakingSurvey(self):
        """Test taking a survey"""
        answer = self.survey.getMyAnswer()
        self.assertEqual(answer, None)

        self.survey.expirationdate = DateTime() + 5
        self.survey.addSurveyAnswer(notify_respondent=False)

        self.survey.expirationdate = DateTime() - 5
        self.assertRaises(SurveyQuestionnaireException, self.survey.addSurveyAnswer, notify_respondent=False)

class SavePropertiesTestCase(unittest.TestCase):
    def setUp(self):
        survey = stubs.Survey()
        survey.get_selected_language = Mock(return_value='en')
        survey.process_releasedate = Mock(return_value=DateTime('1/1/2010'))
        survey.updatePropertiesFromGlossary = Mock()
        survey.recatalogNyObject = Mock()

        self.survey = survey

    def test_allow_drafts(self):
        survey = self.survey

        for value in [0, 1]:
            survey.saveProperties(allow_drafts=value)
            self.assertEqual(survey.__dict__['allow_drafts'], value)

    def test_allow_anonymous(self):
        survey = self.survey

        for value in [0, 1]:
            survey.saveProperties(allow_anonymous=value)
            self.assertEqual(survey.__dict__['allow_anonymous'], value)
