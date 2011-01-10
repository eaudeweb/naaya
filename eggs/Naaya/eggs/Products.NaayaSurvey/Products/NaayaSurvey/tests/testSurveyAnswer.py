import unittest
from mock import Mock, patch

from Products.NaayaWidgets.Widget import WidgetError
import Products.NaayaSurvey.SurveyQuestionnaire
from Products.NaayaSurvey.SurveyQuestionnaire import (
                                                SurveyQuestionnaireException)

import stubs

def invalidation_onsubmit_side_effect(datamodel, errors):
    errors.append('validation_onsubmit_error')
def dec_invalidation_onsubmit(func):
    def new_func(*args, **kwargs):
        global validation_onsubmit
        validation_onsubmit.side_effect = invalidation_onsubmit_side_effect
        try:
            func(*args, **kwargs)
        finally:
            validation_onsubmit.side_effect = None
    return new_func
validation_onsubmit = Mock()

answer_12345 = Mock()
def _getOb_side_effect(*args, **kwargs):
    global validation_onsubmit
    if args[0] == 'answer_12345':
        return answer_12345
    elif args[0] == 'validation_onsubmit':
        return validation_onsubmit
    return None

class AddSurveyAnswerTestCase(unittest.TestCase):
    def setUp(self):
        survey = stubs.Survey()
        survey = survey.__of__(survey)
        survey.expired = Mock(return_value=False)
        survey.getWidgets = Mock(return_value=[])
        survey.getSite = Mock()
        survey.getSite.return_value.validateCaptcha = Mock(return_value=False)
        survey.allow_multiple_answers = True
        survey.notify_owner = False
        survey.notify_respondents = 'LET_THEM_CHOOSE'

        survey.setSessionErrorsTrans = Mock()
        survey.setSessionAnswer = Mock()
        survey.setSession = Mock()
        survey.delSessionKeys = Mock()

        survey.absolute_url = Mock(return_value="http://survey")
        survey._getOb = Mock(side_effect=_getOb_side_effect)

        self.survey = survey

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_expired_survey_no_request(self, manage_addSurveyAnswer):
        survey = self.survey
        survey.expired = Mock(return_value=True)

        self.assertRaises(SurveyQuestionnaireException,
                          survey.addSurveyAnswer)
        self.assertEqual(manage_addSurveyAnswer.call_count, 0)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_expired_survey_with_request(self, manage_addSurveyAnswer):
        survey = self.survey
        survey.expired = Mock(return_value=True)
        REQUEST = Mock()
        REQUEST.form = {}

        survey.addSurveyAnswer(REQUEST=REQUEST)

        survey.setSessionErrorsTrans.assert_called_with(
                                        "The survey has expired")
        REQUEST.RESPONSE.redirect.assert_called_with("http://survey/index_html")
        self.assertEqual(manage_addSurveyAnswer.call_count, 0)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_invalid_widget_no_request(self, manage_addSurveyAnswer):
        survey = self.survey
        widget = Mock()
        widget.getDataModel = Mock(return_value='')
        widget.validateDatamodel = Mock(side_effect=WidgetError('test_error'))
        survey.getWidgets = Mock(return_value=[widget])

        #self.assertRaises(WidgetError, survey.addSurveyAnswer)
        self.assertEqual(manage_addSurveyAnswer.call_count, 0)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_invalid_widget_with_request(self, manage_addSurveyAnswer):
        survey = self.survey
        widget = Mock()
        widget.getWidgetId = Mock(return_value='test_widget')
        widget.getDataModel = Mock(return_value='')
        widget.validateDatamodel = Mock(side_effect=WidgetError('test_error'))
        survey.getWidgets = Mock(return_value=[widget])
        REQUEST = Mock()
        REQUEST.form = {}

        survey.addSurveyAnswer(REQUEST=REQUEST)

        survey.setSessionErrorsTrans.assert_called_with(['test_error'])
        survey.setSessionAnswer.assert_called_with({'test_widget': None})
        survey.setSession.assert_called_with('notify_respondent', False)
        REQUEST.RESPONSE.redirect.assert_called_with("http://survey/index_html")
        self.assertEqual(manage_addSurveyAnswer.call_count, 0)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_invalid_captcha_no_request(self, manage_addSurveyAnswer):
        survey = self.survey
        getSite = survey.getSite
        getSite.return_value.validateCaptcha = Mock(return_value='test_error')

        #survey.addSurveyAnswer()

        #self.assertEqual(survey.getSite.return_value.validateCaptcha.call_count,
        #                 0)
        #manage_addSurveyAnswer.assert_called_with(survey, {}, REQUEST=None)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_invalid_captcha_with_request(self, manage_addSurveyAnswer):
        survey = self.survey
        getSite = survey.getSite
        getSite.return_value.validateCaptcha = Mock(return_value='test_error')
        REQUEST = Mock()
        REQUEST.form = {}

        survey.addSurveyAnswer(REQUEST=REQUEST)

        survey.setSessionErrorsTrans.assert_called_with(['test_error'])
        survey.setSessionAnswer.assert_called_with({})
        survey.setSession.assert_called_with('notify_respondent', False)
        REQUEST.RESPONSE.redirect.assert_called_with("http://survey/index_html")
        self.assertEqual(manage_addSurveyAnswer.call_count, 0)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    @dec_invalidation_onsubmit
    def test_invalidation_onsubmit_no_request(self, manage_addSurveyAnswer):
        survey = self.survey

        #self.assertRaises(WidgetError, survey.addSurveyAnswer())
        #self.assertEqual(manage_addSurveyAnswer.call_count, 0)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    @dec_invalidation_onsubmit
    def test_invalidation_onsubmit_with_request(self, manage_addSurveyAnswer):
        survey = self.survey
        REQUEST = Mock()
        REQUEST.form = {}

        survey.addSurveyAnswer(REQUEST=REQUEST)

        survey.setSessionErrorsTrans.assert_called_with(
                                                ['validation_onsubmit_error'])
        survey.setSessionAnswer.assert_called_with({})
        survey.setSession.assert_called_with('notify_respondent', False)
        REQUEST.RESPONSE.redirect.assert_called_with("http://survey/index_html")
        self.assertEqual(manage_addSurveyAnswer.call_count, 0)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_explicit_answer_id_no_request(self, manage_addSurveyAnswer):
        survey = self.survey
        survey._delObject = Mock()

        survey.addSurveyAnswer(answer_id='12345')

        #survey._delObject.assert_called_with('12345')
        manage_addSurveyAnswer.assert_called_with(survey, {}, REQUEST=None)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_explicit_answer_id_with_request(self, manage_addSurveyAnswer):
        survey = self.survey
        survey._delObject = Mock()
        REQUEST = Mock()
        REQUEST.form = {'answer_id': '12345'}

        survey.addSurveyAnswer(REQUEST=REQUEST)

        survey._delObject.assert_called_with('12345')
        manage_addSurveyAnswer.assert_called_with(survey, {}, REQUEST=REQUEST)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_no_multiple_answers_no_request(self, manage_addSurveyAnswer):
        survey = self.survey
        survey.allow_multiple_answers = False
        old_answer = Mock()
        old_answer.id = '12345'
        survey.getMyAnswer = Mock(return_value=old_answer)
        survey._delObject = Mock()

        survey.addSurveyAnswer()

        survey._delObject.assert_called_with('12345')
        manage_addSurveyAnswer.assert_called_with(survey, {}, REQUEST=None)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_no_multiple_answers_with_request(self, manage_addSurveyAnswer):
        survey = self.survey
        survey.allow_multiple_answers = False
        old_answer = Mock()
        old_answer.id = '12345'
        survey.getMyAnswer = Mock(return_value=old_answer)
        survey._delObject = Mock()
        REQUEST = Mock()
        REQUEST.form = {}

        survey.addSurveyAnswer(REQUEST=REQUEST)

        survey._delObject.assert_called_with('12345')
        manage_addSurveyAnswer.assert_called_with(survey, {}, REQUEST=REQUEST)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_success_no_request(self, manage_addSurveyAnswer):
        manage_addSurveyAnswer.return_value = 'answer_12345'
        survey = self.survey

        result = survey.addSurveyAnswer()

        self.assertEqual(result, 'answer_12345')
        self.assertEqual(survey.setSession.call_count, 0)
        #self.assertEqual(survey.delSessionKeys.call_count, 0)
        manage_addSurveyAnswer.assert_called_with(survey, {}, REQUEST=None)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_success_with_request(self, manage_addSurveyAnswer):
        manage_addSurveyAnswer.return_value = 'answer_12345'
        survey = self.survey
        REQUEST = Mock()
        REQUEST.form = {}

        result = survey.addSurveyAnswer(REQUEST=REQUEST)

        self.assertEqual(result, 'answer_12345')
        self.assertEqual(survey.setSession.call_count, 3)
        self.assertEqual(survey.setSession.call_args_list[0][0],
                         ('title', 'Thank you for taking the survey'))
        self.assertEqual(survey.setSession.call_args_list[1][0],
                         ('body', ''))
        self.assertEqual(survey.setSession.call_args_list[2][0],
                         ('referer', 'http://survey'))
        survey.delSessionKeys.assert_called_with([])
        REQUEST.RESPONSE.redirect.assert_called_with(
                                            "http://survey/messages_html")
        manage_addSurveyAnswer.assert_called_with(survey, {}, REQUEST=REQUEST)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_notify_owner(self, manage_addSurveyAnswer):
        manage_addSurveyAnswer.return_value = 'answer_12345'
        survey = self.survey
        survey.notify_owner = True
        survey.sendNotificationToOwner = Mock()

        survey.addSurveyAnswer()

        manage_addSurveyAnswer.assert_called_with(survey, {}, REQUEST=None)
        survey._getOb.assert_called_with('answer_12345')
        survey.sendNotificationToOwner.assert_called_with(answer_12345)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_notify_respondents_always(self, manage_addSurveyAnswer):
        manage_addSurveyAnswer.return_value = 'answer_12345'
        survey = self.survey
        survey.notify_respondents = 'ALWAYS'
        survey.sendNotificationToRespondent = Mock()

        survey.addSurveyAnswer()

        manage_addSurveyAnswer.assert_called_with(survey, {}, REQUEST=None)
        survey._getOb.assert_called_with('answer_12345')
        survey.sendNotificationToRespondent.assert_called_with(answer_12345)

    @patch('Products.NaayaSurvey.SurveyQuestionnaire.manage_addSurveyAnswer')
    def test_notify_respondents_choose(self, manage_addSurveyAnswer):
        manage_addSurveyAnswer.return_value = 'answer_12345'
        survey = self.survey
        survey.sendNotificationToRespondent = Mock()

        survey.addSurveyAnswer(notify_respondent=True)

        manage_addSurveyAnswer.assert_called_with(survey, {}, REQUEST=None)
        survey._getOb.assert_called_with('answer_12345')
        survey.sendNotificationToRespondent.assert_called_with(answer_12345)
