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

#Zope imports
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime

#Product imports
from Products.NaayaBase.NyFSFile import NyFSFile
from constants import *


def addComment(self,
               title='',
               contributor='',
               contributor_name='',
               message='',
               file='',
               REQUEST=None):
    """ """

    errors = []
    if not contributor_name: errors.append('Please input your name.')
    if not message: errors.append('The comment field cannot be empty.')
    if errors:
        self.setSessionErrors(errors)
        if REQUEST is not None:
            self.setSession('username', contributor_name)
            self.setSession('message', message)
            self.REQUEST.RESPONSE.redirect(self.absolute_url())
        return
    self.delSession('username')
    self.delSession('message')

    if REQUEST and not contributor:
        contributor = REQUEST.AUTHENTICATED_USER.getUserName()

    id = str('tb%s-%s' % (contributor, self.utGenRandomId(6)))
    title = 'Comment by %s (%s)' % (contributor_name, contributor)

    ob = TalkBackConsultationComment(id,
                                     title,
                                     contributor,
                                     contributor_name,
                                     message,
                                     file)
    self._setObject(id, ob)

    ob = self._getOb(id)
    ob.handleUpload(file)

    if REQUEST is not None:
        anchor = self.get_anchor()
        section = self.get_section()
        ret_url = '%s/index_html#%s' % (section.absolute_url(), anchor)

        return REQUEST.RESPONSE.redirect(ret_url)

class TalkBackConsultationComment(NyFSFile):
    """ """

    meta_type = METATYPE_TALKBACKCONSULTATION_COMMENT

    manage_options = ( { 'label' : 'View'
                       , 'action' : 'manage_workspace'
                       },
                     ) + (NyFSFile.manage_options[0], )

    security = ClassSecurityInfo()

    def __init__(self, id, title, contributor, contributor_name, message, file):
        self.contributor = contributor
        self.contributor_name = contributor_name
        self.message = message
        self.comment_date = DateTime()
        NyFSFile.__init__(self, id, title, file)

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
                           'attachment;filename=' + self.utToUtf8(self.filename)
                           )
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
        self.message = message
        if REQUEST is not None:
            self.setSessionInfo(['Saved changes (%s)' % DateTime()])
            self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/edit_html')

    security.declareProtected(view_management_screens, 'manage_workspace')
    manage_workspace = PageTemplateFile('zpt/comment_manage', globals())

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'edit_html')
    edit_html = PageTemplateFile('zpt/comment_edit', globals())

InitializeClass(TalkBackConsultationComment)
