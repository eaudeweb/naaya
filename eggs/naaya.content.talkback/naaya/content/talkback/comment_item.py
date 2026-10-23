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
# Mihai Tabara, Eau de Web


import re
from collections import namedtuple
from urllib.parse import quote

import bleach
from bleach.css_sanitizer import CSSSanitizer
from bs4 import BeautifulSoup

# Tags and attributes kept in comments; everything else is stripped
ALLOWED_TAGS = {'a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code', 'dd',
                'del', 'div', 'dl', 'dt', 'em', 'h1', 'h2', 'h3', 'h4', 'h5',
                'h6', 'hr', 'i', 'img', 'ins', 'li', 'ol', 'p', 'pre', 'q', 's',
                'small', 'span', 'strike', 'strong', 'sub', 'sup', 'table',
                'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'u', 'ul'}
ALLOWED_ATTRIBUTES = {'a': ['href', 'title'],
                      'img': ['src', 'alt', 'title', 'width', 'height'],
                      'td': ['colspan', 'rowspan', 'align', 'style'],
                      'th': ['colspan', 'rowspan', 'align', 'style']}
for _tag in ('p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
    ALLOWED_ATTRIBUTES[_tag] = ['align', 'style']
for _tag in ('span', 'li'):
    ALLOWED_ATTRIBUTES[_tag] = ['style']
# Only the colour and alignment set by the editor buttons
CSS_SANITIZER = CSSSanitizer(
    allowed_css_properties=['color', 'background-color', 'text-align'])


# Tags removed together with their content
DROP_CONTENT_TAGS = ('script', 'style')


def _drop_content_tags(message):
    if not re.search(r'<\s*(script|style)\b', message, re.I):
        return message
    soup = BeautifulSoup(message, 'html.parser')
    for tag in soup.find_all(DROP_CONTENT_TAGS):
        tag.decompose()
    return str(soup)


def _mark_external(attrs, new=False):
    attrs[(None, 'rel')] = 'nofollow'
    attrs[(None, 'class')] = 'external'
    return attrs


def sanitize(message):
    cleaned = bleach.clean(_drop_content_tags(message), tags=ALLOWED_TAGS,
                           attributes=ALLOWED_ATTRIBUTES,
                           css_sanitizer=CSS_SANITIZER, strip=True)
    return bleach.linkify(cleaned, callbacks=[_mark_external],
                          parse_email=False)


def trim(message):
    """ Remove leading and trailing empty paragraphs """
    message = re.sub(r'^\s*<p>(\s*(&nbsp;)*)*\s*</p>\s*', '', message)
    message = re.sub(r'\s*<p>(\s*(&nbsp;)*)*\s*</p>\s*$', '', message)
    return message


def cleanup_message(message):
    return sanitize(trim(message)).strip()

# Zope imports
from AccessControl.class_init import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime

# Product imports
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaBase.NyFSFile import NyFSFile
from .constants import *
from .permissions import PERMISSION_REVIEW_TALKBACKCONSULTATION


def addComment(self, contributor, message,
               file='', reply_to=None):
    id = self.utGenRandomId(6)
    while id in self.objectIds():
        id = self.utGenRandomId(6)
    ob = TalkBackConsultationComment(id, contributor, message,
                                     file, reply_to)
    self._setObject(id, ob)
    ob = self._getOb(id)
    # ob._save_contributor_name()
    ob.handleUpload(file)

    return id


# This creates a new Contributor class, which is a namedtuple.
# It's purpose is to maintain the immutability of the current
# string storage, while also making it easier to add new properties.
#
# The difference between it and a simple tuple is that the fields can
# be accessed by name, e.g:
# >>> contributor = Contributor('the name', 'user@localhost', '')
# >>> contributor.email
# ... 'user@localhost'
#
# WARNING: It is a TUPLE, immutable, field values cannot be changed after
# instantiation. If edits are needed, a new instance needs to be created!
Contributor = namedtuple(
    'Contributor', (
        'name',
        'email',
        'organisation',
        'source',
        'invite',
    )
)


class TalkBackConsultationComment(NyFSFile):
    """ Talk back consultation comment """

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

    def get_contributor_info(self):
        """
        Returns a dict filled with information about the user posting this
        comment. Keys to be returned in the dict are: <email<, <invited>,
        <anonymous>, <name> and <display_name>. Main difference between
        the last two keys is that display_name seizes more information
        about current user (being invited, anonymous, inviter name, etc)

        """
        info = {
            'display_name': '',
            'name': '',
            'email': '',
            'organisation': '',
            'invited': False,
            'anonymous': False,
        }

        auth_tool = self.getAuthenticationTool()
        contributor = self.contributor
        invite_key = contributor.invite

        if invite_key:
            invite = self.invitations.get_invitation(invite_key)
            invite_name = invite.name
            inviter_name = auth_tool.name_from_userid(invite.inviter_userid)

            info['display_name'] = u'{} (invited by {})'.format(
                invite_name, inviter_name)
            info['name'] = invite_name
            info['email'] = invite.email
            info['invited'] = True
        else:
            if contributor.source == 'anonymous':
                contributor_name = contributor.name
                contributor_organisation = contributor.organisation
                if contributor_organisation:
                    info['display_name'] = (
                        '{} - {} (not authenticated)'.format(
                            contributor_name, contributor_organisation))
                else:
                    info['display_name'] = '{} (not authenticated)'.format(
                        contributor_name)
                info['name'] = contributor_name
                info['email'] = contributor.email
                info['organisation'] = contributor_organisation
                info['anonymous'] = True
            else:
                user_id = contributor.name
                user = auth_tool.get_user_with_userid(user_id)

                # handle root zope users
                if user:
                    user_name = auth_tool.getUserFullName(user)
                    info['name'] = user_name
                    info['email'] = auth_tool.getUserEmail(user)
                    info['display_name'] = u'{} ({})'.format(
                        user_id,
                        user_name,
                    )
                else:
                    info['name'] = user_id
                    info['display_name'] = user_id

        return info

    title = property(lambda self: 'Comment by %s' % self.contributor.name,
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
            "attachment;filename*=UTF-8''" + quote(self.filename))
        RESPONSE.setHeader('Pragma', 'public')
        RESPONSE.setHeader('Cache-Control', 'max-age=0')
        return self.index_html()

    security.declareProtected(view, 'check_file')
    def check_file(self):
        return hasattr(self, 'filename')

    security.declareProtected(view, 'get_comment_date')
    def get_comment_date(self):
        """ Get comment date """
        return self.comment_date

    @property
    def is_invited(self):
        return self.contributor.source == 'invite'

    @property
    def is_anonymous(self):
        return self.contributor.source == 'anonymous'

    @property
    def invite_key(self):
        if self.is_invited:
            return self.contributor.invite
        else:
            return None

    def has_replies(self):
        for comment in self.aq_parent.get_comments():
            if comment.reply_to == self.getId():
                return True
        return False

    def check_manage_permissions(self):
        """
        * allow people with PERMISSION_MANAGE_TALKBACKCONSULTATION
        * allow owner of comment (contributor)
        * allow inviter of the owner

        """
        if self.checkPermissionManageTalkBackConsultation():
            return True

        auth_tool = self.getAuthenticationTool()
        owner_tuple = self.getOwnerTuple()
        if owner_tuple is not None:
            user_path, owner_id = owner_tuple
            if owner_id == auth_tool.get_current_userid():
                return True # current user is comment owner

        if self.invite_key is not None:
            invite = self.get_consultation().invitations.get_invitation(self.invite_key)
            if invite.inviter_userid == auth_tool.get_current_userid():
                return True # contributor was invited by current user

        return False

    def check_del_permissions(self):
        """
        Same as manage_permissions, except
        user can not delete comment if there are replies to it.

        """
        if not self.check_manage_permissions():
            return False
        if self.has_replies():
            return False
        return True

    def check_edit_permissions(self):
        """
        Same permission as `manage`. Also, same permission as `delete`,
        except for the no-replies condition missing here.
        Used to be different, kept if needed to be customized at some point.

        """
        return self.check_manage_permissions()

    security.declarePublic('save_modifications')
    def save_modifications(self, message, REQUEST=None):
        """ Save body edits """
        if not self.check_edit_permissions():
            raise Unauthorized
        self.message = cleanup_message(message)
        if REQUEST is not None:
            self.setSessionInfoTrans('Saved changes (${date})',
                                     date=DateTime())
            back_url = REQUEST.form.get('back_url',
                                        self.get_section().absolute_url())
            REQUEST.RESPONSE.redirect(back_url)

    security.declareProtected(view_management_screens, 'manage_workspace')
    manage_workspace = PageTemplateFile('zpt/comment_manage', globals())

    _edit_html = NaayaPageTemplateFile('zpt/comment_edit', globals(),
                                       'tbconsultation_comment_edit')
    security.declarePublic('edit_html')
    def edit_html(self, REQUEST):
        """ edit this comment """
        if not self.check_edit_permissions():
            raise Unauthorized
        return self._edit_html(REQUEST)

InitializeClass(TalkBackConsultationComment)
