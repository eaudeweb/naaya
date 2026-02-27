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
# The Original Code is HelpDeskAgent version 1.0.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania for EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Dragos Chirila, Finsiel Romania

from OFS.Folder import Folder
from OFS.Image import cookId
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens,view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import types, time
from DateTime import DateTime

from Objects import *
from Toolz import *
from Constants import *


#####################################
#   ADD ISSUES FROM ZOPE CONSOLE    #
#####################################
manage_addIssueForm = PageTemplateFile('zpt/Issue_manage_addForm', globals())
def manage_addIssue(self, title=ISSUE_DEFAULT_TITLE,
    user_name=ANONYMOUS_USER_NAME, user_email='', user_phone='',
    subject='', category='', priority='',
    sendtype='', description='', security='',
    link='', attachment='', REQUEST=None):
    """Add a Issue from Zope"""
    #check for some "must" values
    if not subject:
        return getattr(self, 'manage_addIssueForm')(setFormError(REQUEST, 'subject', FORM_ERROR_SUBJECT_EMPTY))
    if not category:
        return getattr(self, 'manage_addIssueForm')(setFormError(REQUEST, 'category', FORM_ERROR_CATEGORY_EMPTY))
    if not description:
        return getattr(self, 'manage_addIssueForm')(setFormError(REQUEST, 'description', FORM_ERROR_DESCRIPTION_EMPTY))
    #add a new issue
    id = GenRandomKey(self.issue_ticket_length)
    title = subject
    if priority == '':
        priority = self.getIssueCategoryPriority(category)
    consultant = self.getIssueCategoryConsultant(category)
    status = self.getIssueStatusInit()
    if security !='':
        security = self.getIssuePrivate()
    else:
        security = self.getIssuePublic()
    date_open = DateTime()
    obj = Issue(id, title, date_open, consultant, user_name, user_email, user_phone,
            subject, category,
            sendtype, priority, status,
            description, link, security)
    obj.addAttachmentForIssue(attachment)
    self._setObject(id, obj)
    #add item to history
    obj.addIssueHistory(date_open, user_name, HISTORY_ISSUE_ADDED,
        self.getIssueStatusTitle(status),
        self.getIssuePriorityTitle(priority), '')
    #send email
    if self.notifyNewIssue():
        self.SendEmailNotifications(SENDEMAIL_HELPDESK_ALL, ACTION_ADD_ISSUE, id)
    #catalog issue
    self.CatalogIssue(obj)
    if REQUEST:
        return self.manage_main(self,REQUEST)


###############################
#   ADD ISSUES FROM WEB SITE  #
###############################
def AddIssue(self, title=ISSUE_DEFAULT_TITLE, user_name=ANONYMOUS_USER_NAME,
    user_email='', user_phone='',
    subject='', category='', priority='', sendtype='', description='',
    security='', link='', attachment='', REQUEST=None):
    """Add a issue from web site"""
    if addIssue(REQUEST):
        #check for some "must" values
        if not subject:
            return getattr(self, 'add_issue_html')(setFormError(REQUEST, 'subject', FORM_ERROR_SUBJECT_EMPTY))
        if not category:
            return getattr(self, 'add_issue_html')(setFormError(REQUEST, 'category', FORM_ERROR_CATEGORY_EMPTY))
        if not description:
            return getattr(self, 'add_issue_html')(setFormError(REQUEST, 'description', FORM_ERROR_DESCRIPTION_EMPTY))
        #add a new issue
        id = GenRandomKey(self.issue_ticket_length)
        if subject != '':
            title = subject
        if priority == '':
            priority = self.getIssueCategoryPriority(category)
        consultant = self.getIssueCategoryConsultant(category)
        status = self.getIssueStatusInit()
        # if "default issue confidentiality" is PRIVATE then the issue's security is PRIVATE
        # otherwise, depends on what the user has selected
        if self.isSecurityFlagPrivate():
            security = self.getIssuePrivate()
        else:
            if security !='':
                security = self.getIssuePrivate()
            else:
                security = self.getIssuePublic()
        date_open = DateTime()
        obj = Issue(id, title, date_open, consultant, user_name, user_email, user_phone,
                subject, category,
                sendtype, priority, status, description,
                link, security)
        obj.addAttachmentForIssue(attachment)
        self._setObject(id, obj)
        #add item to history
        obj.addIssueHistory(date_open, user_name, HISTORY_ISSUE_ADDED, self.getIssueStatusTitle(status), self.getIssuePriorityTitle(priority), '')
        #send email
        if self.notifyNewIssue():
            self.SendEmailNotifications(SENDEMAIL_HELPDESK_ALL, ACTION_ADD_ISSUE, id)
        #catalog issue
        self.CatalogIssue(obj)
        REQUEST.RESPONSE.redirect(str(self.absolute_url(0)) + '/?newissue=' + str(id))

