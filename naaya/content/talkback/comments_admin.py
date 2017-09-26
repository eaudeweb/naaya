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
# Mihai Tabara, Eau de Web

#Python imports
from cStringIO import StringIO
import csv
import codecs
from DateTime import DateTime

try:
    import json
except ImportError:
    import simplejson as json

import xlwt

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from OFS.SimpleItem import SimpleItem

from Paragraph import Paragraph
from permissions import (PERMISSION_MANAGE_TALKBACKCONSULTATION)
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.managers.import_export import set_response_attachment

class CommentsAdmin(SimpleItem):
    security = ClassSecurityInfo()

    title = "Comments administration"

    def __init__(self, id):
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

        if self.checkPermissionManageTalkBackConsultation():
            pass
        elif self.checkPermissionInviteToTalkBackConsultation():
            pass
        elif self.own_comments():
            pass
        else:
            raise Unauthorized

        total_count = 0
        invited_count = 0
        anonymous_count = 0

        for comment in self._iter_comments():
            total_count += 1
            if comment.is_invited:
                invited_count += 1
            elif comment.is_anonymous:
                anonymous_count += 1

        contributors = self._get_contributors_stats()
        invited = filter(lambda x: x['invited'], contributors)
        anonymous = filter(lambda x: x['anonymous'], contributors)

        options = {
            'contributors_count': len(contributors),
            'invited_contributors_count': len(invited),
            'anonymous_contributors_count': len(anonymous),
            'contributors_details': contributors,
            'total_count': total_count,
            'invited_count': invited_count,
            'anonymous_count': anonymous_count,
            'comment_macros': Paragraph.comments_html.macros,
            'get_comments_trend': self.get_comments_trend(),
        }
        return self._admin_template(REQUEST, **options)

    def _get_contributors_stats(self):

        contrib_stats = {}
        for comment in self._iter_comments():
            try:
                test = contrib_stats[comment.contributor]
            except KeyError:
                new_user_info = comment.get_contributor_info()
                new_user_info['count'] = 1
                contrib_stats[comment.contributor] = new_user_info
            else:
                contrib_stats[comment.contributor]['count'] += 1
        contrib_stats = [v for k, v in contrib_stats.items()]

        return contrib_stats

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'get_comments_trend')
    def get_comments_trend(self):
        """ get comments trend """
        days = {
            self.start_date.Date(): 0,
            self.end_date.Date(): 0
        }

        for comment in self._iter_comments():
            date = comment.comment_date.Date()
            count = days.setdefault(date, 0)
            days[date] = count + 1

        data = []
        for day, comments in days.items():
            data.append({'day': day, 'comments': comments})

        return json.dumps(sorted(data, key=lambda x: x['day']))

    security.declarePrivate('generate_csv_output')
    def generate_csv_output(self, fields, comments):

        output = StringIO()
        csv_writer = csv.writer(output)

        csv_writer.writerow(['Consultation deadline',
                             (self.end_date + 1).strftime('%Y/%m/%d %H:%M')])
        csv_writer.writerow(['Date of export', DateTime().strftime('%Y/%m/%d %H:%M')])

        csv_writer.writerow([field[0] for field in fields])

        for n, item in enumerate(comments):
            row = [field[1](item).encode('utf-8') for field in fields]
            csv_writer.writerow(row)


        return codecs.BOM_UTF8 + output.getvalue()

    security.declarePrivate('generate_excel_output')
    def generate_excel_output(self, fields, comments):

        header_style = xlwt.easyxf('font: bold on; align: horiz left;')
        normal_style = xlwt.easyxf('align: horiz left, vert top;')

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sheet 1')

        ws.row(0).set_cell_text(0, 'Consultation deadline', header_style)
        ws.row(0).set_cell_text(1, (self.end_date + 1).strftime('%Y/%m/%d %H:%M'),
                                normal_style)
        ws.row(1).set_cell_text(0, 'Date of export', header_style)
        ws.row(1).set_cell_text(1, DateTime().strftime('%Y/%m/%d %H:%M'),
                                normal_style)

        row = 2
        for col in range(len(fields)):
            ws.row(row).set_cell_text(col, fields[col][0], header_style)

        for item in comments:
            row += 1
            for col in range(len(fields)):
                ws.row(row).set_cell_text(col, fields[col][1](item),
                                          normal_style)
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
        for item in comments:
            row += 1
            for col in range(len(fields)):
                ws.row(row).set_cell_text(col, fields[col][1](item),
                                          normal_style)
            row += 1
            ws.row(row).set_cell_text(0, 'EEA Comments' , header_style)
        output = StringIO()
        wb.save(output)

        return output.getvalue()

    def _all_comments(self):

        def replies(this_comment):
            yield this_comment
            for child_comment in this_comment['children']:
                for c in replies(child_comment):
                    yield c

        for section in self.list_sections():
            for paragraph in section.get_paragraphs():
                for top_comment in paragraph.get_comment_tree():
                    for c in replies(top_comment):
                        yield c


    def all_comments(self):
        perm_manage = self.checkPermissionManageTalkBackConsultation()
        if perm_manage:
            return self._all_comments()
        own_comments = self.own_comments()
        if own_comments:
            return own_comments
        raise Unauthorized

    def export(self, file_type="CSV", as_attachment=False, REQUEST=None):
        """ """
        perm_manage = self.checkPermissionManageTalkBackConsultation()
        if not (perm_manage or self.own_comments):
            raise Unauthorized

        html2text = self.getSite().html2text
        def plain(s, trim=None):
            return html2text(s, trim)

        fields = [
            ('Section', lambda i: i['comment'].get_section().title_or_id()),
            ('Paragraph', lambda i: (i['comment'].get_paragraph()
                                     .plaintext_summary())),
            ('Message Id', lambda i: i['comment'].getId()),
            ('Replies', lambda i: str(len(i['children']))),
            ('In reply to', lambda i: i['comment'].reply_to or ''),
            ('Message', lambda i: plain(i['comment'].message)),
            ('Contributor', lambda i: i['comment'].get_contributor_name()),
            ('Date', lambda i: (i['comment'].comment_date
                                .strftime('%Y/%m/%d %H:%M'))),
            ('Paragraph url', lambda i: (i['comment'].get_paragraph()
                                         .absolute_url())),
        ]

        comments = self.all_comments()

        if file_type == 'CSV':
            ret = self.generate_csv_output(fields, comments)
            content_type = 'text/csv; charset=utf-8'
            filename = 'comments.csv'

        elif file_type == 'Excel':
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
            ret = self.generate_custom_excel_output(fields, comments)
            content_type = 'application/vnd.ms-excel'
            filename = 'comments.xls'

        else: raise ValueError('unknown file format %r' % file_type)

        if as_attachment and REQUEST is not None:
            filesize = len(ret)
            set_response_attachment(REQUEST.RESPONSE, filename,
                content_type, filesize)
        return ret

    _comments_table_html = NaayaPageTemplateFile('zpt/comments_table',
                                globals(), 'tbconsultation_comments_table')

    def comments_table_html(self):
        """ table showing all comments from all participants (manager)
        or all the user's comments, if the user is just a commenter """
        if self.checkPermissionManageTalkBackConsultation():
            pass
        elif self.own_comments():
            pass
        else:
            raise Unauthorized

        return self._comments_table_html()

InitializeClass(CommentsAdmin)
