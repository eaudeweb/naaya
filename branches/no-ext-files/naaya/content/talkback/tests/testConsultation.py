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

import re
from unittest import TestSuite, makeSuite
from datetime import date, timedelta
from DateTime import DateTime
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup
from copy import deepcopy

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.talkback.tbconsultation_item import addNyTalkBackConsultation, NyTalkBackConsultation
from naaya.content.talkback.comment_item import addComment
from Products.NaayaBase.NyRoleManager import NyRoleManager


class ConsultationBasicTestCase(NaayaFunctionalTestCase):
    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya TalkBack Consultation')
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        start_date = (date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
        end_date = (date.today() + timedelta(days=10)).strftime('%d/%m/%Y')
        addNyTalkBackConsultation(self.portal.myfolder, title="Test consultation",
            start_date=start_date, end_date=end_date,
            contributor='contributor', submitted=1)
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.portal.manage_uninstall_pluggableitem('Naaya TalkBack Consultation')
        transaction.commit()

    def test_create_consultation(self):
        self.portal.myfolder.manage_delObjects(['test-consultation'])
        transaction.commit()

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/talkbackconsultation_add_html')
        form = self.browser.get_form('frmAdd')
        form['title:utf8:ustring'] = "New consultation"
        self.browser.clicked(form, form.find_control('title:utf8:ustring'))
        self.browser.submit()

        self.assertEqual(self.portal.myfolder.objectIds(), ['new-consultation'])

        self.browser_do_logout()

    def test_create_section(self):
        self.browser_do_login('admin', '')

        self.assertEqual(len(self.portal.myfolder['test-consultation'].objectIds()), 0)

        self.browser.go('http://localhost/portal/myfolder/test-consultation/section_add_html')
        form = self.browser.get_form('frmAdd')
        form['title:utf8:ustring'] = "Section one"
        form['body:utf8:ustring'] = "<p>First paragraph</p><p>Second paragraph</p>"
        self.browser.clicked(form, form.find_control('title:utf8:ustring'))
        self.browser.submit()

        self.assertEqual(len(self.portal.myfolder['test-consultation'].objectIds()), 1)

        section = self.portal.myfolder['test-consultation'].objectValues()[0]
        self.assertEqual(section.title, "Section one")
        self.assertEqual(section.objectIds(), ['000', '001'])
        self.assertEqual(section['000'].body, '<p>First paragraph</p>')
        self.assertEqual(section['001'].body, '<p>Second paragraph</p>')

        self.browser_do_logout()

    def test_create_comment(self):
        self.portal.myfolder['test-consultation'].addSection(
            id='sec1', title='sec1', body='blah')
        transaction.commit()

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/test-consultation/sec1/000')
        self.assertTrue('Add a comment' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        form['message:utf8:ustring'] = 'I has something to say'
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()

        paragraph = self.portal.myfolder['test-consultation']['sec1']['000']
        self.assertEqual(len(paragraph.objectIds()), 1)
        comment = paragraph.objectValues()[0]
        self.assertEqual(comment.contributor, 'admin')
        self.assertEqual(comment.message, 'I has something to say')

        self.browser_do_logout()

    def test_create_admin_comment_after_expiration(self):
        consultation = self.portal.myfolder['test-consultation']
        consultation.addSection(
            id='sec2', title='sec2', body='blah2')
        transaction.commit()

        #Change the consultation end date to yesterday,
        #and check if administrators can still post comments
        end_date = consultation.end_date
        new_date = DateTime((date.today() - timedelta(days=1)).strftime('%d/%m/%Y'))
        self.portal.myfolder['test-consultation'].end_date = new_date
        transaction.commit()

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/test-consultation/sec2/000')
        self.assertTrue('Add a comment' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        form['message:utf8:ustring'] = 'I has something to say 2'
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()

        paragraph = consultation['sec2']['000']
        self.assertEqual(len(paragraph.objectIds()), 1)
        comment = paragraph.objectValues()[0]
        self.assertEqual(comment.contributor, 'admin')
        self.assertEqual(comment.message, 'I has something to say 2')

        self.browser_do_logout()

    def test_view_in_folder(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)

        tables = soup.findAll('table', id='folderfile_list')
        self.assertTrue(len(tables) == 1)

        links_to_consultation = tables[0].findAll('a', attrs={'href': 'http://localhost/portal/myfolder/test-consultation'})
        self.assertTrue(len(links_to_consultation) == 1)
        self.assertTrue(links_to_consultation[0].string == 'Test consultation')

        self.browser_do_logout()

    def test_NyRoleManager_wrappers(self):
        self.assertTrue(NyTalkBackConsultation.manage_addLocalRoles == NyRoleManager.manage_addLocalRoles)
        self.assertTrue(NyTalkBackConsultation.manage_setLocalRoles == NyRoleManager.manage_setLocalRoles)
        self.assertTrue(NyTalkBackConsultation.manage_delLocalRoles == NyRoleManager.manage_delLocalRoles)

class CommentSubmissionTestCase(NaayaFunctionalTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        start_date = (date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
        end_date = (date.today() + timedelta(days=10)).strftime('%d/%m/%Y')
        addNyTalkBackConsultation(self.portal.myfolder, title="Test consultation",
            start_date=start_date, end_date=end_date,
            contributor='contributor', submitted=1)
        section_data = {
            'id': 'test-section',
            'title': 'Test section',
            'body': (
                '<p>First paragraph</p>'
                '<p>Second paragraph</p>'
                '<p>Third paragraph</p>'),
        }
        self.consultation = self.portal.myfolder['test-consultation']
        self.consultation._Naaya___Review_TalkBack_Consultation_Permission = ['Contributor']
        self.consultation.addSection(**section_data)
        transaction.commit()
        self.section = self.consultation['test-section']
        self.section_url = 'http://localhost/portal/myfolder/test-consultation/test-section'

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        transaction.commit()

    def test_anonymous_comment(self):
        self.assertEqual(len(self.section['000'].objectIds()), 0)
        self.consultation._Naaya___Review_TalkBack_Consultation_Permission = ['Anonymous']
        transaction.commit()

        self.browser.go(self.section_url + '/000')
        self.assertTrue('Add a comment' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        form['contributor_name:utf8:ustring'] = 'gigi'
        form['message:utf8:ustring'] = 'I has something to say'
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()

        self.assertEqual(len(self.section['000'].objectIds()), 1)
        comment = self.section['000'].objectValues()[0]
        self.assertEqual(comment.contributor, 'anonymous:gigi')
        self.assertEqual(comment.message, 'I has something to say')
        self.assertEqual(comment.title, 'Comment by anonymous:gigi')

    def test_logged_in_comment(self):
        self.browser_do_login('contributor', 'contributor')

        self.browser.go(self.section_url + '/000')
        self.assertTrue('Add a comment' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        form_controls = set(c.name for c in form.controls)
        self.assertTrue('contributor_name:utf8:ustring' not in form_controls)
        form['message:utf8:ustring'] = 'Logged in comment'
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()

        self.assertEqual(len(self.section['000'].objectIds()), 1)
        comment = self.section['000'].objectValues()[0]
        self.assertEqual(comment.contributor, 'contributor')
        self.assertEqual(comment.message, 'Logged in comment')
        self.assertEqual(comment.title_or_id(), 'Comment by contributor')

        self.browser_do_logout()

    def test_comment_with_attachment(self):
        self.browser_do_login('contributor', 'contributor')

        self.browser.go(self.section_url + '/000')
        form = self.browser.get_form('frmAdd')
        form_controls = set(c.name for c in form.controls)
        self.assertTrue('file' not in form_controls)

        self.consultation.allow_file = True
        transaction.commit()

        self.browser.go(self.section_url + '/000')
        form = self.browser.get_form('frmAdd')
        form_controls = set(c.name for c in form.controls)
        self.assertTrue('file' in form_controls)
        form['message:utf8:ustring'] = 'Comment with attachment'
        form.find_control('file').add_file(StringIO('some data'),
            filename='attached.txt', content_type='text/plain; charset=utf-8')
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()

        self.assertEqual(len(self.section['000'].objectIds()), 1)
        comment = self.section['000'].objectValues()[0]
        self.assertEqual(comment.contributor, 'contributor')
        self.assertEqual(comment.message, 'Comment with attachment')

        self.browser.go('%s/000/%s/get_talkback_file' %
            (self.section_url, comment.getId()))
        self.assertEqual(self.browser.get_code(), 200)
        self.assertEqual(self.browser_get_header('content-disposition'),
            'attachment;filename*=UTF-8\'\'attached.txt')
        self.assertEqual(self.browser_get_header('content-type'),
            'text/plain; charset=utf-8')
        self.assertEqual(self.browser.get_html(), 'some data')

        self.browser_do_logout()

    def test_edit_comment(self):
        comment_id = addComment(self.section['000'],
            contributor='contributor', message='original comment')
        transaction.commit()

        self.browser_do_login('admin', '')

        self.browser.go('%s/000/%s/edit_html' % (self.section_url, comment_id))
        form = self.browser.get_form('frmEdit')
        self.assertEqual(form['message:utf8:ustring'].strip(),
                         'original comment')
        form['message:utf8:ustring'] = 'modified comment'
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()

        self.assertEqual(self.section['000'][comment_id].message, 'modified comment')

        self.browser_do_logout()

    def test_owner_edit_comment(self):
        self.browser_do_login('reviewer', 'reviewer')

        comment_id = addComment(self.section['000'],
            contributor='reviewer', message='original comment')
        transaction.commit()

        self.browser.go('%s/000/%s/edit_html' % (self.section_url, comment_id))
        form = self.browser.get_form('frmEdit')

        form['message:utf8:ustring'] = 'modified comment'
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()

        self.assertEqual(self.section['000'][comment_id].message, 'modified comment')

        self.browser_do_logout()

        #login with a different user
        self.browser_do_login('contributor', 'contributor')

        self.browser.go('%s/000/%s/edit_html' % (self.section_url, comment_id))
        self.assertRedirectUnauthorizedPage()

        self.browser_do_logout()

    def test_sanitized_html(self):
        # We only test a couple of obvious cases, to make sure sanitizing
        # is functioning. The library (currently `scrubber`) has more tests.

        tests = [
            ('simple', 'simple'),
            ('hey <script>scripted</script>', 'hey'),
            ('and <a href="javascript:alert(1)">a link</a>',
                'and <a rel="nofollow" class="external">a link</a>'),
        ]

        self.browser_do_login('contributor', 'contributor')

        for test_input, test_output in tests:
            self.browser.go(self.section_url + '/000')
            form = self.browser.get_form('frmAdd')
            form['message:utf8:ustring'] = test_input
            self.browser.clicked(form, form.find_control('message:utf8:ustring'))
            self.browser.submit()

            comment = self.section['000'].objectValues()[0]
            self.assertEqual(comment.message, test_output)
            self.section['000'].manage_delObjects([comment.getId()])
            transaction.commit()

        self.browser_do_logout()

    def test_threaded_comments(self):
        comment1_id = addComment(self.section['000'],
            contributor='contributor', message='original comment')
        transaction.commit()

        self.browser_do_login('contributor', 'contributor')

        self.browser.go('%s/000?reply_to=%s' % (self.section_url, comment1_id))
        form = self.browser.get_form('frmAdd')
        self.assertEqual(form['reply_to'], comment1_id)
        self.assertEqual(form['message:utf8:ustring'],
                         '<p></p><blockquote>original comment</blockquote><p></p>')
        form['message:utf8:ustring'] = ('<p>\n&nbsp;\n</p>\n'
                                        '<blockquote>original comment</blockquote>\n'
                                        '<p>\n&nbsp;\n</p>')
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()

        comment2_id = ( set(self.section['000'].objectIds()) -
                        set([comment1_id])
                      ).pop()
        comment2 = self.section['000'][comment2_id]
        self.assertEqual(comment2.reply_to, comment1_id)
        self.assertEqual(comment2.message, '<blockquote>original comment</blockquote>')

        # make sure we can't add a reply to a non-existent comment
        self.browser.go('%s/000?reply_to=%s' % (self.section_url, comment1_id))
        self.section['000'].manage_delObjects([comment1_id])
        transaction.commit()
        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()

        self.assertEqual(len(self.section['000'].objectIds()), 1,
                         'Should not have created comment with bogus '
                         '`reply_to` value')

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ConsultationBasicTestCase))
    suite.addTest(makeSuite(CommentSubmissionTestCase))
    return suite
