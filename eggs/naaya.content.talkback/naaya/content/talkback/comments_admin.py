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

from io import StringIO
import csv
import codecs
from DateTime import DateTime

import json

from AccessControl.class_init import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from OFS.SimpleItem import SimpleItem

from .Paragraph import Paragraph
from naaya.core.zope2util import XLSX_CONTENT_TYPE, new_xlsx_workbook
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
        elif self.checkPermissionManageComments():
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
        invited = [x for x in contributors if x['invited']]
        anonymous = [x for x in contributors if x['anonymous']]

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
            contributor_name = comment.contributor.name
            if not contributor_name:
                contributor_name = comment.get_contributor_info()['name']
            try:
                contrib_stats[contributor_name]
            except KeyError:
                new_user_info = comment.get_contributor_info()
                new_user_info['count'] = 1
                contrib_stats[contributor_name] = new_user_info
            else:
                contrib_stats[contributor_name]['count'] += 1
        contrib_stats = [v for k, v in contrib_stats.items()]

        return contrib_stats

    security.declarePublic('get_comments_trend')

    def get_comments_trend(self):
        """ get comments trend """
        if self.checkPermissionManageTalkBackConsultation():
            pass
        elif self.checkPermissionManageComments():
            pass
        elif self.own_comments():
            return {}
        else:
            raise Unauthorized

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
        csv_writer.writerow(['Date of export',
                             DateTime().strftime('%Y/%m/%d %H:%M')])

        csv_writer.writerow([field[0] for field in fields])

        for n, item in enumerate(comments):
            row = [field[1](item) for field in fields]
            csv_writer.writerow(row)

        return codecs.BOM_UTF8 + output.getvalue().encode('utf-8')

    security.declarePrivate('generate_excel_output')

    def generate_excel_output(self, fields, comments):

        output, wb = new_xlsx_workbook()
        header_style = wb.add_format({'bold': True, 'align': 'left'})
        normal_style = wb.add_format({'align': 'left', 'valign': 'top'})
        link_style = wb.add_format({'font_color': 'blue', 'underline': 1})
        ws = wb.add_worksheet('Sheet 1')

        ws.write_string(0, 0, 'Consultation deadline', header_style)
        ws.write_string(0, 1, (self.end_date + 1).strftime('%Y/%m/%d %H:%M'),
                        normal_style)
        ws.write_string(1, 0, 'Date of export', header_style)
        ws.write_string(1, 1, DateTime().strftime('%Y/%m/%d %H:%M'),
                        normal_style)

        row = 2
        for col in range(len(fields)):
            ws.write_string(row, col, fields[col][0], header_style)

        for item in comments:
            row += 1
            for col in range(len(fields)):
                text = fields[col][1](item)
                # if the user is invited, we don't have a user profile
                # so no hyperlink
                if (fields[col][0] == 'Contributor' and
                        'invited by' not in text and
                        '(' in text):
                    # display_name is "userid (full name)"
                    link = ('https://www.eionet.europa.eu/users/' +
                            text[:text.find(' (')])
                    ws.write_url(row, col, link, link_style, string=text)
                else:
                    ws.write_string(row, col, text, normal_style)
        wb.close()

        return output.getvalue()

    security.declarePrivate('generate_custom_excel_output')

    def generate_custom_excel_output(self, fields, comments):

        output, wb = new_xlsx_workbook()
        normal_style = wb.add_format({'text_wrap': True, 'align': 'left',
                                      'valign': 'top'})
        header_style = wb.add_format({'bold': True, 'text_wrap': True,
                                      'align': 'left'})
        ws = wb.add_worksheet('Sheet 1')
        row = 0
        for col in range(len(fields)):
            ws.write_string(row, col, fields[col][0], header_style)

        # xlwt widths (1/256 of a character) converted to characters
        ws.set_column(0, 0, 3000 / 256)
        ws.set_column(1, 1, 20000 / 256)
        ws.set_column(2, 2, 7500 / 256)
        ws.set_column(3, 3, 5000 / 256)
        for item in comments:
            row += 1
            for col in range(len(fields)):
                ws.write_string(row, col, fields[col][1](item), normal_style)
            row += 1
            ws.write_string(row, 0, 'EEA Comments', header_style)
        wb.close()

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
        perm_manage_comments = self.checkPermissionManageComments()
        if perm_manage or perm_manage_comments:
            return self._all_comments()
        own_comments = self.own_comments()
        if own_comments:
            return own_comments
        raise Unauthorized

    def export(self, file_type="CSV", as_attachment=False, REQUEST=None):
        """ Export """
        perm_manage = self.checkPermissionManageTalkBackConsultation()
        perm_manage_comments = self.checkPermissionManageComments()
        if not (perm_manage or perm_manage_comments or self.own_comments()):
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
            ('Contributor',
             lambda i: i['comment'].get_contributor_info()['display_name']),
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
            content_type = XLSX_CONTENT_TYPE
            filename = 'comments.xlsx'

        elif file_type == 'CustomExcel':
            fields = [
                ('Section',
                 lambda i: i['comment'].get_section().title_or_id()),
                ('Message', lambda i: plain(i['comment'].message)),
                ('Contributor',
                 lambda i: (i['comment'].get_contributor_info()
                            ['display_name'])),
                ('Date', lambda i: (i['comment'].comment_date
                                    .strftime('%Y/%m/%d %H:%M'))),
            ]
            ret = self.generate_custom_excel_output(fields, comments)
            content_type = XLSX_CONTENT_TYPE
            filename = 'comments.xlsx'

        else:
            raise ValueError('unknown file format %r' % file_type)

        if as_attachment and REQUEST is not None:
            filesize = len(ret)
            set_response_attachment(REQUEST.RESPONSE, filename,
                                    content_type, filesize)
        return ret

    _comments_table_html = NaayaPageTemplateFile(
        'zpt/comments_table', globals(), 'tbconsultation_comments_table')

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
