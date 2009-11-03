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
# Alex Morega, Eau de Web

#Python imports
import os
import sys
from itertools import groupby

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Paragraph import Paragraph
from constants import PERMISSION_MANAGE_TALKBACKCONSULTATION

#local imports

class CommentsAdmin(SimpleItem):
    security = ClassSecurityInfo()

    title = "Comments administration"

    def __init__(self, id):
        super(SimpleItem, self).__init__(id)
        self.id = id

    def _iter_comments(self):
        for section in self.list_sections():
            for paragraph in section.get_paragraphs():
                for comment in paragraph.get_comments():
                    yield comment

    _comment_template = Paragraph.comments_html
    _admin_template = PageTemplateFile('zpt/comments_admin', globals())
    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'index_html')
    def index_html(self, REQUEST):
        """ the admin page for comments """

        unapproved = []
        total_count = 0
        invited_count = 0
        anonymous_count = 0

        for comment in self._iter_comments():
            if comment.approved is False:
                unapproved.append(comment)

            total_count += 1
            if comment.is_invited:
                invited_count += 1
            elif comment.is_anonymous:
                anonymous_count += 1

        group_key = lambda comment: comment.get_section()
        grouped_unapproved = [(k, list(g))
                              for k, g in groupby(unapproved, group_key)]

        options = {
            'total_count': total_count,
            'invited_count': invited_count,
            'anonymous_count': anonymous_count,
            'unapproved_count': len(unapproved),
            'unapproved_comments': grouped_unapproved,
            'comment_macros': self._comment_template.macros,
        }
        return self._admin_template(REQUEST, **options)

InitializeClass(CommentsAdmin)
