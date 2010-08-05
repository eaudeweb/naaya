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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web
# Alex Morega, Eau de Web

import re

import scrubber
if 'any' not in dir(__builtins__):
    from Products.NaayaCore.backport import any
    scrubber.any = any
sanitize = scrubber.Scrubber().scrub

def trim(message):
    """ Remove leading and trailing empty paragraphs """
    message = re.sub(r'^\s*<p>(\s*(&nbsp;)*)*\s*</p>\s*', '', message)
    message = re.sub(r'\s*<p>(\s*(&nbsp;)*)*\s*</p>\s*$', '', message)
    return message

def cleanup_message(message):
    return sanitize(trim(message)).strip()

#Zope imports
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime

#Product imports
from Products.NaayaBase.NyFSFile import NyFSFile
from constants import *


def addComment(self, contributor, message,
               file='', reply_to=None, approved=True):
    id = self.utGenRandomId(6)
    while id in self.objectIds():
        id = self.utGenRandomId(6)
    ob = TalkBackConsultationComment(id, contributor, message,
                                     file, reply_to, approved)
    self._setObject(id, ob)

    ob = self._getOb(id)
    ob.handleUpload(file)

    return id

class TalkBackConsultationComment(NyFSFile):
    """ """

    meta_type = METATYPE_TALKBACKCONSULTATION_COMMENT

    manage_options = ( { 'label' : 'View'
                       , 'action' : 'manage_workspace'
                       },
                     ) + (NyFSFile.manage_options[0], )

    security = ClassSecurityInfo()

    reply_to = None
    approved = True

    def __init__(self, id, contributor, message, file, reply_to, approved):
        self.contributor = contributor
        self.message = message
        self.reply_to = reply_to
        self.approved = approved
        self.comment_date = DateTime()
        NyFSFile.__init__(self, id, '', file)

    def get_contributor_name(self):
        auth_tool = self.getAuthenticationTool()
        contributor = self.contributor

        if self.contributor.startswith('invite:'):
            invite = self.invitations.get_invitation(contributor[7:])
            inviter_name = auth_tool.name_from_userid(invite.inviter_userid)
            return "%s (invited by %s)" % (invite.name, inviter_name)

        elif self.contributor.startswith('anonymous:'):
            return "%s (not authenticated)" % contributor[10:]

        else:
            name = auth_tool.name_from_userid(contributor)
            return "%s (%s)" % (name, contributor)

    title = property(lambda self: 'Comment by %s' % self.contributor,
                     lambda self, value: None)

    security.declareProtected(
        PERMISSION_REVIEW_TALKBACKCONSULTATION, 'handleUpload')
    def handleUpload(self, file=None):
        if not file: return
        self.filename = file.filename
        data, size = self._read_data(file)
        content_type = self._get_content_type(
            file, data, self.__name__, 'application/octet-stream')
        self.update_data(data, content_type, size, file.filename)

    security.declareProtected(view, 'get_talkback_file')
    def get_talkback_file(self, REQUEST, RESPONSE):
        """Download the attached file"""

        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Content-Disposition',
            "attachment;filename*=UTF-8''" + self.utToUtf8(self.filename))
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        return self.index_html()

    security.declareProtected(view, 'check_file')
    def check_file(self):
        return hasattr(self, 'filename')

    security.declareProtected(view, 'get_comment_date')
    def get_comment_date(self):
        """ """
        return self.comment_date

    @property
    def is_invited(self):
        return self.contributor.startswith('invite:')

    @property
    def is_anonymous(self):
        return self.contributor.startswith('anonymous:')

    @property
    def invite_key(self):
        if self.is_invited:
            return self.contributor[len('invite:'):]
        else:
            return None

    def visible_to_user(self, request):
        if self.approved:
            return True

        if self.check_admin_permissions():
            return True

        if self.invite_key is not None:
            invitations = self.get_consultation().invitations
            current_invite = invitations.get_current_invitation(request)
            if (current_invite is not None and
                current_invite.key == self.invite_key):
                return True

        return False

    def check_admin_permissions(self):
        """
        Allow people with PERMISSION_REVIEW_TALKBACKCONSULTATION.
        In the case of invited comments, also allow the inviter.
        """
        if self.checkPermissionManageTalkBackConsultation():
            return True # user has review permission

        if self.invite_key is not None:
            invite = self.get_consultation().invitations.get_invitation(self.invite_key)
            auth_tool = self.getAuthenticationTool()
            if invite.inviter_userid == auth_tool.get_current_userid():
                return True # contributor was invited by current user

        return False

    security.declarePublic('save_modifications')
    def save_modifications(self, message, REQUEST=None):
        """ Save body edits """
        if not self.check_admin_permissions():
            raise Unauthorized
        self.message = cleanup_message(message)
        if REQUEST is not None:
            self.setSessionInfo(['Saved changes (%s)' % DateTime()])
            back_url = REQUEST.form.get('back_url',
                                        self.get_section().absolute_url())
            REQUEST.RESPONSE.redirect(back_url)

    security.declarePublic('approve')
    def approve(self, REQUEST):
        """ approve this comment """
        if not self.check_admin_permissions():
            raise Unauthorized

        if REQUEST.REQUEST_METHOD != 'POST':
            raise ValueError('Please use POST')

        self.approved = True

        back_url = REQUEST.form.get('back_url', self.get_section().absolute_url())
        REQUEST.RESPONSE.redirect(back_url)

    security.declareProtected(view_management_screens, 'manage_workspace')
    manage_workspace = PageTemplateFile('zpt/comment_manage', globals())

    _edit_html = PageTemplateFile('zpt/comment_edit', globals())
    security.declarePublic('edit_html')
    def edit_html(self, REQUEST):
        """ edit this comment """
        if not self.check_admin_permissions():
            raise Unauthorized
        return self._edit_html(REQUEST)

InitializeClass(TalkBackConsultationComment)
