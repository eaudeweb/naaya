import csv
from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch, Mock

import transaction
from pyquery import PyQuery

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaSurvey.MegaSurvey import manage_addMegaSurvey
from Products.NaayaCore.EmailTool.EmailTool import divert_mail

SURVEY_URL = 'http://localhost/portal/myfolder/test-survey'


class SurveyFunctionalTest(NaayaFunctionalTestCase):
    """ Answering a survey and reading its answers and reports """

    def setUp(self):
        super(SurveyFunctionalTest, self).setUp()
        addNyFolder(self.portal, 'myfolder', contributor='admin', submitted=1)
        today = date.today()
        manage_addMegaSurvey(
            self.portal.myfolder, title="Test survey",
            releasedate=(today - timedelta(days=1)).strftime('%d/%m/%Y'),
            expirationdate=(today + timedelta(days=10)).strftime('%d/%m/%Y'),
            contributor='admin', submitted=1)
        self.survey = survey = self.portal.myfolder['test-survey']
        self.text = survey.addWidget(title='Name',
                                     meta_type='Naaya String Widget')
        self.radio = survey.addWidget(title='Happy', choices=['Yes', 'No'],
                                      meta_type='Naaya Radio Widget')
        self.matrix = survey.addWidget(title='Rate', rows=['Food', 'Room'],
                                       choices=['Bad', 'Good'],
                                       meta_type='Naaya Radio Matrix Widget')
        self.file = survey.addWidget(title='Document',
                                     meta_type='Naaya File Widget')
        survey.allow_multiple_answers = True
        self.diverted_mail = divert_mail()
        transaction.commit()
        self.browser_do_login('admin', '')

    def tearDown(self):
        divert_mail(False)
        self.portal.manage_delObjects(['myfolder'])
        transaction.commit()
        super(SurveyFunctionalTest, self).tearDown()

    def answer(self, name, happy, food, room, files=None):
        response = self.browser._twill._client.post(
            SURVEY_URL + '/addSurveyAnswer',
            data={self.text: name, self.radio: str(happy),
                  '%s_0' % self.matrix: str(food),
                  '%s_1' % self.matrix: str(room)},
            files=files or {}, follow_redirects=False)
        transaction.begin()
        return response

    def answers(self):
        return self.survey.objectValues('Naaya Survey Answer')

    def test_answer_stored_and_thank_you_page(self):
        response = self.answer('Ana', 0, 1, 1)
        self.assertEqual(response.headers['location'],
                         SURVEY_URL + '/messages_html')
        [answer] = self.answers()
        self.assertEqual(answer.get(self.text), 'Ana')
        self.assertEqual(answer.get(self.radio), 0)
        self.assertEqual(answer.get(self.matrix), [1, 1])
        self.assertEqual(answer.respondent, 'admin')
        self.browser.go(SURVEY_URL + '/messages_html')
        self.assertEqual(self.browser.get_code(), 200)
        self.assertIn('Thank you for taking the survey',
                      self.browser.get_html())

    def test_answer_with_file_upload(self):
        self.answer('Ana', 0, 1, 0, files={
            self.file: ('report.txt', b'file contents', 'text/plain')})
        [answer] = self.answers()
        attachment = getattr(answer, self.file)
        self.assertEqual(attachment.content_type, 'text/plain')
        self.assertEqual(attachment.size, len(b'file contents'))
        self.assertEqual(attachment.open().read(), b'file contents')
        self.browser.go(answer.absolute_url())
        self.assertIn('report.txt', self.browser.get_html())

    def test_missing_required_answer(self):
        self.survey._getOb(self.text).required = True
        transaction.commit()
        response = self.answer('', 0, 1, 0)
        self.assertEqual(response.headers['location'], SURVEY_URL)
        self.assertEqual(self.answers(), [])

    def test_download_csv(self):
        self.answer('Ana', 0, 1, 0)
        self.answer('Ion', 1, 0, 0)
        self.browser.go(SURVEY_URL + '/download?file_type=CSV')
        self.assertTrue(
            self.browser_get_header('content-type').startswith('text/csv'))
        rows = list(csv.reader(StringIO(self.browser.get_html())))
        self.assertEqual(rows[0], ['Respondent', 'Name', 'Happy', 'Rate',
                                   'Food', 'Room', 'Document'])
        self.assertEqual(sorted(row[1:6] for row in rows[1:]),
                         [['Ana', 'Yes', '', 'Good', 'Bad'],
                          ['Ion', 'No', '', 'Bad', 'Bad']])

    def test_html_report_statistics(self):
        self.answer('Ana', 0, 1, 1)
        self.answer('Ion', 0, 0, 1)
        self.answer('Dan', 1, 1, 1)
        report_id = self.survey.generateFullReport(title='Full report')
        transaction.commit()
        self.browser.go(SURVEY_URL + '/questionnaire_view_report_html'
                        '?report_id=' + report_id)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        text = PyQuery(html).text()
        for expected in ('Happy', 'Rate', 'Food', 'Room', 'Ana', 'Ion',
                         'Dan', '66.67%', '33.33%', '100.00%'):
            self.assertIn(expected, text)
        charts = PyQuery(html)('img[src^="http://chart.apis.google.com"]')
        self.assertEqual(len(charts), 2)
        self.assertIn('chl=Yes|No|Not%20answered', charts[1].get('src'))
        self.assertTrue(PyQuery(html)('img[alt="66.67"]'))

    def test_pdf_export_with_auth_cookie(self):
        self.answer('Ana', 0, 1, 1)
        report_id = self.survey.generateFullReport(title='Full report')
        request = self.portal.REQUEST
        request.environ['HTTP_COOKIE'] = 'lang=en; __ac="c2VjcmV0"'
        request.environ['HTTP_X_FORWARDED_HOST'] = 'example.com'
        request['HTTP_X_FORWARDED_HOST'] = 'example.com'
        jars = []

        def from_url(url, output, options):
            with open(options['cookie-jar']) as f:
                jars.append(f.read())
            return b'%PDF'
        with patch('Products.NaayaSurvey.SurveyQuestionnaire.pdfkit') as kit:
            kit.from_url.side_effect = from_url
            data = self.survey.questionnaire_export(report_id, request,
                                                    type='pdf')
        self.assertEqual(data, b'%PDF')
        self.assertEqual(jars, ['__ac=c2VjcmV0; domain=example.com; path=/;'])
        url = kit.from_url.call_args.args[0]
        self.assertTrue(url.endswith(
            '/questionnaire_view_report_html?report_id=' + report_id))

    def test_pdf_export_without_cookies(self):
        report_id = self.survey.generateFullReport(title='Full report')
        request = self.portal.REQUEST
        request.environ.pop('HTTP_COOKIE', None)
        with patch('Products.NaayaSurvey.SurveyQuestionnaire.pdfkit') as kit:
            kit.from_url.return_value = b'%PDF'
            data = self.survey.questionnaire_export(report_id, request,
                                                    type='pdf')
        self.assertEqual(data, b'%PDF')
        self.assertNotIn('cookie-jar', kit.from_url.call_args.kwargs[
            'options'])

    def test_respondent_edits_own_answer(self):
        self.answer('Ana', 0, 1, 1)
        [answer] = self.answers()
        response = self.browser._twill._client.post(
            SURVEY_URL + '/addSurveyAnswer',
            data={self.text: 'Ana Maria', self.radio: '1',
                  '%s_0' % self.matrix: '0', '%s_1' % self.matrix: '0',
                  'answer_id': answer.getId()},
            follow_redirects=False)
        transaction.begin()
        [edited] = self.answers()
        self.assertEqual(edited.getId(), answer.getId())
        self.assertEqual(edited.get(self.text), 'Ana Maria')
        self.assertEqual(edited.creation_date, answer.creation_date)
        self.assertEqual(response.headers['location'],
                         SURVEY_URL + '/messages_html')

    def test_deny_editing_own_answer(self):
        self.survey.allow_own_answer_edit = False
        self.survey.allow_multiple_answers = False
        transaction.commit()
        self.answer('Ana', 0, 1, 1)
        [answer] = self.answers()
        self.browser.go(SURVEY_URL)
        self.assertEqual(self.browser.get_url(), answer.absolute_url())
        self.survey.allow_own_answer_edit = True
        transaction.commit()
        self.browser.go(SURVEY_URL)
        self.assertEqual(self.browser.get_url(), SURVEY_URL)
