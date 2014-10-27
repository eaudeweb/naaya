from unittest import TestSuite, makeSuite
from datetime import date, timedelta

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaSurvey.MegaSurvey import manage_addMegaSurvey
from Products.NaayaSurvey.SurveyAnswer import manage_addSurveyAnswer

from Products.NaayaCore.EmailTool.EmailTool import divert_mail


class SurveyTestCase(NaayaFunctionalTestCase):
    def setUp(self):
        super(SurveyTestCase, self).setUp()

        addNyFolder(self.portal, 'myfolder', contributor='admin', submitted=1)
        releasedate = (date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
        expirationdate = (date.today() + timedelta(days=10)).strftime('%d/%m/%Y')
        manage_addMegaSurvey(self.portal.myfolder, title="Test survey",
            releasedate=releasedate, expirationdate=expirationdate,
            allow_anonymous=1, contributor='admin', submitted=1)
        self.survey = self.portal.myfolder['test-survey']
        self.survey.addWidget(title="Question",
            meta_type="Naaya String Widget")
        manage_addSurveyAnswer(self.survey, respondent='admin',
            datamodel={'w_question': 'String answer...'},
            anonymous_answer=True)
        self.survey.generateFullReport(title='Full report')
        self.diverted_mail = divert_mail()
        self.survey_url = 'http://localhost/portal/myfolder/test-survey'
        transaction.commit()

    def tearDown(self):
        divert_mail(False)
        self.portal.manage_delObjects(['myfolder'])
        transaction.commit()

    def test_anonymous_true_view_answers(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.survey_url+'/view_answers_html')
        html = self.browser.get_html()
        self.assertTrue('Answered by Anonymous authenticated user' in html)
        self.assertFalse('Answered by admin' in html)

        self.browser_do_logout()

    def test_anonymous_true_reports(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.survey_url+'/questionnaire_view_report_html?report_id=full-report')
        html = self.browser.get_html()
        self.assertFalse('>admin<' in html)
        self.assertTrue('>Anonymous authenticated user<' in html)

        self.browser_do_logout()

    def test_anonymous_false_view_answers(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.survey_url)
        form = self.browser.get_form('frmAdd')
        form['anonymous_answer:int'] = ['0']
        form['w_question:utf8:ustring'] = 'String answer...'
        self.browser.clicked(form, form.find_control('w_question:utf8:ustring'))
        self.browser.submit()

        self.browser.go(self.survey_url+'/view_answers_html')
        html = self.browser.get_html()
        self.assertTrue('Answered by admin' in html)
        self.assertFalse('Answered by Anonymous authenticated user' in html)

        self.browser_do_logout()

    def test_anonymous_false_reports(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.survey_url)
        form = self.browser.get_form('frmAdd')
        form['anonymous_answer:int'] = ['0']
        form['w_question:utf8:ustring'] = 'String answer...'
        self.browser.clicked(form, form.find_control('w_question:utf8:ustring'))
        self.browser.submit()

        self.browser.go(self.survey_url+'/questionnaire_view_report_html?report_id=full-report')
        html = self.browser.get_html()
        self.assertTrue('>admin<' in html)
        self.assertFalse('>Anonymous authenticated user<' in html)

        self.browser_do_logout()

    def test_anonymous_disabled_view_old_answer(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.survey_url+'/edit_html')
        form = self.browser.get_form('frmEdit')
        form['allow_anonymous'] = ['0']
        self.browser.clicked(form, form.find_control('allow_anonymous'))
        self.browser.submit()

        self.browser.go(self.survey_url+'/view_answers_html')
        html = self.browser.get_html()
        self.assertTrue('Answered by Anonymous authenticated user' in html)
        self.assertFalse('Answered by admin' in html)

        self.browser_do_logout()

    def test_anonymous_disabled_view_answers(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.survey_url+'/edit_html')
        form = self.browser.get_form('frmEdit')
        form['allow_anonymous'] = ['0']
        self.browser.clicked(form, form.find_control('allow_anonymous'))
        self.browser.submit()

        self.browser.go(self.survey_url)
        form = self.browser.get_form('frmAdd')
        form['w_question:utf8:ustring'] = 'String answer...'
        self.browser.clicked(form, form.find_control('w_question:utf8:ustring'))
        self.browser.submit()

        self.browser.go(self.survey_url+'/view_answers_html')
        html = self.browser.get_html()
        self.assertTrue('Answered by admin' in html)
        self.assertFalse('Answered by Anonymous authenticated user' in html)

        self.browser_do_logout()

    def test_anonymous_disabled_old_answer_reports(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.survey_url+'/edit_html')
        form = self.browser.get_form('frmEdit')
        form['allow_anonymous'] = ['0']
        self.browser.clicked(form, form.find_control('allow_anonymous'))
        self.browser.submit()

        self.browser.go(self.survey_url+'/questionnaire_view_report_html?report_id=full-report')
        html = self.browser.get_html()
        self.assertFalse('>admin<' in html)
        self.assertTrue('>Anonymous authenticated user<' in html)

        self.browser_do_logout()

    def test_anonymous_disabled_reports(self):
        self.browser_do_login('admin', '')

        self.browser.go(self.survey_url+'/edit_html')
        form = self.browser.get_form('frmEdit')
        form['allow_anonymous'] = ['0']
        self.browser.clicked(form, form.find_control('allow_anonymous'))
        self.browser.submit()

        self.browser.go(self.survey_url)
        form = self.browser.get_form('frmAdd')
        form['w_question:utf8:ustring'] = 'String answer...'
        self.browser.clicked(form, form.find_control('w_question:utf8:ustring'))
        self.browser.submit()

        self.browser.go(self.survey_url+'/questionnaire_view_report_html?report_id=full-report')
        html = self.browser.get_html()
        self.assertTrue('>admin<' in html)
        self.assertFalse('>Anonymous authenticated user<' in html)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(SurveyTestCase))
    return suite
