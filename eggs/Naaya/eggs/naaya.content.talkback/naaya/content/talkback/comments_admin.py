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
except ImportError:
    excel_export_available = False

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from OFS.SimpleItem import SimpleItem

from Paragraph import Paragraph
from constants import (PERMISSION_MANAGE_TALKBACKCONSULTATION,
                       PERMISSION_INVITE_TO_TALKBACKCONSULTATION)
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
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
                for comment in sorted(paragraph.get_comments(),
                                      key=lambda c: c.comment_date):
                    yield comment

    _admin_template = NaayaPageTemplateFile('zpt/comments_admin', globals(),
                                            'tbconsultation_comments_admin')

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
            'comment_macros': Paragraph.comments_html.macros,
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

        header_style = xlwt.easyxf('font: bold on; align: horiz left;')
        normal_style = xlwt.easyxf('align: horiz left, vert top;')

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sheet 1')
        row = 0
        for col in range(len(fields)):
            ws.row(row).set_cell_text(col, fields[col][0], header_style)

        for comment in comments:
            row += 1
            for col in range(len(fields)):
                ws.row(row).set_cell_text(col, fields[col][1](comment), normal_style)
        output = StringIO()
        wb.save(output)

        return output.getvalue()

    security.declarePrivate('generate_custom_excel_output')
    def generate_custom_excel_output(self, fields, comments):

        normal_style = xlwt.easyxf('align: wrap on, horiz left, vert top;')
        header_style = xlwt.easyxf('font: bold on; align: wrap on, horiz left;')

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sheet 1')
        row = 0
        for col in range(len(fields)):
            ws.row(row).set_cell_text(col, fields[col][0], header_style)

        ws.col(0).width = 3000
        ws.col(1).width = 20000
        ws.col(2).width = 7500
        ws.col(3).width = 5000
        for comment in comments:
            row += 1
            for col in range(len(fields)):
                ws.row(row).set_cell_text(col, fields[col][1](comment), normal_style)
            row += 1
            ws.row(row).set_cell_text(0, 'EEA Comments' , header_style)
        output = StringIO()
        wb.save(output)

        return output.getvalue()

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'all_comments')
    def all_comments(self):
        def replies(tree):
            yield tree['comment']
            for child_comment in tree['children']:
                for c in replies(child_comment):
                    yield c

        for section in self.list_sections():
            for paragraph in section.get_paragraphs():
                for top_comment in paragraph.get_comment_tree():
                    for c in replies(top_comment):
                        yield c


    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'export')
    def export(self, file_type="CSV", as_attachment=False, REQUEST=None):
        """ """

        html2text = self.getSite().html2text
        def plain(s, trim=None):
            return html2text(s, trim)

        fields = [
            ('Section', lambda c: c.get_section().title_or_id()),
            ('Paragraph', lambda c: c.get_paragraph().plaintext_summary()),
            ('Message Id', lambda c: c.getId()),
            ('In reply to', lambda c: c.reply_to or ''),
            ('Message', lambda c: plain(c.message)),
            ('Contributor', lambda c: c.get_contributor_name()),
            ('Date', lambda c: c.comment_date.strftime('%Y/%m/%d %H:%M')),
            ('Paragraph url', lambda c: c.get_paragraph().absolute_url()),
        ]

        comments = self.all_comments()

        if file_type == 'CSV':
            ret = self.generate_csv_output(fields, comments)
            content_type = 'text/csv; charset=utf-8'
            filename = 'comments.csv'

        elif file_type == 'Excel':
            assert excel_export_available
            ret = self.generate_excel_output(fields, comments)
            content_type = 'application/vnd.ms-excel'
            filename = 'comments.xls'

        elif file_type == 'CustomExcel':
            fields = [
                ('Section', lambda c: c.get_section().title_or_id()),
                ('Message', lambda c: plain(c.message)),
                ('Contributor', lambda c: c.get_contributor_name()),
                ('Date', lambda c: c.comment_date.strftime('%Y/%m/%d %H:%M')),
            ]
            assert excel_export_available
            ret = self.generate_custom_excel_output(fields, comments)
            content_type = 'application/vnd.ms-excel'
            filename = 'comments.xls'

        else: raise ValueError('unknown file format %r' % file_type)

        if as_attachment and REQUEST is not None:
            filesize = len(ret)
            set_response_attachment(REQUEST.RESPONSE, filename,
                content_type, filesize)
        return ret

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'comments_table_html')
    comments_table_html = NaayaPageTemplateFile('zpt/comments_table',
                                globals(), 'tbconsultation_comments_table')

InitializeClass(CommentsAdmin)
