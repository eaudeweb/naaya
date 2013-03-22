import sys
import urllib
import tempfile
import shutil
import os.path
from cStringIO import StringIO

try:
    import xlwt
    excel_export_available = True
except:
    excel_export_available = False

# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
from DateTime import DateTime
from Globals import InitializeClass
from OFS.Traversable import path2url
from ZPublisher import NotFound
from ZPublisher.HTTPRequest import FileUpload
from zLOG import LOG, ERROR, DEBUG
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from Products.PythonScripts.PythonScript import manage_addPythonScript

# Product imports
from Products.Naaya.constants import DEFAULT_SORTORDER
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyImageContainer import NyImageContainer
from Products.NaayaBase.constants import \
     MESSAGE_SAVEDCHANGES, PERMISSION_EDIT_OBJECTS, \
     PERMISSION_SKIP_CAPTCHA
from Products.NaayaCore.managers import recaptcha_utils
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.EmailTool.EmailPageTemplate import (
    manage_addEmailPageTemplate, EmailPageTemplateFile)
from Products.NaayaWidgets.Widget import WidgetError
from Products.NaayaBase.NyRoleManager import NyRoleManager
from naaya.core.zope2util import folder_manage_main_plus

from SurveyAnswer import manage_addSurveyAnswer, SurveyAnswer
from permissions import *
from questionnaire_item import questionnaire_item

from migrations import available_migrations, perform_migration

class SurveyQuestionnaireException(Exception):
    """Survey related exception"""
    pass

def set_response_attachment(RESPONSE, filename, content_type, length=None):
    RESPONSE.setHeader('Content-Type', content_type)
    if length is not None:
        RESPONSE.setHeader('Content-Length', length)
    RESPONSE.setHeader('Pragma', 'public')
    RESPONSE.setHeader('Cache-Control', 'max-age=0')
    RESPONSE.setHeader('Content-Disposition', "attachment; filename*=UTF-8''%s"
        % urllib.quote(filename))

email_templates = {
    'email_to_owner': EmailPageTemplateFile('templates/email_survey_answer_to_owner.zpt', globals()),
    'email_to_respondent': EmailPageTemplateFile('templates/email_survey_answer_to_respondent.zpt', globals()),
    'email_to_unauthenticated': EmailPageTemplateFile('templates/email_survey_answer_to_unauthenticated.zpt', globals()),
}

