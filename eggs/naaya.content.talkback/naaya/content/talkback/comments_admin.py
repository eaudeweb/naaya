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
from cStringIO import StringIO
import csv

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Paragraph import Paragraph
from constants import (PERMISSION_MANAGE_TALKBACKCONSULTATION,
                       PERMISSION_INVITE_TO_TALKBACKCONSULTATION)

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

    security.declarePublic('index_html')
    def index_html(self, REQUEST):
        """ the admin page for comments """

        if self.checkPermission(PERMISSION_MANAGE_TALKBACKCONSULTATION):
            pass
        elif self.checkPermission(PERMISSION_INVITE_TO_TALKBACKCONSULTATION):
            pass
        else:
            raise Unauthorized

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

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'export_csv')
    def export_csv(self, REQUEST, RESPONSE):
        """ export all comments as CSV """

        data_file = StringIO()
        csv_writer = csv.writer(data_file)

        html2text = self.getSite().html2text
        def plain(s, trim=None):
            return html2text(s, trim)

        fields = [
            ('Section', lambda c: c.get_section().title_or_id()),
            ('Paragraph', lambda c: c.get_paragraph().absolute_url()),
            ('Paragraph text', lambda c: plain(c.get_paragraph().body, 100)),
            ('Contributor', lambda c: c.get_contributor_name()),
            ('Date', lambda c: c.comment_date.strftime('%Y/%m/%d %H:%M')),
            ('Message', lambda c: c.message),
            ('Message (plain text)', lambda c: plain(c.message)),
        ]

        csv_writer.writerow([field[0] for field in fields])

        comments = [c for c in self._iter_comments() if c.approved]
        comments.sort(key=dict(fields)['Date'])

        for comment in comments:
            row = [field[1](comment).encode('utf-8') for field in fields]
            csv_writer.writerow(row)

        raw_data = data_file.getvalue()

        RESPONSE.setHeader('Content-Type', 'text/csv;charset=utf-8')
        RESPONSE.setHeader('Content-Length', len(raw_data))
        RESPONSE.setHeader('Content-Disposition',
                           "attachment; filename=comments.csv")
        return raw_data

InitializeClass(CommentsAdmin)
