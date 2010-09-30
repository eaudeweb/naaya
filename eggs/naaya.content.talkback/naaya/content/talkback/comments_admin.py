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
try:
    import xlwt
    excel_export_available = True
except:
    excel_export_available = False

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Paragraph import Paragraph
from constants import (PERMISSION_MANAGE_TALKBACKCONSULTATION,
                       PERMISSION_INVITE_TO_TALKBACKCONSULTATION)
from Products.NaayaCore.managers.import_export import set_response_attachment

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

    security.declarePrivate('generate_csv_output')
    def generate_csv_output(self, fields, comments):

        output = StringIO()
        csv_writer = csv.writer(output)

        csv_writer.writerow([field[0] for field in fields])

        for n, comment in enumerate(comments):
            row = [field[1](comment).encode('utf-8') for field in fields]
            csv_writer.writerow(row)
        return output.getvalue()

    security.declarePrivate('generate_excel_output')
    def generate_excel_output(self, fields, comments):

        style = xlwt.XFStyle()
        normalfont = xlwt.Font()
        header = xlwt.Font()
        header.bold = True
        style.font = header

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sheet 1')
        row = 0
        for col in range(0, len(fields)):
            ws.row(row).set_cell_text(col, fields[col][0], style)
        style.font = normalfont

        for comment in comments:
            row += 1
            for col in range(0, len(fields)):
                ws.row(row).set_cell_text(col, fields[col][1](comment), style)
        output = StringIO()
        wb.save(output)

        return output.getvalue()

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'export')
    def export(self, file_type="CSV", as_attachment=False, REQUEST=None):
        """ """

        html2text = self.getSite().html2text
        def plain(s, trim=None):
            return html2text(s, trim)

        fields = [
            ('Section', lambda c: c.get_section().title_or_id()),
            ('Paragraph', lambda c: plain(c.get_paragraph().body, 100)),
            ('Message Id', lambda c: c.getId()),
            ('In reply to', lambda c: c.reply_to or ''),
            ('Message', lambda c: plain(c.message)),
            ('Contributor', lambda c: c.get_contributor_name()),
            ('Date', lambda c: c.comment_date.strftime('%Y/%m/%d %H:%M')),
            ('Paragraph url', lambda c: c.get_paragraph().absolute_url()),
        ]

        comments = [c for c in self._iter_comments() if c.approved]
        comments.sort(key=lambda c: (c.get_paragraph().id, c.comment_date))

        if file_type == 'CSV':
            ret = self.generate_csv_output(fields, comments)
            content_type = 'text/csv; charset=utf-8'
            filename = 'comments.csv'

        elif file_type == 'Excel':
            assert excel_export_available
            ret = self.generate_excel_output(fields, comments)
            content_type = 'application/vnd.ms-excel'
            filename = 'comments.xls'

        else: raise ValueError('unknown file format %r' % file_type)

        if as_attachment and REQUEST is not None:
            filesize = len(ret)
            set_response_attachment(REQUEST.RESPONSE, filename,
                content_type, filesize)
        return ret

InitializeClass(CommentsAdmin)
