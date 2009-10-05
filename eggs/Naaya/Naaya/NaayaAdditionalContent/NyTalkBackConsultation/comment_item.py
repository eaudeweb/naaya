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

try:
    import scrubber
except ImportError:
    sanitize = lambda x: x
else:
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
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime

#Product imports
from Products.NaayaBase.NyFSFile import NyFSFile
from constants import *


def addComment(self, contributor, message, file='', reply_to=None):
    id = self.utGenRandomId(6)
    while id in self.objectIds():
        id = self.utGenRandomId(6)
    ob = TalkBackConsultationComment(id, contributor, message, file, reply_to)
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

    def __init__(self, id, contributor, message, file, reply_to):
        self.contributor = contributor
        self.message = message
        self.reply_to = reply_to
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

    security.declareProtected(
        PERMISSION_MANAGE_TALKBACKCONSULTATION, 'save_modifications')
    def save_modifications(self, message, REQUEST=None):
        """ Save body edits """
        self.message = cleanup_message(message)
        if REQUEST is not None:
            self.setSessionInfo(['Saved changes (%s)' % DateTime()])
            self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/edit_html')

    security.declareProtected(view_management_screens, 'manage_workspace')
    manage_workspace = PageTemplateFile('zpt/comment_manage', globals())

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'edit_html')
    edit_html = PageTemplateFile('zpt/comment_edit', globals())

InitializeClass(TalkBackConsultationComment)
