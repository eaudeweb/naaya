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

# Zope imports
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view
from DateTime import DateTime

# Product imports
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaBase.NyImageContainer import NyImageContainer
from comment_item import addComment, TalkBackConsultationComment
from comment_item import cleanup_message
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from constants import *
from Products.NaayaCore.managers.utils import html2text
from permissions import (PERMISSION_REVIEW_TALKBACKCONSULTATION,
                         PERMISSION_MANAGE_TALKBACKCONSULTATION)


def addParagraph(self, id='', title='', body='', sort_index=None,
                 REQUEST=None):
    if id:
        id = self.utSlugify(id)
    else:
        id = self.make_paragraph_id()
    body = re.sub(r'href="\#_ftn([0-9]*)"', r'href="#_ftn\1" id="_ftnref\1"',
                  body)
    body = re.sub(r'href="\#_ftnref([0-9]*)"',
                  r'href="#_ftnref\1" id="_ftn\1"', body)
    ob = Paragraph(id, title, body)
    self._setObject(id, ob)
    ob = self._getOb(id)

    self._ensure_paragraph_ids()
    if sort_index is not None:
        self.paragraph_ids.insert(sort_index, id)
    else:
        self.paragraph_ids.append(id)
    self._p_changed = 1


class Paragraph(Folder):

    meta_type = METATYPE_TALKBACKCONSULTATION_PARAGRAPH

    security = ClassSecurityInfo()

    meta_types = [
        {'name': METATYPE_TALKBACKCONSULTATION_COMMENT, 'action': 'addComment',
            'permission': PERMISSION_REVIEW_TALKBACKCONSULTATION},
    ]

    def __init__(self, id, title, body):
        self.id = id
        self.title = title
        self.body = body
        self.imageContainer = NyImageContainer(self, True)

    security.declareProtected(view, 'get_paragraph')

    def get_paragraph(self):
        return self

    security.declareProtected(view, 'get_anchor')

    def get_anchor(self):
        return 'tbp-%s' % self.id

    security.declareProtected(view, 'plaintext_summary')

    def plaintext_summary(self, chars=1024):
        return html2text(self.body, chars, ellipsis=True)

    security.declareProtected(view, 'get_comments')

    def get_comments(self):
        return self.objectValues([METATYPE_TALKBACKCONSULTATION_COMMENT])

    security.declareProtected(view, 'get_comment')

    def get_comment(self, comment_id):
        return self._getOb(comment_id)

    security.declareProtected(view, 'get_comment_tree')

    def get_comment_tree(self):
        comment_tree = {}
        for comment in self.objectValues(
                [METATYPE_TALKBACKCONSULTATION_COMMENT]):
            parent = comment_tree.setdefault(comment.reply_to, [])
            children = comment_tree.setdefault(comment.getId(), [])
            comment_dict = {'comment': comment, 'children': children}
            parent.append(comment_dict)

        # comment_tree[None] is the list of top-level comments
        return comment_tree.get(None, [])

    security.declareProtected(view, 'comment_count')

    def comment_count(self):
        return sum(1 for c in self.get_comments())

    _delete_comment_confirmation = NaayaPageTemplateFile(
        'zpt/paragraph_delete_comment', globals(),
        'tbconsultation_paragraph_delete_comment')
    security.declareProtected(view, 'delete_comment')

    def delete_comment(self, comment_id, REQUEST=None):
        """ """
        comment = self._getOb(comment_id)
        if not comment.check_del_permissions():
            raise Unauthorized

        if not isinstance(comment, TalkBackConsultationComment):
            raise ValueError('Member object with id="%s" is not a '
                             'TalkBackConsultationComment instance'
                             % comment_id)

        if REQUEST and REQUEST.REQUEST_METHOD != 'POST':
            # the client should POST to delete the comment
            return self._delete_comment_confirmation(self, REQUEST,
                                                     comment=comment)

        self.manage_delObjects([comment_id])
        if REQUEST:
            back_url = REQUEST.form.get('back_url',
                                        self.get_section().absolute_url())
            REQUEST.RESPONSE.redirect(back_url)

    _split_content_html = NaayaPageTemplateFile(
        'zpt/paragraph_split', globals(), 'tbconsultation_paragraph_split')

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'split_body')

    def split_body(self, body_0=None, body_1=None, REQUEST=None):
        """ """
        if REQUEST is not None and REQUEST.REQUEST_METHOD != 'POST':
            return self._split_content_html(self, REQUEST)

        if body_0 is None or body_1 is None:
            raise ValueError(
                'Missing body_0 or body_1 while trying to split paragraph "%s"'
                % self.id)

        section = self.get_section()
        section._ensure_paragraph_ids()
        my_index = section.paragraph_ids.index(self.id)
        addParagraph(section, body=body_1, sort_index=my_index+1)
        self.body = body_0

        if REQUEST is not None:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect(section.absolute_url() + '/edit_html')
            REQUEST.RESPONSE.redirect(
                "%s/edit_html#%s" %
                (section.absolute_url(), self.get_anchor()))

    security.declareProtected(
        PERMISSION_MANAGE_TALKBACKCONSULTATION, 'merge_down')

    def merge_down(self, REQUEST):
        """ """

        # get a list of paragraphs
        section = self.get_section()
        section._ensure_paragraph_ids()
        paragraphs = section.paragraph_ids

        # get the paragraph following this one
        try:
            next_paragraph = paragraphs[paragraphs.index(self.id)+1]
            next_paragraph = self.get_section()._getOb(next_paragraph)
        except IndexError:
            self.setSessionErrorsTrans(
                'Bad paragraph index while merging paragraphs')
            REQUEST.RESPONSE.redirect(self.get_section().absolute_url())
            return

        # merge the paragraphs - body and comments
        self.body += next_paragraph.body

        comment_ids = [comment.getId() for comment in
                       next_paragraph.get_comments()]
        objs = next_paragraph.manage_copyObjects(comment_ids)
        self.manage_pasteObjects(objs)

        # remove the old paragraph
        self.get_section().remove_paragraph(next_paragraph.id)

        # refresh the section page
        self.setSessionInfoTrans("Merged paragraphs")
        REQUEST.RESPONSE.redirect("%s/edit_html#%s" %
                                  (self.get_section().absolute_url(),
                                   self.get_anchor()))

    security.declareProtected(
        PERMISSION_MANAGE_TALKBACKCONSULTATION, 'move_down')

    def move_down(self, REQUEST):
        """ """

        # get a list of paragraphs
        section = self.get_section()
        section._ensure_paragraph_ids()
        paragraphs = section.paragraph_ids
        index = paragraphs.index(self.id)
        if index + 1 >= len(paragraphs):
            self.setSessionErrorsTrans(
                'Bad paragraph index while merging paragraphs')
            REQUEST.RESPONSE.redirect(self.get_section().absolute_url())
            return

        # swap the paragraphs
        paragraphs[index], paragraphs[index+1] = (paragraphs[index+1],
                                                  paragraphs[index])
        section._p_changed = 1

        # refresh the section page
        self.setSessionInfoTrans("Swapped paragraphs")
        REQUEST.RESPONSE.redirect("%s/edit_html#%s" %
                                  (self.get_section().absolute_url(),
                                   self.get_anchor()))

    security.declarePublic('addComment')

    def addComment(self, REQUEST):
        """wrapper method, checks security and calls the real addComment """
        if self.check_cannot_comment():
            raise Unauthorized

        invitation = self.invitations.get_current_invitation(REQUEST)
        userid = self.getAuthenticationTool().get_current_userid()
        message = REQUEST.form.get('message', '')
        clean_message = cleanup_message(message)
        next_page = REQUEST.get('next_page', self.absolute_url())
        reply_to = REQUEST.form.get('reply_to', None)

        contributor_name = REQUEST.form.get('contributor_name', '')
        errors = []
        if invitation is not None:
            contributor = 'invite:' + invitation.key
        elif userid is None:
            if contributor_name:
                contributor = 'anonymous:' + contributor_name
            else:
                errors.append('Please input your name.')
        else:
            contributor = userid

        if not clean_message:
            errors.append('The comment field cannot be empty.')
        if reply_to is not None and reply_to not in self.objectIds():
            errors.append("Can't reply to non-existent comment")

        if errors:
            self.setSessionErrorsTrans(errors)
            self.setSession('contributor_name', contributor_name)
            self.setSession('message', message)
            return REQUEST.RESPONSE.redirect(next_page)
        else:
            self.delSession('username')
            self.delSession('message')

        form_data = {
            'contributor': contributor,
            'message': clean_message,
            'file': REQUEST.form.get('file', ''),
            'reply_to': reply_to,
        }
        addComment(self, **form_data)

        success_message = "Comment submitted successfully."
        self.setSessionInfoTrans(success_message)
        REQUEST.RESPONSE.redirect(next_page)

    security.declareProtected(view, 'comment_form')
    comment_form = NaayaPageTemplateFile('zpt/comment_form', globals(),
                                         'tbconsultation_comment_form')

    security.declarePublic('get_message')

    def get_message(self, reply_to=None):
        session_message = self.getSession('message', None)
        if session_message is not None:
            return session_message

        if reply_to is not None:
            orig_message = self._getOb(reply_to).message
            reply_message = ('<p></p><blockquote>%s</blockquote><p></p>'
                             % orig_message)
            return reply_message

        return ''

    security.declareProtected(
        PERMISSION_MANAGE_TALKBACKCONSULTATION, 'save_modifications')

    def save_modifications(self, body, REQUEST=None):
        """ Save body edits """
        self.body = body
        if REQUEST is not None:
            self.setSessionInfoTrans('Saved changes (${date})',
                                     date=DateTime())
            self.REQUEST.RESPONSE.redirect(self.absolute_url() + '/edit_html')

    # forms
    security.declareProtected(view, 'index_html')
    index_html = NaayaPageTemplateFile('zpt/paragraph_index', globals(),
                                       'tbconsultation_paragraph_index')

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'edit_html')
    edit_html = NaayaPageTemplateFile('zpt/paragraph_edit', globals(),
                                      'tbconsultation_paragraph_edit')

    security.declareProtected(view, 'comments_html')
    comments_html = NaayaPageTemplateFile('zpt/paragraph_comments', globals(),
                                          'tbconsultation_paragraph_comments')

    security.declareProtected(view, 'embedded_html')
    embedded_html = NaayaPageTemplateFile(
        'zpt/paragraph_embedded', globals(),
        'tbconsultation_paragraph_edit_embedded')

InitializeClass(Paragraph)