def AddIssueQuick(self, title=ISSUE_QUICK_DEFAULT_TITLE, subject='', category='', priority='', description='', security='', link='', attachment='', REQUEST=None):
    """Add quick a issue from web site"""
    if addIssueQuick(REQUEST):
        #check for some "must" values
        if not subject:
            return getattr(self, 'add_issue_quick_html')(setFormError(REQUEST, 'subject', FORM_ERROR_SUBJECT_EMPTY))
        if not category:
            return getattr(self, 'add_issue_quick_html')(setFormError(REQUEST, 'category', FORM_ERROR_CATEGORY_EMPTY))
        if not description:
            return getattr(self, 'add_issue_quick_html')(setFormError(REQUEST, 'description', FORM_ERROR_DESCRIPTION_EMPTY))
        #add a new issue
        id = GenRandomKey(self.issue_ticket_length)
        if subject != '':
            title = subject
        if priority == '':
            priority = self.getIssueCategoryPriority(category)
        consultant = self.getIssueCategoryConsultant(category)
        status = self.getIssueStatusInit()
        # if "default issue confidentiality" is PRIVATE then the issue's security is PRIVATE
        # otherwise, depends on what the user has selected
        if self.isSecurityFlagPrivate():
            security = self.getIssuePrivate()
        else:
            if security !='':
                security = self.getIssuePrivate()
            else:
                security = self.getIssuePublic()
        date_open = DateTime()
        obj = Issue(id, title, date_open, consultant, '', '', '', subject, category, '', priority, status, description, link, security)
        obj.addAttachmentForIssue(attachment)
        self._setObject(id, obj)
        #add item to history
        obj.addIssueHistory(date_open, '', HISTORY_ISSUE_ADDED, self.getIssueStatusTitle(status), self.getIssuePriorityTitle(priority), '')
        #send email
        if self.notifyNewIssue():
            self.SendEmailNotifications(SENDEMAIL_HELPDESK_ALL, ACTION_ADD_ISSUE, id)
        #catalog issue
        self.CatalogIssue(obj)
        REQUEST.RESPONSE.redirect(str(self.absolute_url(0)) + '/?newissue=' + str(id))


