# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web

# Python imports
import sys
from urllib import urlencode

# Zope imports
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from DateTime import DateTime
from Globals import InitializeClass
from OFS.Traversable import path2url
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZPublisher import BadRequest, InternalError, NotFound
from ZPublisher.HTTPRequest import FileUpload
from zLOG import LOG, ERROR, DEBUG

# Product imports
from Products.Naaya.constants import DEFAULT_SORTORDER
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyImageContainer import NyImageContainer
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.constants import \
     EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG, \
     MESSAGE_SAVEDCHANGES, PERMISSION_EDIT_OBJECTS
from Products.NaayaCore.managers.utils import genObjectId, genRandomId
from Products.NaayaCore.managers import recaptcha_utils
from Products.NaayaWidgets.Widget import WidgetError

from SurveyAnswer import manage_addSurveyAnswer, SurveyAnswer
from SurveyReport import manage_addSurveyReport
from permissions import *
from questionnaire_item import questionnaire_item

class SurveyQuestionnaireException(Exception):
    """Survey related exception"""
    pass

def manage_addSurveyQuestionnaire(context, id='', title='', lang=None, REQUEST=None, **kwargs):
    """ """
    if not title:
        title = 'Survey Instance'
    if not id:
        id = genObjectId(title)

    idSuffix = ''
    while id+idSuffix in context.objectIds():
        idSuffix = genRandomId(p_length=4)
    id = id + idSuffix

    # Get selected language
    lang = REQUEST and REQUEST.form.get('lang', None)
    lang = lang or kwargs.get('lang', context.gl_get_selected_language())

    if REQUEST:
        kwargs.update(REQUEST.form)
    kwargs['releasedate'] = context.process_releasedate(kwargs.get('releasedate', DateTime()))
    kwargs['expirationdate'] = context.process_releasedate(kwargs.get('expirationdate', DateTime()))
    contributor = context.REQUEST.AUTHENTICATED_USER.getUserName()
    #log post date
    auth_tool = context.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)

    kwargs['id'] = id
    kwargs.setdefault('title', title)
    kwargs.setdefault('lang', lang)

    ob = SurveyQuestionnaire(**kwargs)
    context.gl_add_languages(ob)
    context._setObject(id, ob)

    ob = context._getOb(id)
    ob.updatePropertiesFromGlossary(lang)
    ob.submitThis()
    context.recatalogNyObject(ob)

    # Return
    if not REQUEST:
        return id
    #redirect if case
    if REQUEST.has_key('submitted'): ob.submitThis()
    l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if l_referer == 'questionnaire_manage_add' or l_referer.find('questionnaire_manage_add') != -1:
        return context.manage_main(context, REQUEST, update_menu=1)
    elif l_referer == 'questionnaire_add_html':
        context.setSession('referer', context.absolute_url())
        REQUEST.RESPONSE.redirect('%s/messages_html' % context.absolute_url())

