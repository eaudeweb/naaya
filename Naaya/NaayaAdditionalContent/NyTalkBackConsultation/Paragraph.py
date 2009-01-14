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
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from DateTime import DateTime

#Product imports
from comment_item import addComment, TalkBackConsultationComment
from constants import *


def addParagraph(self, id='', title='', body='', REQUEST=None):
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    ob = Paragraph(id, title, body)
    self._setObject(id, ob)


class Paragraph(Folder):

    meta_type = METATYPE_TALKBACKCONSULTATION_PARAGRAPH

    security = ClassSecurityInfo()

    def all_meta_types( self, interfaces=None ):
        """
        Called by Zope to determine what
        kind of object the envelope can contain
        """
        return [{'name': METATYPE_TALKBACKCONSULTATION_COMMENT,
              'action': 'addComment',
              'permission': PERMISSION_REVIEW_TALKBACKCONSULTATION}
             ]


    def __init__(self, id, title, body):
        self.id =  id
        self.title = title
        self.body = body

    security.declareProtected(view, 'get_paragraph')
    def get_paragraph(self):
        return self

    security.declareProtected(view, 'get_anchor')
    def get_anchor(self):
        return 'naaaya-talkback-paragraph-%s' % self.id

    security.declareProtected(view, 'get_comments')
    def get_comments(self):
        return self.objectValues([METATYPE_TALKBACKCONSULTATION_COMMENT])

    _delete_comment_confirmation = PageTemplateFile('zpt/paragraph_delete_comment', globals())
    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'delete_comment')
    def delete_comment(self, comment_id, REQUEST=None):
        """ """
        if not isinstance(self[comment_id], TalkBackConsultationComment):
            raise ValueError('Member object with id="%s" is not a TalkBackConsultationComment instance' % comment_id)
        
        if REQUEST and REQUEST.REQUEST_METHOD != 'POST':
            # the client should POST to delete the comment
            return self._delete_comment_confirmation(self, REQUEST, comment=self[comment_id])
        
        self.manage_delObjects([comment_id])
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_section().absolute_url())

    security.declareProtected(
        PERMISSION_MANAGE_TALKBACKCONSULTATION, 'merge_down')
    def merge_down(self, REQUEST):
        """ """

        # get a list of paragraphs
        paragraphs = [paragraph.id for paragraph in self.get_paragraphs()]
        paragraphs.sort()

        # get the paragraph following this one
        try:
            next_paragraph = paragraphs[paragraphs.index(self.id)+1]
            next_paragraph = self.get_section()._getOb(next_paragraph)
        except IndexError:
            self.setSessionErrors([
                'Bad paragraph index while merging paragraphs'])
            REQUEST.RESPONSE.redirect(self.get_section().absolute_url())
            return

        # merge the paragraphs - body and comments
        self.body += next_paragraph.body

        comment_ids = [comment.getId() for comment in \
                       next_paragraph.get_comments()]
        objs = next_paragraph.manage_copyObjects(comment_ids)
        self.manage_pasteObjects(objs)

        # remove the old paragraph
        self.get_section().manage_delObjects([next_paragraph.id])

        # refresh the section page
        REQUEST.RESPONSE.redirect( "%s/edit_html#%s" %
                                   (self.get_section().absolute_url(),
                                    self.get_anchor()) )

    security.declareProtected(
        PERMISSION_REVIEW_TALKBACKCONSULTATION, 'addComment')
    addComment = addComment

    security.declareProtected(
        PERMISSION_MANAGE_TALKBACKCONSULTATION, 'save_modifications')
    def save_modifications(self, body, REQUEST=None):
        """ Save body edits """
        self.body = body
        if REQUEST is not None:
            self.setSessionInfo(['Saved changes (%s)' % DateTime()])
            self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/edit_html')

    #forms
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/paragraph_index', globals())

    security.declareProtected(
        PERMISSION_MANAGE_TALKBACKCONSULTATION, 'edit_html')
    edit_html = PageTemplateFile('zpt/paragraph_edit', globals())

    security.declareProtected(view, 'comments_html')
    comments_html = PageTemplateFile('zpt/paragraph_comments', globals())

InitializeClass(Paragraph)