class Issue(Folder):
    """Issue Object"""

    product_name = NAAYAHELPDESKAGENT_PRODUCT_NAME
    meta_type = ISSUE_META_TYPE_LABEL
    icon = 'misc_/NaayaHelpDeskAgent/Issue'

    manage_options = (
        Folder.manage_options
        +
        (
            {'label': ISSUE_MANAGE_OPTION_PROPERTIES, 'action': 'edit_manage_html',},
            {'label': ISSUE_MANAGE_OPTION_COMMENTS, 'action':'comments_manage_html',},
            {'label': ISSUE_MANAGE_OPTION_HISTORY, 'action': 'history_manage_html',},
        )
    )

    meta_types = ()
    all_meta_types = meta_types

    #security stuff
    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    # security property ->
    #       - 0: private
    #       - 1: public
    def __init__(self, id, title, date_open, consultant, user_name, user_email, user_phone,
        subject, category, sendtype, priority,
        status, description, link, security):
        """Inits with default values"""
        self.id = id
        self.date_open = date_open
        self.date_close = ''
        self.solution_time = ''
        self.updateIssueProperties(title, date_open, consultant, user_name,
            user_email, user_phone, subject,
            category, sendtype, priority, status, description,
            link, security)
        self.__issuecomment = {}
        self.__historycounter = 1
        self.__issuehistory = {}

    def _setModifyTime(self, newtime):
        """Update date_modify"""
        self.date_modify = newtime

    def updateIssueProperties(self, title, date_modify, consultant,
        user_name, user_email, user_phone,
        subject, category, sendtype, priority, status, description,
        link, security):
        """Set/update Issue properties"""
        self.title = title
        self.date_modify = date_modify
        self.consultant = consultant
        self.user_name = user_name
        self.user_email = user_email
        self.user_phone = user_phone
        self.subject = subject
        self.category = category
        self.sendtype = sendtype
        self.priority = priority
        self.status = status
        self.description = description
        self.link = link
        self.security = security

    def addAttachmentForIssue(self, attachment):
        """Add an attachment to comment"""
        if attachment != '':
            if attachment.filename != '':
                #upload file
                attachmentId, attachmentTitle = cookId(None, None, attachment)
                attachmentId = str(self.id) + '_' + attachmentId
                attachmentTitle = ATTACHMENT_FOR_ISSUE_LABEL
                self.manage_addFile(attachmentId, attachment, attachmentTitle)

    def updAttachmentForIssue(self, attachment):
        """Updates the attachment"""
        if attachment.filename != '':
            #upload file
            obj = self.getAttachmentForIssue()[0]
            if obj:
                obj.manage_upload(attachment)
            else:
                self.addAttachmentForIssue(attachment)

    def getAttachmentForIssue(self):
        """Test if there is an attachment for this issue"""
        ret = None, ''
        issueId = str(self.id)
        for attId in self.objectIds():
            if issueId == str(attId)[0:len(issueId)]:
                ret = getattr(self, attId), str(attId)[len(issueId)+1:]
                break
        return ret

    def getIssueComment(self, oId):
        """Get a IssueComment object by id"""
        try: return self.__issuecomment[oId]
        except: return None

    def getListIssueComment(self):
        """Get the list of IssueComment objects"""
        return self.__issuecomment.values()

    def issuecomments(self):
        """ For catalog """
        return ' '.join(map(lambda x: x.content, self.__issuecomment.values()))

    def addIssueComment(self, oId, obj):
        """Add a new IssueComment object"""
        self.__issuecomment[oId] = obj
        self._setModifyTime(DateTime())
        self._p_changed = 1

    def updateIssueComment(self, oId, oDate, oUsername, oContent):
        """Update a IssueComment object"""
        try:
            obj = self.__issuecomment[oId]
        except:
            pass
        else:
            obj.date = oDate
            obj.username = oUsername
            obj.content = oContent
            self.__issuecomment[oId] = obj
            self._setModifyTime(DateTime())
            self._p_changed = 1

    def deleteIssueComment(self, oIds):
        """Delete IssueComment objects"""
        for oId in ConvertToList(oIds):
            try:
                del(self.__issuecomment[oId])
                #handle attachment
                self.delAttachmentForComment(oId)
                self._setModifyTime(DateTime())
            except:
                pass
        self._p_changed = 1

    def addAttachmentForComment(self, attachment, commentId):
        """Add an attachment to comment"""
        if attachment.filename != '':
            #upload file
            attachmentId, attachmentTitle = cookId(None, None, attachment)
            attachmentId = str(commentId) + '_' + attachmentId
            attachmentTitle = ATTACHMENT_FOR_COMMENT_LABEL + str(commentId)
            self.manage_addFile(attachmentId, attachment, attachmentTitle)

    def getAttachmentForComment(self, commentId):
        """Test if there is an attachment with this id"""
        ret = None, ''
        commentId = str(commentId)
        for attId in self.objectIds():
            if commentId == str(attId)[0:len(commentId)]:
                ret = getattr(self, attId), str(attId)[len(commentId)+1:]
                break
        return ret

    def delAttachmentForComment(self, commentId):
        """Delete the attachment for comment if it exists"""
        commentId = str(commentId)
        for attId in self.objectIds():
            if commentId == str(attId)[0:len(commentId)]:
                self.manage_delObjects(attId)
                ret = getattr(self, attId), str(attId)[len(commentId)+1:]
                break

    def getIssueHistory(self, oId):
        """Get a IssueHistory object by id"""
        try: return self.__issuehistory[oId]
        except: return None

    def getListIssueHistory(self):
        """Get the list of IssueHistory objects"""
        return self.__issuehistory.values()

    def addIssueHistory(self, date, username, action, status, priority, consultant, comments=''):
        """Add a new IssueHistory object"""
        obj = IssueHistory(self.__historycounter, date, username, action, status, priority, consultant, comments)
        self.__issuehistory[self.__historycounter] = obj
        self.__historycounter = self.__historycounter + 1
        self._p_changed = 1

    def clearIssueHistory(self):
        """Clear history"""
        self.__issuehistory = {}
        self.__historycounter = 1
        self._p_changed = 1

    security.declareProtected(PERMISSION_MANAGE_HELPDESK_SETTINGS, 'manageIssueProperties')
    def manageIssueProperties(self, REQUEST=None):
        """Edit current Issue object properties"""
        local_roles = REQUEST.AUTHENTICATED_USER.getRolesInContext(self)
        if ('Manager' in local_roles) or (HELPDESK_ROLE_ADMINISTRATOR in local_roles) or (HELPDESK_ROLE_CONSULTANT in local_roles):
            if updateObjectAction(REQUEST):
                #update properties
                date_modify = DateTime()
                consultant = REQUEST.get('consultant', self.consultant)
                user_name = REQUEST.get('user_name', '')
                user_email = REQUEST.get('user_email', '')
                user_phone = REQUEST.get('user_phone', '')
                subject = REQUEST.get('subject', '')
                category = REQUEST.get('category', '')
                priority = REQUEST.get('priority', '')
                sendtype = REQUEST.get('sendtype', '')
                status = REQUEST.get('status', '')
                description = REQUEST.get('description', '')
                link = REQUEST.get('link', '')
                comments = REQUEST.get('comments', '')
                if REQUEST.has_key('security'):
                    security = self.getIssuePrivate()
                else:
                    security = self.getIssuePublic()
                self.updateIssueProperties(subject, date_modify, consultant, user_name, user_email, user_phone, subject, category, sendtype, priority, status, description, link, security)
                #upload file
                attachment = REQUEST.get('attachment', '')
                self.updAttachmentForIssue(attachment)
                #add item to history
                self.addIssueHistory(date_modify, self.REQUEST.AUTHENTICATED_USER.getUserName(), HISTORY_ISSUE_MODIFIED, self.getIssueStatusTitle(status), self.getIssuePriorityTitle(priority), consultant, comments)
                #create a comment
                if comments != '':
                    oId = GenRandomKey()
                    oDate = DateTime()
                    oUsername = self.getUserName(self.getAuthenticatedUser())
                    obj = IssueComment(oId, oDate, oUsername, 1, comments)
                    self.addIssueComment(oId, obj)
                #send email
                if self.notifyModifyIssue():
                    self.SendEmailNotifications(SENDEMAIL_HELPDESK_ALL, ACTION_UPDATE_ISSUE, self.id)
                #catalog issue
                self.aq_parent.RecatalogIssue(self)
        #go back to comments page
        REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(PERMISSION_POST_COMMENTS, 'manageIssueComment')
    def manageIssueComment(self, REQUEST=None):
        """Manage IssueComment objects"""
        if self.getIssueStatusFinal() != self.status:
            #the issue is not in the final state
            if addObjectAction(REQUEST):
                #add a new IssueComment object
                oId = GenRandomKey()
                oDate = DateTime()
                oUsername = REQUEST.get('username', ANONYMOUS_USER_NAME)
                try:
                    oContentType = int(REQUEST.get('content_type', 1))
                except:
                    oContentType = 1
                oContent = REQUEST.get('content', '')
                obj = IssueComment(oId, oDate, oUsername, oContentType, oContent)
                # handle attachment
                if self.isAuthenticated():
                    oAttachment = REQUEST.get('attachment', '')
                    self.addAttachmentForComment(oAttachment, oId)
                self.addIssueComment(oId, obj)
                #add item to history
                self.addIssueHistory(oDate, oUsername, HISTORY_COMMENT_ADDED, self.getIssueStatusTitle(self.status), self.getIssuePriorityTitle(self.priority), self.consultant)
                #email stuff
                eAction = ACTION_ADD_COMMENT
            elif updateObjectAction(REQUEST):
                #update a IssueComment object
                oId = REQUEST.get('id', '')
                oDate = DateTime()
                oUsername = REQUEST.get('username', ANONYMOUS_USER_NAME)
                oContent = REQUEST.get('content', '')
                self.updateIssueComment(oId, oDate, oUsername, oContent)
                #add item to history
                self.addIssueHistory(oDate, oUsername, HISTORY_COMMENT_MODIFIED, self.getIssueStatusTitle(self.status), self.getIssuePriorityTitle(self.priority), self.consultant)
                #email stuff
                eAction = ACTION_UPDATE_COMMENT
            elif deleteObjectAction(REQUEST):
                #delete IssueComment objects
                oIds = REQUEST.get('ids', [])
                oContent = ''
                self.deleteIssueComment(oIds)
                #add item to history
                self.addIssueHistory(DateTime(), self.REQUEST.AUTHENTICATED_USER, HISTORY_COMMENT_DELETED, self.getIssueStatusTitle(self.status), self.getIssuePriorityTitle(self.priority), self.consultant)
                #email stuff
                eAction = ACTION_DELETE_COMMENT
            #send email
            if self.notifyModifyIssue():
                self.SendEmailNotifications(SENDEMAIL_HELPDESK_ALL, eAction, self.id, oContent)
            #catalog issue
            self.aq_parent.RecatalogIssue(self)
        #go back to comments page
        REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(PERMISSION_MANAGE_HELPDESK_SETTINGS, 'manageIssueHistory')
    def manageIssueHistory(self, REQUEST=None):
        """Manage IssueHistory"""
        local_roles = REQUEST.AUTHENTICATED_USER.getRolesInContext(self)
        if ('Manager' in local_roles) or (HELPDESK_ROLE_ADMINISTRATOR in local_roles) or (HELPDESK_ROLE_CONSULTANT in local_roles):
            if deleteObjectAction(REQUEST):
                #clear IssueHistory object
                self.clearIssueHistory()
        #go back to history page
        REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declareProtected(view, 'manageFeedback')
    def manageFeedback(self, REQUEST=None):
        """Send feedback and create a comment"""
        oFrom = REQUEST.get('from', ANONYMOUS_USER_NAME)
        oContent = REQUEST.get('content', '')
        try:
            oContentType = int(REQUEST.get('content_type', 1))
        except:
            oContentType = 1
        oHttpReferer = REQUEST.get('httpreferer', 'index_html')
        #send email
        self.SendEmail(oContent, self.user_email, oFrom, HELPDESK_DEFAULT_FEEDBACK_EMAIL_SUBJECT)
        if REQUEST.has_key('comment'):
            #add a new IssueComment object
            oId = GenRandomKey()
            oDate = DateTime()
            obj = IssueComment(oId, oDate, oFrom, oContentType, oContent)
            self.addIssueComment(oId, obj)
            #add item to history
            self.addIssueHistory(oDate, oFrom, HISTORY_COMMENT_ADDED, self.getIssueStatusTitle(self.status), self.getIssuePriorityTitle(self.priority), self.consultant)
            #send email
            if self.notifyModifyIssue():
                self.SendEmailNotifications(SENDEMAIL_HELPDESK_ALL, ACTION_ADD_COMMENT, self.id, oContent)
        #catalog issue
        self.aq_parent.RecatalogIssue(self)
        #go back
        REQUEST.RESPONSE.redirect(oHttpReferer)

    def EncodeTextareaContent(self, content):
        """Encode a textarea content:
                - encode content
                - replace \n with <br>"""
        return TEXTAREAEncode(content)

    #############
    # SECURITY  #
    #############
    def isPublic(self):
        """Test if current issue is public"""
        return self.getHelpDeskAgent().isPublic(self)

    def isPrivate(self):
        """Test if current issue is private"""
        return self.getHelpDeskAgent().isPrivate(self)

    def checkPermissionPostComments(self):
        """
        Check the right to post comments to issues.
        """
        return getSecurityManager().checkPermission(PERMISSION_POST_COMMENTS, self) is not None

    ########################################
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/Issue_index', globals())

    security.declareProtected(view, 'menu_html')
    menu_html = PageTemplateFile('zpt/Issue_menu', globals())

    security.declareProtected(view, 'footer_html')
    footer_html = PageTemplateFile('zpt/Issue_footer', globals())

    security.declareProtected(view, 'feedback_html')
    feedback_html = PageTemplateFile('zpt/Issue_feedback', globals())

    security.declareProtected(PERMISSION_MANAGE_HELPDESK_SETTINGS, 'edit_form_html')
    edit_form_html = PageTemplateFile('zpt/Issue_edit_form', globals())

    security.declareProtected(PERMISSION_MANAGE_HELPDESK_SETTINGS, 'edit_user_html')
    edit_user_html = PageTemplateFile('zpt/Issue_edit_user', globals())

    security.declareProtected(view_management_screens, 'edit_manage_html')
    edit_manage_html = PageTemplateFile('zpt/Issue_edit_manage', globals())

    security.declareProtected(PERMISSION_POST_COMMENTS, 'comments_form_html')
    comments_form_html = PageTemplateFile('zpt/Issue_comments_form', globals())

    security.declareProtected(PERMISSION_POST_COMMENTS, 'comments_user_html')
    comments_user_html = PageTemplateFile('zpt/Issue_comments_user', globals())

    security.declareProtected(view_management_screens, 'comments_manage_html')
    comments_manage_html = PageTemplateFile('zpt/Issue_comments_manage', globals())

    security.declareProtected(PERMISSION_MANAGE_HELPDESK_SETTINGS, 'history_form_html')
    history_form_html = PageTemplateFile('zpt/Issue_history_form', globals())

    security.declareProtected(PERMISSION_MANAGE_HELPDESK_SETTINGS, 'history_user_html')
    history_user_html = PageTemplateFile('zpt/Issue_history_user', globals())

    security.declareProtected(view_management_screens, 'history_manage_html')
    history_manage_html = PageTemplateFile('zpt/Issue_history_manage', globals())

    security.setPermissionDefault(PERMISSION_MANAGE_HELPDESK_SETTINGS, [HELPDESK_ROLE_ADMINISTRATOR, HELPDESK_ROLE_CONSULTANT])

InitializeClass(Issue)
