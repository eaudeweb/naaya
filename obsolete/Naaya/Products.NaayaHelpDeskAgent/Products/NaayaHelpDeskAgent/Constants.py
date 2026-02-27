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


import Globals

# define some constants

NAAYAHELPDESKAGENT_PRODUCT_NAME = 'NaayaHelpDeskAgent'
NAAYAHELPDESKAGENT_PRODUCT_PATH = Globals.package_home(globals())

#ini file headers
INIFILE_ISSUE_PRIORITY = 'IssuePriority'
INIFILE_ISSUE_STATUS = 'IssueStatus'
INIFILE_ISSUE_SENDTYPE = 'IssueSendType'
INIFILE_ISSUE_CATEGORY = 'IssueCategory'

#some default properties
HELPDESK_DEFAULT_TITLE = 'HelpDesk-Agent'
HELPDESK_DEFAULT_USER_FOLDER = 'acl_users'
HELPDESK_DEFAULT_MAIL_SERVER_NAME = 'localhost'
HELPDESK_DEFAULT_MAIL_SERVER_NAME = 25
HELPDESK_DEFAULT_MAIL_FROM_ADDRESS = 'IssueTracker@localhost'
HELPDESK_DEFAULT_ADD_ISSUE_EMAIL_SUBJECT = 'HelpDesk Agent: new issue posted'
HELPDESK_DEFAULT_UPDATE_ISSUE_EMAIL_SUBJECT = 'HelpDesk Agent: issue modification'
HELPDESK_DEFAULT_DELETE_ISSUE_EMAIL_SUBJECT = 'HelpDesk Agent: issue deleted'
HELPDESK_DEFAULT_ADD_ISSUE_COMMENT_EMAIL_SUBJECT = 'HelpDesk Agent: new comment to issue posted'
HELPDESK_DEFAULT_UPDATE_ISSUE_COMMENT_EMAIL_SUBJECT = 'HelpDesk Agent: comment modification'
HELPDESK_DEFAULT_DELETE_ISSUE_COMMENT_EMAIL_SUBJECT = 'HelpDesk Agent: comment(s) deleted'
HELPDESK_DEFAULT_FEEDBACK_EMAIL_SUBJECT = 'HelpDesk Agent: feedback'
HELPDESK_DEFAULT_ISSUE_TICKET_LENGTH = 15
ISSUE_DEFAULT_TITLE = 'Issue'
ISSUE_QUICK_DEFAULT_TITLE = 'Quick Issue'

#define HelpDesk roles names
HELPDESK_ROLE_ADMINISTRATOR = 'Issue administrator'
HELPDESK_ROLE_CONSULTANT = 'Issue resolver'
HELPDESK_ROLE_AUTHENTICATED = 'Authenticated'

#define HelpDesk Permission names
PERMISSION_MANAGE_HELPDESK_SETTINGS = 'HelpDesk Administration'
PERMISSION_POST_ISSUES = 'HelpDesk Post Issues'
PERMISSION_POST_COMMENTS = 'HelpDesk Post Comments to Issues'
PERMISSION_ATTACH_FILES = 'Attach files to issues'

#define security constants for issue
ISSUE_SECURITY_PUBLIC = 'public'
ISSUE_SECURITY_PRIVATE = 'private'

#anonymous user label
ANONYMOUS_USER_NAME = 'Anonymous'

#history labels
HISTORY_ISSUE_ADDED = 'Issue added'
HISTORY_ISSUE_MODIFIED = 'Issue modified'
HISTORY_COMMENT_ADDED = 'Comment added'
HISTORY_COMMENT_MODIFIED = 'Comment modified'
HISTORY_COMMENT_DELETED = 'Comment(s) deleted'

#manage options labels
HELPDESK_MANAGE_OPTION_VIEW = 'View'
HELPDESK_MANAGE_OPTION_ADMINISTRATION = 'Administration'
HELPDESK_MANAGE_OPTION_REPORTS = 'Reports'
ISSUE_MANAGE_OPTION_VIEW = 'View'
ISSUE_MANAGE_OPTION_PROPERTIES = 'More Properties'
ISSUE_MANAGE_OPTION_COMMENTS = 'Comments'
ISSUE_MANAGE_OPTION_HISTORY = 'History'

#meta types labels
HELPDESK_META_TYPE_LABEL = 'Naaya HelpDesk'
ISSUE_META_TYPE_LABEL = 'Naaya HelpDesk Issue'

#attachment label
ATTACHMENT_FOR_ISSUE_LABEL = 'Attachment for issue'
ATTACHMENT_FOR_COMMENT_LABEL = 'Attachment for comment '

#email constants
SENDEMAIL_HELPDESK_ADMINISTRATORS = 1
SENDEMAIL_HELPDESK_CONSULTANTS = 2
SENDEMAIL_HELPDESK_USERS = 4
SENDEMAIL_HELPDESK_ALL = 7

#email notifications
NOTIFY_ADD_ISSUE = 1
NOTIFY_MODIFY_ISSUE = 2
NOTIFY_ALL = 3

#actions
ACTION_ADD_ISSUE = 101
ACTION_UPDATE_ISSUE = 102
ACTION_DELETE_ISSUE = 103
ACTION_ADD_COMMENT = 201
ACTION_UPDATE_COMMENT = 202
ACTION_DELETE_COMMENT = 203

#errors
FORM_ERROR_SUBJECT_EMPTY = 'Subject field must be filled.'
FORM_ERROR_CATEGORY_EMPTY = 'Category field must be filled.'
FORM_ERROR_DESCRIPTION_EMPTY = 'Description field must be filled.'
