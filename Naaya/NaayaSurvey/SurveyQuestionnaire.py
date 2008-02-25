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
from zLOG import LOG, ERROR, DEBUG
from OFS.Traversable import path2url
from Acquisition import Implicit
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZPublisher import BadRequest, InternalError, NotFound
from ZPublisher.HTTPRequest import FileUpload

# Product imports
from Products.NaayaWidgets.Widget import WidgetError
from SurveyAnswer import manage_addSurveyAnswer, SurveyAnswer
from questionnaire_item import questionnaire_item
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyImageContainer import NyImageContainer
from Products.NaayaBase.NyCheckControl import NyCheckControl

from constants import *
from Products.NaayaBase.constants import \
     EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG, \
     MESSAGE_SAVEDCHANGES, PERMISSION_EDIT_OBJECTS

from SurveyReport import manage_addSurveyReport
from statistics.SimpleTabularStatistics import SimpleTabularStatistics
from statistics.MultipleChoiceTabularStatistics import MultipleChoiceTabularStatistics


def manage_addSurveyQuestionnaire(context, id='', title='', lang=None, REQUEST=None, **kwargs):
    """ """
    util = utils()
    if not title:
        title = 'Questionnaire'
    if not id:
        id = util.utGenObjectId(title)

    idSuffix = ''
    while id+idSuffix in context.objectIds():
        idSuffix = util.utGenRandomId(p_length=4)
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

    kwargs.setdefault('id', id)
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
    meta_label = "Survey"
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

    _survey_type = None

    def __init__(self, id, survey_type, lang=None, **kwargs):
        self.id = id
        self._survey_type = survey_type

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

        kwargs.setdefault('title', kwargs.get('title', ''))
        kwargs.setdefault('description', kwargs.get('description', ''))
        kwargs.setdefault('keywords', kwargs.get('keywords', ''))
        kwargs.setdefault('coverage', kwargs.get('coverage', ''))
        kwargs.setdefault('sortorder', kwargs.get('sortorder', 100))

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
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #
    # Self read mehtods
    #
    security.declarePublic('expired')
    def expired(self):
        """ """
        now = DateTime()
        expire_date = DateTime(self.expirationdate)
        return now.greaterThan(expire_date)

    def checkPermissionViewAnswers(self):
        """Check if the user has the VIEW_ANSWERS permission"""
        return self.checkPermission(PERMISSION_VIEW_ANSWERS)

    def checkPermissionViewReports(self):
        """Check if the user has the VIEW_REPORTS permission"""
        return self.checkPermission(PERMISSION_VIEW_REPORTS)

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
        """ return survey template"""
        stool = self.portal_survey
        stype = getattr(stool, self._survey_type, None)
        return stype

    security.declareProtected(view, 'getSurveyTemplateId')
    def getSurveyTemplateId(self):
        """ return survey template id"""
        stype = self.getSurveyTemplate()
        if not stype:
            return ''
        return stype.getId()

    security.declareProtected(view, 'getSurveyTemplateLabel')
    def getSurveyTemplateLabel(self):
        """ Return label """
        stype = self.getSurveyTemplate()
        if stype:
            return stype.title
        return ''

    security.declareProtected(view, 'getSurveyTemplateDescription')
    def getSurveyTemplateDescription(self):
        """ Return description """
        stype = self.getSurveyTemplate()
        if stype:
            return stype.description
        return ''

    #
    # Answer edit methods
    #
    security.declareProtected(PERMISSION_ADD_ANSWER, 'addSurveyAnswer')
    def addSurveyAnswer(self, REQUEST=None, **kwargs):
        """ """
        if self.getMySurveyAnswer():
            raise Exception("You have already answered")
        datamodel = {}
        errors = []
        for widget in self.getSurveyTemplate().getWidgets():
            try:
                value = widget.getDatamodel(REQUEST.form)
                widget.validateDatamodel(value)
                datamodel[widget.getWidgetId()] = value
            except WidgetError, ex:
                datamodel[widget.getWidgetId()] = None
                errors.append(ex)

        if errors:
            if not REQUEST:
                raise WidgetError(', '.join([i for i in str(errors)]))
            self.setSessionErrors(errors)
            for widget, value in datamodel.items():
                if value is None:
                    continue
                if isinstance(value, FileUpload):
                    continue
                self.setSession(widget, value)
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())
            return

        answer_id = manage_addSurveyAnswer(self, datamodel, REQUEST=REQUEST)
        self._sendNotifications(self._getOb(answer_id))
        self.delSessionKeys(datamodel.keys())

        if REQUEST:
            self.setSession('title', 'Thank you for taking the survey')
            self.setSession('body', '')
            self.setSession('referer', self.aq_parent.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        return answer_id

    def _sendNotifications(self, answer):
        """Send email notifications about the newly added answer.

                @param answer: the answer object that was added
        """
        owner = self.getOwner()
        auth_tool = self.getSite().getAuthenticationTool()
        email_tool = self.getSite().getEmailTool()
        template = email_tool._getOb('email_survey_answer')

        # compose email
        d = {}
        d['NAME'] = auth_tool.getUserFullName(owner)
        respondent = self.REQUEST.AUTHENTICATED_USER
        d['RESPONDENT'] = "User %s" % auth_tool.getUserFullName(respondent)
        d['SURVEY_TITLE'] = self.title
        d['SURVEY_URL'] = self.absolute_url()
        d['LINK'] = answer.absolute_url()
        content = template.body % d

        # send email
        sender_email = self.getNotificationTool().from_email
        try:
            recp_email = auth_tool.getUserEmail(owner)
            email_tool.sendEmail(content, recp_email, sender_email, template.title)
            LOG('Products.NaayaSurvey.SurveyQuestionnaire', DEBUG, 'Notification sent from %s to %s' % (sender_email, recp_email))
        except:
            # possible causes - the owner doesn't have email (e.g. regular Zope user)
            #                 - we can not send the email
            # these aren't fatal errors, so we'll just log the error
            err = sys.exc_info()
            LOG('Products.NaayaSurvey.SurveyQuestionnaire', ERROR, 'Could not send notifications', error=err)

    #
    # Answer read methods
    #
    security.declareProtected(PERMISSION_VIEW_ANSWERS, 'getAnswers')
    def getAnswers(self):
        # Return answers
        return self.objectValues(SurveyAnswer.meta_type)

    security.declarePublic('getMySurveyAnswer')
    def getMySurveyAnswer(self):
        """Return the answer of the current user or None if it doesn't exist

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

    security.declareProtected(PERMISSION_VIEW_REPORTS, 'questionnaire_view_report_html')
    def questionnaire_view_report_html(self, report_id, REQUEST):
        """View the report report_id"""
        report = self.getSurveyTemplate().getReport(report_id)
        if not report:
            raise NotFound('Report %s' % (report_id,))
        return report.view_report_html(answers=self.getAnswers())

    # site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/questionnaire_index', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    edit_html = PageTemplateFile('zpt/questionnaire_edit', globals())

    security.declareProtected(PERMISSION_ADD_QUESTIONNAIRE, 'questionnaire_add_html')
    questionnaire_add_html = PageTemplateFile('zpt/questionnaire_add', globals())

    security.declarePublic('view_reports_html')
    view_reports_html = PageTemplateFile('zpt/questionnaire_view_reports', globals())

    security.declarePublic('view_answers_html')
    view_answers_html = PageTemplateFile('zpt/questionnaire_view_answers', globals())

InitializeClass(SurveyQuestionnaire)