class SurveyQuestionnaire(NyRoleManager, NyAttributes, questionnaire_item, NyContainer):
    """ """
    meta_type = "Naaya Survey Questionnaire"
    meta_label = "Survey Instance"
    icon = 'misc_/NaayaSurvey/NySurveyQuestionnaire.gif'
    icon_marked = 'misc_/NaayaSurvey/NySurveyQuestionnaire_marked.gif'

    _constructors = ()

    all_meta_types = ()

    manage_options=(
        {'label':'Contents', 'action':'manage_main',
          'help':('OFSP','ObjectManager_Contents.stx')},
        {'label':'Properties', 'action':'manage_propertiesForm',
         'help':('OFSP','Properties.stx')},
        {'label':'View', 'action':'index_html'},
        {'label':'Migrations', 'action':'manage_migrate_html'},
        {'label': 'Updates', 'action':'manage_update_combo_answers_html'},
        {'label':'Security', 'action':'manage_access',
         'help':('OFSP', 'Security.stx')},
      )

    security = ClassSecurityInfo()

    notify_owner = True
    notify_respondents = 'LET_THEM_CHOOSE_YES'
    allow_overtime = 0
    allow_drafts = False
    allow_multiple_answers = False

    def __init__(self, id, survey_template, lang=None, **kwargs):
        """
            @param id: id
            @param survey_template: id of the survey template
        """
        self.id = id
        self._survey_template = survey_template

        self.save_properties(lang=lang, **kwargs)
        NyContainer.__dict__['__init__'](self)
        self.imageContainer = NyImageContainer(self, True)

    #
    # Self edit methods
    #
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST:
            kwargs.update(REQUEST.form)
        lang = kwargs.get('lang', self.get_selected_language())

        kwargs.setdefault('title', '')
        kwargs.setdefault('description', '')
        kwargs.setdefault('keywords', '')
        kwargs.setdefault('coverage', '')
        kwargs.setdefault('sortorder', DEFAULT_SORTORDER)

        releasedate = kwargs.get('releasedate', DateTime())
        releasedate = self.process_releasedate(releasedate)
        kwargs['releasedate'] = releasedate

        expirationdate = kwargs.get('expirationdate', DateTime())
        expirationdate = self.process_releasedate(expirationdate)
        kwargs['expirationdate'] = expirationdate

        self.save_properties(**kwargs)
        self.updatePropertiesFromGlossary(lang)
        self.recatalogNyObject(self)

        if REQUEST:
            # Log date
            contributor = REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            # Redirect
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES, date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #
    # Methods required by the Naaya framework
    #
    security.declareProtected(view, 'hasVersion')
    def hasVersion(self):
        """ """
        return False

    security.declareProtected(view, 'getVersionLocalProperty')
    def getVersionLocalProperty(self, id, lang):
        """ """
        return self.getLocalProperty(id, lang)

    security.declareProtected(view, 'getVersionProperty')
    def getVersionProperty(self, id):
        """ """
        return getattr(self, id, '')

    #
    # Answer edit methods
    #

    security.declareProtected(view, 'canAddAnswerDraft')
    def canAddAnswerDraft(self):
        """ Check if current user can add an answer draft """
        auth_tool = self.getAuthenticationTool()
        return self.allow_drafts and not auth_tool.isAnonymousUser()

    security.declareProtected(PERMISSION_ADD_ANSWER, 'addSurveyAnswerDraft')
    def addSurveyAnswerDraft(self, REQUEST=None, notify_respondent=False,
            **kwargs):
        """This is just to be able to specify submit method in zpt"""
        return self.addSurveyAnswer(REQUEST, notify_respondent, draft=True,
                                    **kwargs)

    security.declareProtected(PERMISSION_ADD_ANSWER, 'addSurveyAnswer')
    def addSurveyAnswer(self, REQUEST=None, notify_respondent=False,
            draft=False, **kwargs):
        """Add someone's answer"""
        if REQUEST:
            kwargs.update(REQUEST.form)

        #check survey expiration
        if self.expired() and not self.checkPermissionPublishObjects():
            error_msg = "The survey has expired"
            if not REQUEST:
                raise SurveyQuestionnaireException(error_msg)
            self.setSessionErrorsTrans(error_msg)
            REQUEST.RESPONSE.redirect(self.absolute_url())
            return

        #check datamodel
        datamodel = {}
        errors = []
        for widget in self.getWidgets():
            try:
                value = widget.getDatamodel(kwargs)
                if not draft:
                    widget.validateDatamodel(value)
            except WidgetError, ex:
                if not REQUEST:
                    raise
                value = None
                errors.append(str(ex))
            datamodel[widget.getWidgetId()] = value

        if draft:
            if not self.canAddAnswerDraft():
                error_msg = "Can't add draft (not logged in or not allowed)"
                if not REQUEST:
                    raise SurveyQuestionnaireException(error_msg)
                errors.append(error_msg)
        else:
            try:
                validation_onsubmit = self['validation_onsubmit']
            except KeyError:
                pass
            else:
                validation_onsubmit(datamodel, errors)

        if not REQUEST and errors:
            raise WidgetError(errors[0])

        #check Captcha/reCaptcha
        if REQUEST and not self.checkPermission(PERMISSION_SKIP_CAPTCHA):
            captcha_errors = self.getSite().validateCaptcha('', REQUEST)
            if captcha_errors:
                errors.append(captcha_errors)

        answer_id = kwargs.pop('answer_id', None)
        if errors:
            # assumed that REQUEST is not None
            self.setSessionErrorsTrans(errors)
            self.setSessionAnswer(datamodel)
            self.setSession('notify_respondent', notify_respondent)
            if answer_id is not None:
                answer = self._getOb(answer_id)
                REQUEST.RESPONSE.redirect('%s?edit=1' % answer.absolute_url())
            else:
                REQUEST.RESPONSE.redirect(self.absolute_url())
            return

        suggestions = []
        cf_approval_list = []
        respondent = None
        creation_date = None
        anonymous_editing_key = None
        if answer_id is not None:
            old_answer = self._getOb(answer_id)
            respondent = old_answer.respondent
            cf_approval_list = getattr(old_answer, 'cf_approval_list', [])
            suggestions = getattr(old_answer, 'suggestions', [])
            anonymous_editing_key = getattr(old_answer,
                'anonymous_editing_key', None)
            if not getattr(old_answer, 'draft', False):
                creation_date = old_answer.get('creation_date')
            # an answer ID was provided explicitly for us to edit, so we
            # remove the old one
            self._delObject(answer_id)
            LOG('NaayaSurvey.SurveyQuestionnaire', DEBUG,
                'Deleted previous answer %s while editing' % answer_id)

        if not self.allow_multiple_answers:
            # look for an old answer and remove it
            old_answer = self.getAnswerForRespondent(respondent=respondent)
            if old_answer is not None:
                self._delObject(old_answer.id)
                LOG('NaayaSurvey.SurveyQuestionnaire', DEBUG,
                    'Deleted previous answer %s' % old_answer.absolute_url())

        #If we are in edit mode, keep the answer_id from the "old answer"
        answer_id = manage_addSurveyAnswer(self, datamodel, REQUEST=REQUEST,
                                           draft=draft, respondent=respondent,
                                           id=answer_id,
                                           creation_date=creation_date)

        answer = self._getOb(answer_id)

        if suggestions:
            answer.suggestions = suggestions
        if cf_approval_list:
            answer.cf_approval_list = cf_approval_list

        if self.isAnonymousUser():
            if anonymous_editing_key:
                answer.anonymous_editing_key = anonymous_editing_key
            anonymous_responder_email = kwargs.pop('anonymous_responder_email', None)
            if anonymous_responder_email:
                answer.anonymous_responder_email = anonymous_responder_email
                if not answer.get('anonymous_editing_key'):
                    answer.anonymous_editing_key = self.utGenRandomId(16)
                    self.sendNotificationToUnauthenticatedRespondent(answer)
        elif not draft:
            if self.notify_owner:
                self.sendNotificationToOwner(answer)
            if (self.notify_respondents == 'ALWAYS'
                or (self.notify_respondents.startswith('LET_THEM_CHOOSE')
                    and notify_respondent)):
                self.sendNotificationToRespondent(answer)

        if REQUEST:
            self.delSessionKeys(datamodel.keys())
            if not draft:
                if self.aq_parent.meta_type == 'Naaya Meeting':
                    self.setSessionInfoTrans('Thank you for taking the survey')
                    REQUEST.RESPONSE.redirect(self.aq_parent.absolute_url())
                else:
                    self.setSession('title', 'Thank you for taking the survey')
                    self.setSession('body', '')
                    self.setSession('referer', self.absolute_url())
                    REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
            else:
                REQUEST.RESPONSE.redirect('%s?edit=1' % answer.absolute_url())
        return answer_id

    security.declareProtected(PERMISSION_EDIT_ANSWERS, 'deleteAnswer')
    def deleteAnswer(self, answer_id, REQUEST=None):
        """ """
        self._delObject(answer_id)
        LOG('NaayaSurvey.SurveyQuestionnaire', DEBUG,
                'Deleting answer %s' % answer_id)

        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())

    #
    # Email notifications
    #

    security.declarePrivate('sendNotificationToOwner')
    def sendNotificationToOwner(self, answer):
        """Send an email notifications about the newly added answer to the owner of the survey.

            @param answer: the answer object that was added
            @type answer: SurveyAnswer
        """
        owner = self.getOwner()
        respondent = self.REQUEST.AUTHENTICATED_USER
        auth_tool = self.getSite().getAuthenticationTool()
        respondent_name = auth_tool.getUserFullName(respondent)

        d = {}
        d['NAME'] = auth_tool.getUserFullName(owner)
        if respondent_name == 'Anonymous User':
            d['RESPONDENT'] = ("%s, email: %s" % (respondent_name, answer.get('anonymous_responder_email', 'Not available')))
        else:
            d['RESPONDENT'] = ("User %s" % auth_tool.getUserFullName(respondent))
        d['SURVEY_TITLE'] = self.title
        d['SURVEY_URL'] = self.absolute_url()
        d['LINK'] = answer.absolute_url()

        self._sendEmailNotification('email_to_owner', d, owner)

    security.declarePrivate('sendNotificationToRespondent')
    def sendNotificationToRespondent(self, answer):
        """Send an email notification about the newly added answer to the respondent.
            If the respondent is an anonymous user no notification will be sent.

            @param answer: the answer object that was added (unsed for the moment)
            @type answer: SurveyAnswer
        """
        if self.isAnonymousUser():
            return

        respondent = self.REQUEST.AUTHENTICATED_USER
        auth_tool = self.getSite().getAuthenticationTool()

        d = {}
        d['NAME'] = auth_tool.getUserFullName(respondent)
        d['SURVEY_TITLE'] = self.title
        d['SURVEY_URL'] = self.absolute_url()
        d['LINK'] = "%s" % answer.absolute_url()

        self._sendEmailNotification('email_to_respondent', d,
                respondent)

    security.declarePrivate('sendNotificationToUnauthenticatedRespondent')
    def sendNotificationToUnauthenticatedRespondent(self, answer):
        """Send an email notification about the newly added answer to the email
            address provided by an anonymous respondent.

            @param answer: the answer object that was added (unsed for the moment)
            @type answer: SurveyAnswer
        """
        recp_email = answer.get('anonymous_responder_email')
        key = answer.get('anonymous_editing_key', None)

        d = {}
        d['SURVEY_TITLE'] = self.title
        d['SURVEY_URL'] = self.absolute_url()
        d['LINK'] = "%s?key=%s" % (answer.absolute_url(), key)
        d['EDIT_LINK'] = "%s?edit=1&key=%s" % (answer.absolute_url(), key)

        self._sendEmailNotification('email_to_unauthenticated', d,
                    recp_email=recp_email)

    security.declarePrivate('_sendEmailNotification')
    def _sendEmailNotification(self, template_name, d, recipient=None,
            recp_email=None):
        """Send an email notification.

            @param template_name: name of the email template
            @type template_name: string
            @param d: dictionary with the values used in the template
            @type d: dict
            @param recipient: recipient
            @type recipient: Zope User
        """
        if recipient is None and recp_email is None:
            #this only happens when self.isAnonymousUser() is True and the user
            #has not filled in an email address. So just return
            return

        auth_tool = self.getSite().getAuthenticationTool()
        email_tool = self.getSite().getEmailTool()
        translate = self.getSite().getPortalTranslations()
        template = self._get_template(template_name)
        d.update({'portal': self.getSite(), '_translate': translate})
        mail_data = template(**d)

        sender_email = email_tool.get_addr_from()

        try:
            recp_email = recp_email or auth_tool.getUserEmail(recipient)
            email_tool.sendEmail(mail_data['body_text'],
                                 recp_email,
                                 sender_email,
                                 mail_data['subject'])
            LOG('NaayaSurvey.SurveyQuestionnaire', DEBUG, 'Notification sent from %s to %s' % (sender_email, recp_email))
        except:
            # possible causes - the recipient doesn't have email
            #                   (e.g. regular Zope user)
            #                 - we can not send the email
            # these aren't fatal errors, so we'll just log the error
            err = sys.exc_info()
            LOG('NaayaSurvey.SurveyQuestionnaire', ERROR,
                'Could not send email notification for survey %s' %
                (self.absolute_url(),), error=err)

    #
    # Answer read methods
    #
    security.declareProtected(PERMISSION_VIEW_ANSWERS, 'getAnswers')
    def getAnswers(self, draft=False):
        """Return a list of answers.
           Filters out the draft ones.
        """
        return [answer for answer in self.objectValues(SurveyAnswer.meta_type)
                            if answer.is_draft()==bool(draft)]

    # this is method is used by the widget manage forms
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'getAnswerCountForQuestion')
    def getAnswerCountForQuestion(self, question_id, exclude_None=False):
        """Return the count of answers for question_id, excluding None ones if exclude_None if True."""
        L = [answer.get(question_id) for answer in self.getAnswers()]
        if exclude_None:
            L = [x for x in L if x is not None]
        return len(L)

    security.declarePublic('getMyAnswer')
    def getMyAnswer(self, multiple=False, draft=False):
        """Return the answer of the current user or None if it doesn't exist.
           If multiple answers exist, only the first one is returned.
           Filters out the draft ones.
        """
        return self.getAnswerForRespondent(multiple, draft)

    security.declarePublic('getAnswerForRespondent')
    def getAnswerForRespondent(self, multiple=False, draft=False, respondent=None):
        """Return the answer of the respondent (or current user if None)
           Returns None if the answer doesn't exist.
           If multiple answers exist, only the first one is returned.
           Filters out the draft ones.
        """
        if respondent is None:
            respondent = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if respondent == 'Anonymous User':
            return None

        catalog = self.getCatalogTool()
        objects = []
        for brain in catalog({'path': path2url(self.getPhysicalPath()),
                              'meta_type': SurveyAnswer.meta_type,
                              'respondent': respondent}):
            obj = brain.getObject()
            # if the "respondent" index is missing for some reason, we get
            # all answers, so we must do the filtering ourselves.
            if obj.respondent != respondent:
                continue
            if obj.is_draft() != bool(draft):
                continue
            if not multiple:
                return obj
            else:
                objects.append(obj)
        if objects:
            return objects
        else:
            return None

    security.declarePublic('getMyAnswerDatamodel')
    def getMyAnswerDatamodel(self):
        """ """
        answer = self.getMyAnswer()
        if answer is None:
            return {}
        return answer.getDatamodel()

    security.declarePrivate('setSessionAnswer')
    def setSessionAnswer(self, datamodel):
        """Sets the session with the specified answer"""
        for widget_id, value in datamodel.items():
            if value is None:
                continue
            if isinstance(value, FileUpload):
                continue
            self.setSession(widget_id, value)

    security.declareProtected(PERMISSION_VIEW_REPORTS, 'questionnaire_view_report_html')
    def questionnaire_view_report_html(self, report_id, REQUEST):
        """View the report report_id"""
        report = self.getReport(report_id)
        if not report:
            raise NotFound('Report %s' % (report_id,))
        return report.view_report_html(answers=self.getAnswers())

    security.declarePrivate('generate_excel')
    def generate_excel(self, report, answers):
        state = {}
        wb = xlwt.Workbook(encoding='utf-8')
        state['ws'] = wb.add_sheet('Report')
        state['temp_folder'] = tempfile.mkdtemp()
        state['answers'] = answers
        separator_style = xlwt.easyxf('borders: top thin')
        # alternatives for formatting
        #filled_cell_style = xlwt.easyxf(pattern: pattern solid, fore_colour 0x16')
        #ws.col(1).width = len('Text in cell') * 256
        current_row = 1
        question = ''
        for statistic in report.getSortedStatistics():
            if question != statistic.question.title and\
                report.getSortedStatistics().index(statistic) != 0:
                question = statistic.question.title
                state['ws'].write_merge(current_row, current_row, 0, 20, '', separator_style)
                current_row += 1
            elif question == statistic.question.title:
                state['ws'].write_merge(current_row, current_row, 1, 5, '', separator_style)
                current_row += 1
            state['current_row'] = current_row
            statistic.add_to_excel(state)
            current_row = state['current_row'] + 1
        shutil.rmtree(state['temp_folder'])
        #output = StringIO()
        output = tempfile.NamedTemporaryFile()
        wb.save(output)
        output.seek(0)
        return output.read()

    security.declareProtected(PERMISSION_VIEW_REPORTS, 'questionnaire_export')
    def questionnaire_export(self, report_id, REQUEST, answers=None):
        """ Exports the report in excel format """
        report = self.getReport(report_id)
        if not report:
            raise NotFound('Report %s' % (report_id,))
        assert excel_export_available
        if answers is None:
            answers = self.getAnswers()
        ret = self.generate_excel(report, answers=answers)
        content_type = 'application/vnd.ms-excel'
        filename = '%s Export.xls' % report.id

        if REQUEST is not None:
            filesize = len(ret)
            set_response_attachment(REQUEST.RESPONSE, filename,
                content_type, filesize)
        return ret

    #
    # utils
    #
    security.declareProtected(view, 'expired')
    def expired(self):
        """
        expired():
        -> true if the expiration date has been exceeded,
        -> false if the expiration date is still to be reached or
        if the survey allows posting after the expiration date.
        """


        if self.allow_overtime:
            return False
        now = DateTime()
        expire_date = DateTime(self.expirationdate) + 1
        return now.greaterThan(expire_date)

    security.declareProtected(view, 'get_days_left')
    def get_days_left(self):
        """ Returns the remaining days for the survey or the number of days before it starts """
        today = self.utGetTodayDate().earliestTime()
        if self.releasedate.lessThanEqualTo(today):
            return (1, int(str((self.expirationdate + 1) - today).split('.')[0]))
        else:
            return (0, int(str(self.releasedate - today).split('.')[0]))

    security.declarePublic('checkPermissionViewAnswers')
    def checkPermissionViewAnswers(self):
        """Check if the user has the VIEW_ANSWERS permission"""
        return self.checkPermission(PERMISSION_VIEW_ANSWERS) or self.checkPermissionPublishObjects()

    security.declarePublic('checkPermissionViewReports')
    def checkPermissionViewReports(self):
        """Check if the user has the VIEW_REPORTS permission"""
        return self.checkPermission(PERMISSION_VIEW_REPORTS)

    security.declarePublic('checkPermissionEditObjects')
    def checkPermissionEditObjects(self):
        """Check if the user has the EDIT_OBJECTS permission"""
        return self.checkPermission(PERMISSION_EDIT_OBJECTS)

    security.declarePublic('checkPermissionAddAnswer')
    def checkPermissionAddAnswer(self):
        """Check if the user has the ADD_ANSWER permission"""
        return self.checkPermission(PERMISSION_ADD_ANSWER)

    def checkPermissionEditAnswers(self):
        """ Check if the user has  EDIT_ANSWER permission"""
        return self.checkPermission(PERMISSION_EDIT_ANSWERS)

    #
    # Site pages
    #
    security.declareProtected(PERMISSION_VIEW_REPORTS, 'view_reports_html')
    view_reports_html = NaayaPageTemplateFile('zpt/questionnaire_view_reports',
                        globals(), 'NaayaSurvey.questionnaire_view_reports')

    security.declareProtected(PERMISSION_VIEW_ANSWERS, 'view_answers_html')
    view_answers_html = NaayaPageTemplateFile('zpt/questionnaire_view_answers',
                        globals(), 'NaayaSurvey.questionnaire_view_answers')

    manage_main = folder_manage_main_plus
    ny_before_listing = PageTemplateFile('zpt/questionnaire_manage_header',
                                         globals())

    security.declareProtected(view_management_screens,
                              'manage_create_validation_html')
    def manage_create_validation_html(self, REQUEST=None):
        """ create a blank validation_html template in this survey """
        datafile = os.path.join(os.path.dirname(__file__), 'www',
                             'initial_validation_html.txt')
        id = 'validation_html'
        title = "Custom questionnaire HTML"
        manage_addPageTemplate(self, id, title, open(datafile).read())
        if REQUEST is not None:
            url = self[id].absolute_url() + '/manage_workspace'
            REQUEST.RESPONSE.redirect(url)

    security.declareProtected(view_management_screens,
                              'manage_create_validation_onsubmit')
    def manage_create_validation_onsubmit(self, REQUEST=None):
        """ create a blank validation_onsubmit template in this survey """
        datafile = os.path.join(os.path.dirname(__file__), 'www',
                             'initial_validation_onsubmit.txt')
        id = 'validation_onsubmit'
        manage_addPythonScript(self, id)
        self._getOb(id).write(open(datafile, 'rb').read())
        if REQUEST is not None:
            url = self[id].absolute_url() + '/manage_workspace'
            REQUEST.RESPONSE.redirect(url)

    security.declarePublic('view_my_answer_html')
    def view_my_answer_html(self, REQUEST):
        """Display a page with the answer of the current user"""
        answer = self.getMyAnswer()
        if answer is None:
            raise NotFound("You haven't taken this survey") # TODO: replace with a proper exception/error message
        return answer.index_html(REQUEST=REQUEST)

    security.declareProtected(view_management_screens, 'manage_migrate')
    def manage_migrate(self, REQUEST, widget_id, convert_to):
        """ convert widget type """
        perform_migration(self, widget_id, convert_to)
        self.setSessionInfo(["Changed widget type for %r" % widget_id])
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_migrate_html')

    security.declareProtected(view_management_screens, 'manage_migrate_html')
    manage_migrate_html = PageTemplateFile('zpt/questionnaire_manage_migrate',
                                           globals())
    manage_migrate_html.available_migrations = available_migrations

    security.declareProtected('View management screens', 'manage_update_combo_answers_html')
    def manage_update_combo_answers_html(self, REQUEST=None):
        """ Update answer to questions based on combos
            for the case when the first option was not initially entered as
            'Please select'"""

        if not REQUEST.form.has_key('question_id'):
            return self._manage_update_combo_answers_html()
        question_id = REQUEST.get('question_id')
        errors = []
        question_ids = [question.id for question in self.objectValues('Naaya Combobox Widget')] + [question.id for question in self.objectValues('Naaya Combobox Matrix Widget')]

        if not question_id:
            errors.append('No question ID provided')
        elif question_id not in question_ids:
            errors.append('Invalid question ID')
        if errors:
            return self._manage_update_combo_answers_html(errors=errors)

        question = self._getOb(question_id)
        if question.meta_type == 'Naaya Combobox Widget':
            question.choices.insert(0, 'Please select')
            question._p_changed = True
            for answer in self.objectValues('Naaya Survey Answer'):
                the_choice = getattr(answer, question_id)
                setattr(answer, question_id, the_choice + 1)
        else:
            question.values.insert(0, 'Please select')
            question._p_changed = True
            for answer in self.objectValues('Naaya Survey Answer'):
                new_choices = []
                old_choices = getattr(answer, question_id)
                for choices_list in old_choices:
                    new_choices.append([value+1 for value in choices_list])
                setattr(answer, question_id, new_choices)

        return self._manage_update_combo_answers_html(success=True)

    _manage_update_combo_answers_html = PageTemplateFile('zpt/questionnaire_manage_update', globals())

    def _get_template(self, name):
        template = self._getOb(name, None)
        if template is not None:
            return template.render_email

        template = email_templates.get(name, None)
        if template is not None:
            return template.render_email

        raise ValueError('template for %r not found' % name)

    security.declareProtected(view_management_screens,
                              'manage_customizeTemplate')
    def manage_customizeTemplate(self, name, REQUEST=None):
        """ customize the email template called `name` """
        manage_addEmailPageTemplate(self, name,
            email_templates[name]._text)
        ob = self._getOb(name)

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(ob.absolute_url() + '/manage_workspace')
        else:
            return name

    customize_email_templates = PageTemplateFile('zpt/customize_emailpt', globals())
    customize_email_templates.email_templates = email_templates

InitializeClass(SurveyQuestionnaire)