class SurveyQuestionnaire(NyAttributes, questionnaire_item, NyContainer):
    """ """
    meta_type = "Naaya Survey Questionnaire"
    meta_label = "Survey Instance"
    icon = 'misc_/NaayaSurvey/NySurveyQuestionnaire.gif'
    icon_marked = 'misc_/NaayaSurvey/NySurveyQuestionnaire_marked.gif'

    _constructors = (manage_addSurveyQuestionnaire,)

    all_meta_types = ()

    manage_options=(
        {'label':'Contents', 'action':'manage_main',
          'help':('OFSP','ObjectManager_Contents.stx')},
        {'label':'Properties', 'action':'manage_propertiesForm',
         'help':('OFSP','Properties.stx')},
        {'label':'View', 'action':'index_html'},
        {'label':'Security', 'action':'manage_access',
         'help':('OFSP', 'Security.stx')},
      )

    security = ClassSecurityInfo()

    notify_owner = True
    notify_respondents = 'LET_THEM_CHOOSE_YES'

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

        self.allow_overtime = int(kwargs.get('allow_overtime', '0'))
        self.save_properties(**kwargs)
        self.updatePropertiesFromGlossary(lang)
        self.recatalogNyObject(self)

        if REQUEST:
            # Log date
            contributor = REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            # Redirect
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
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

    security.declareProtected(view, 'getSurveyTemplate')
    def getSurveyTemplate(self):
        """Return the survey template used for this questionnaire"""
        stool = self.portal_survey
        return getattr(stool, self._survey_template)

    security.declareProtected(view, 'getSurveyTemplateId')
    def getSurveyTemplateId(self):
        """Return survey template id; used by the catalog tool."""
        stype = self.getSurveyTemplate()
        if not stype:
            return ''
        return stype.getId()

    #
    # Answer edit methods
    #
    security.declareProtected(PERMISSION_ADD_ANSWER, 'addSurveyAnswer')
    def addSurveyAnswer(self, REQUEST=None, notify_respondent=False, **kwargs):
        """Add someone's answer"""
        try:
            if self.expired():
                raise SurveyQuestionnaireException("The survey has expired")
        except SurveyQuestionnaireException, ex:
            if REQUEST:
                self.setSessionErrors([ex])
                return REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())
            else:
                raise

        datamodel = {}
        errors = []
        for widget in self.getSurveyTemplate().getWidgets():
            try:
                value = widget.getDatamodel(REQUEST.form)
                widget.validateDatamodel(value)
                datamodel[widget.getWidgetId()] = value
            except WidgetError, ex:
                if not REQUEST:
                    raise
                datamodel[widget.getWidgetId()] = None
                errors.append(ex)

        if errors or not recaptcha_utils.is_valid_captcha(self, REQUEST):
            if errors:
                self.setSessionErrors(errors)
            self.setSessionAnswer(datamodel)
            self.setSession('notify_respondent', notify_respondent)
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())
            return

        old_answer = self.getMyAnswer()
        if old_answer is not None:
            self._delObject(old_answer.id)
            LOG('NaayaSurvey.SurveyQuestionnaire', DEBUG, 'Deleted previous answer %s' % (old_answer.absolute_url()))

        answer_id = manage_addSurveyAnswer(self, datamodel, REQUEST=REQUEST)
        answer = self._getOb(answer_id)
        if self.notify_owner:
            self.sendNotificationToOwner(answer)
        if self.notify_respondents == 'ALWAYS' or \
           self.notify_respondents.startswith('LET_THEM_CHOOSE') and notify_respondent:
            self.sendNotificationToRespondent(answer)
        self.delSessionKeys(datamodel.keys())

        if REQUEST:
            self.setSession('title', 'Thank you for taking the survey')
            self.setSession('body', '')
            self.setSession('referer', self.aq_parent.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        return answer_id

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

        d = {}
        d['NAME'] = auth_tool.getUserFullName(owner)
        d['RESPONDENT'] = "User %s" % auth_tool.getUserFullName(respondent)
        d['SURVEY_TITLE'] = self.title
        d['SURVEY_URL'] = self.absolute_url()
        d['LINK'] = answer.absolute_url()

        self._sendEmailNotification('email_survey_answer', d, owner)

    security.declarePrivate('sendNotificationToRespondent')
    def sendNotificationToRespondent(self, answer):
        """Send an email notification about the newly added answer to the respondent.
            If the respondent is an anonymous user no notification will be sent.

            @param answer: the answer object that was added (unsed for the moment)
            @type answer: SurveyAnswer
        """
        if self.isAnonymousUser():
            return

        owner = self.getOwner()
        respondent = self.REQUEST.AUTHENTICATED_USER
        auth_tool = self.getSite().getAuthenticationTool()

        d = {}
        d['NAME'] = auth_tool.getUserFullName(respondent)
        d['SURVEY_TITLE'] = self.title
        d['SURVEY_URL'] = self.absolute_url()
        d['LINK'] = "%s" % answer.absolute_url()

        self._sendEmailNotification('email_survey_answer_to_respondent', d, respondent)

    security.declarePrivate('_sendEmailNotification')
    def _sendEmailNotification(self, template_name, d, recipient):
        """Send an email notification.

            @param template_name: name of the email template
            @type template_name: string
            @param d: dictionary with the values used in the template
            @type d: dict
            @param recipient: recipient
            @type recipient: Zope User
        """
        auth_tool = self.getSite().getAuthenticationTool()
        email_tool = self.getSite().getEmailTool()
        template = email_tool._getOb(template_name)
        sender_email = self.getNotificationTool().from_email
        try:
            recp_email = auth_tool.getUserEmail(recipient)
            email_tool.sendEmail(template.body % d,
                                 recp_email,
                                 sender_email,
                                 template.title)
            LOG('NaayaSurvey.SurveyQuestionnaire', DEBUG, 'Notification sent from %s to %s' % (sender_email, recp_email))
        except:
            # possible causes - the recipient doesn't have email (e.g. regular Zope user)
            #                 - we can not send the email
            # these aren't fatal errors, so we'll just log the error
            err = sys.exc_info()
            LOG('NaayaSurvey.SurveyQuestionnaire', ERROR, 'Could not send email notification for survey %s' % (self.absolute_url(),), error=err)

    #
    # Answer read methods
    #
    security.declareProtected(PERMISSION_VIEW_ANSWERS, 'getAnswers')
    def getAnswers(self):
        """Return a list of answers"""
        return self.objectValues(SurveyAnswer.meta_type)

    # this is method is used by the widget manage forms
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'getAnswerCountForQuestion')
    def getAnswerCountForQuestion(self, question_id, exclude_None=False):
        """Return the count of answers for question_id, excluding None ones if exclude_None if True."""
        L = [answer.get(question_id) for answer in self.getAnswers()]
        if exclude_None:
            L = [x for x in L if x is not None]
        return len(L)

    security.declarePublic('getMyAnswer')
    def getMyAnswer(self):
        """Return the answer of the current user or None if it doesn't exist.

            If multiple answers exist, only the first one is returned.
        """
        if self.isAnonymousUser():
            return None
        respondent = self.REQUEST.AUTHENTICATED_USER.getUserName()
        catalog = self.getCatalogTool()
        for brain in catalog({'path': path2url(self.getPhysicalPath()),
                              'meta_type': SurveyAnswer.meta_type,
                              'respondent': respondent}):
            return brain.getObject()
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
        report = self.getSurveyTemplate().getReport(report_id)
        if not report:
            raise NotFound('Report %s' % (report_id,))
        return report.view_report_html(answers=self.getAnswers())

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
        expire_date = DateTime(self.expirationdate)
        return now.greaterThan(expire_date)

    security.declareProtected(view, 'get_days_left')
    def get_days_left(self):
        """ Returns the remaining days for the survey or the number of days before it starts """
        today = self.utGetTodayDate().earliestTime()
        if self.releasedate.lessThanEqualTo(today):
            return (1, int(str(self.expirationdate - today).split('.')[0]))
        else:
            return (0, int(str(self.releasedate - today).split('.')[0]))

    security.declarePublic('checkPermissionViewAnswers')
    def checkPermissionViewAnswers(self):
        """Check if the user has the VIEW_ANSWERS permission"""
        return self.checkPermission(PERMISSION_VIEW_ANSWERS) and self.checkPermissionPublishObjects()

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

    #
    # Site pages
    #
    security.declareProtected(PERMISSION_ADD_QUESTIONNAIRE, 'questionnaire_add_html')
    questionnaire_add_html = PageTemplateFile('zpt/questionnaire_add', globals())

    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/questionnaire_index', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/questionnaire_edit', globals())

    security.declareProtected(PERMISSION_VIEW_REPORTS, 'view_reports_html')
    view_reports_html = PageTemplateFile('zpt/questionnaire_view_reports', globals())

    security.declareProtected(PERMISSION_VIEW_ANSWERS, 'view_answers_html')
    view_answers_html = PageTemplateFile('zpt/questionnaire_view_answers', globals())

    security.declarePublic('view_my_answer_html')
    def view_my_answer_html(self, REQUEST):
        """Display a page with the answer of the current user"""
        answer = self.getMyAnswer()
        if answer is None:
            raise NotFound("You haven't taken this survey") # TODO: replace with a proper exception/error message
        return answer.index_html(REQUEST=REQUEST)

    #
    # macros & other html snippets
    #
    security.declareProtected(view, 'base_index_html')
    base_index_html = PageTemplateFile('zpt/base_questionnaire_index', globals())

    security.declareProtected(view, 'showCaptcha')
    def showCaptcha(self):
        """Return HTML code for CAPTCHA"""
        return recaptcha_utils.render_captcha(self)

InitializeClass(SurveyQuestionnaire)
