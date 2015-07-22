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

from unittest import TestSuite, makeSuite
from datetime import date, timedelta

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaContent.NyTalkBackConsultation.NyTalkBackConsultation import addNyTalkBackConsultation
from Products.NaayaContent.NyTalkBackConsultation.comment_item import addComment
from Products.NaayaCore.EmailTool.EmailTool import divert_mail


class CommentsAdminTestCase(NaayaFunctionalTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, 'myfolder', contributor='admin', submitted=1)
        start_date = (date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
        end_date = (date.today() + timedelta(days=10)).strftime('%d/%m/%Y')
        addNyTalkBackConsultation(self.portal.myfolder, title="Test consultation",
            start_date=start_date, end_date=end_date,
            contributor='admin', submitted=1)
        consultation = self.portal.myfolder['test-consultation']

        consultation.addSection(
            id='test-section', title='Test section',
            body='<p>First paragraph</p><p>Second paragraph</p>')

        consultation.invitations._send_invitation(
            name='The Invitee', email='invitee@thinkle.edu',
            organization='Thinkle University', notes='Knows his shit',
            inviter_userid='contributor', inviter_name='Contributor Test', message='')
        self.invite_key = consultation.invitations._invites.values()[0].key

        comments = []
        paragraph_000 = consultation['test-section']['000']
        # comment 0
        id0 = addComment(paragraph_000,
                         contributor='contributor',
                         message=u'comment by contributor (0)')
        comments.append(paragraph_000[id0])

        # comment 1
        id1 = addComment(consultation['test-section']['000'],
                         contributor='invite:' + self.invite_key,
                         message=u'invitee comment (1)', approved=False)
        comments.append(paragraph_000[id1])

        transaction.commit()

        self.comments = comments
        self.consultation = self.portal.myfolder['test-consultation']
        self.diverted_mail = divert_mail()
        self.cons_url = 'http://localhost/portal/myfolder/test-consultation'

    def beforeTearDown(self):
        divert_mail(False)
        self.portal.manage_delObjects(['myfolder'])
        transaction.commit()

    def test_list_all_comments(self):
        all_comments = list(self.consultation.admin_comments._iter_comments())
        self.assertEqual(len(all_comments), 2)

        self.assertTrue(self.comments[0] in all_comments)
        self.assertTrue(self.comments[1] in all_comments)

    def test_admin_page(self):
        self.browser_do_login('admin', '')
        self.browser.go(self.cons_url + '/admin_comments')
        html = self.browser.get_html()

        self.assertFalse(self.comments[0].message in html)
        self.assertTrue(self.comments[1].message in html)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(CommentsAdminTestCase))
    return suite
