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


class InvitationTestCase(NaayaFunctionalTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, 'myfolder', contributor='admin', submitted=1)
        start_date = (date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
        end_date = (date.today() + timedelta(days=10)).strftime('%d/%m/%Y')
        addNyTalkBackConsultation(self.portal.myfolder, title="Test consultation",
            start_date=start_date, end_date=end_date,
            contributor='admin', submitted=1)
        transaction.commit()
        self.consultation = self.portal.myfolder['test-consultation']
        self.diverted_mail = divert_mail()
        self.cons_url = 'http://localhost/portal/myfolder/test-consultation'

    def beforeTearDown(self):
        divert_mail(False)
        self.portal.manage_delObjects(['myfolder'])
        transaction.commit()

    def test_invite(self):
        data = {
            'name': 'The Invitee',
            'email': 'invitee@thinkle.edu',
            'organization': 'Thinkle University',
            'notes': 'Knows his shit',
            'message': 'Hi Invitee, please enlighten us.',
            'inviter_userid': 'someguy',
            'inviter_name': 'Some Guy',
        }
        self.consultation.invitations._send_invitation(**data)
        self.assertEqual(len(self.consultation.invitations._invites), 1)
        i = self.consultation.invitations._invites.values()[0]
        self.assertEqual(i.name, data['name'])
        self.assertEqual(i.email, data['email'])
        self.assertEqual(i.organization, data['organization'])
        self.assertEqual(i.notes, data['notes'])
        self.assertEqual(i.inviter_userid, 'someguy')

        self.assertEqual(len(self.diverted_mail), 1)
        body, addr_to, addr_from, subject = self.diverted_mail[0]
        self.assertEqual(addr_to, [data['email']])
        # we modify `body` because the message is automatically wrapped.
        self.assertTrue(data['message'] in body.replace('\n', ' '))

    def test_invite_page(self):
        data = {
            'name': 'The Invitee',
            'email': 'invitee@thinkle.edu',
            'organization': 'Thinkle University',
            'notes': 'Knows his shit',
            'message': 'Hi Invitee, please enlighten us.',
        }
        self.assertEqual(len(self.consultation.invitations._invites), 0)
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/test-consultation/invitations/create')
        form = self.browser.get_form('invite')
        form['name:utf8:ustring'] = data['name']
        form['email'] = data['email']
        form['organization:utf8:ustring'] = data['organization']
        form['notes:utf8:ustring'] = data['notes']
        form['message:utf8:ustring'] = data['message']
        for control in form.controls:
            if control.name == 'do' and control.value == 'Send invitation':
                self.browser.clicked(form, control)
        self.browser.submit()
        self.assertEqual(len(self.consultation.invitations._invites), 1)
        i = self.consultation.invitations._invites.values()[0]
        self.assertEqual(i.name, data['name'])
        self.assertEqual(i.email, data['email'])
        self.assertEqual(i.organization, data['organization'])
        self.assertEqual(i.notes, data['notes'])
        self.assertEqual(i.inviter_userid, 'admin')
        self.assertEqual(i.create_date, date.today())

        self.assertEqual(len(self.diverted_mail), 1)
        body, addr_to, addr_from, subject = self.diverted_mail[0]
        self.assertEqual(addr_to, [data['email']])
        # we modify `body` because the message is automatically wrapped.
        self.assertTrue(data['message'] in body.replace('\n', ' '))

        self.browser_do_logout()

    def test_permission(self):
        self.browser_do_login('contributor', 'contributor')

        self.browser.go('http://localhost/portal/myfolder/test-consultation/invitations/create')
        self.assertRedirectUnauthorizedPage()

        self.consultation._Naaya___Invite_to_TalkBack_Consultation_Permission = ['Contributor']
        transaction.commit()

        self.browser.go('http://localhost/portal/myfolder/test-consultation/invitations/create')
        self.assertRedirectLoginPage(False)
        self.assertRedirectUnauthorizedPage(False)

        self.browser_do_logout()

    def test_edit_permission(self):
        def get_inviter_roles():
            return getattr(self.consultation,
                           '_Naaya___Invite_to_TalkBack_Consultation_Permission',
                           [])
        self.assertEqual(get_inviter_roles(), [])

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/test-consultation/edit_html')
        form = self.browser.get_form('frmEdit')
        self.assertEqual(form['allow_reviewer_invites:boolean'], [])
        form['allow_reviewer_invites:boolean'] = ['on']
        self.browser.clicked(form, form.find_control('title:utf8:ustring'))
        self.browser.submit()

        self.assertEqual(get_inviter_roles(), ['Reviewer'])

        self.browser.go('http://localhost/portal/myfolder/test-consultation/edit_html')
        form = self.browser.get_form('frmEdit')
        self.assertEqual(form['allow_reviewer_invites:boolean'], ['on'])

        self.browser.go('http://localhost/portal/myfolder/talkbackconsultation_add_html')
        form = self.browser.get_form('frmAdd')
        self.assertEqual(form['allow_reviewer_invites:boolean'], [])

        self.browser_do_logout()

    def test_manage_invites(self):
        data = {
            'name': 'The Invitee',
            'email': 'invitee@thinkle.edu',
            'organization': 'Thinkle University',
            'notes': 'Knows his shit',
        }
        create_invitation = self.consultation.invitations._create_invitation
        key1 = create_invitation(inviter_userid='someguy', **data)
        key2 = create_invitation(inviter_userid='reviewer', **data)
        self.consultation.allow_reviewer_invites = True
        transaction.commit()

        self.browser_do_login('admin', '')
        self.browser.go(self.cons_url + '/invitations')
        html = self.browser.get_html()
        self.assertTrue(key1 in html)
        self.assertTrue(key2 in html)
        self.browser_do_logout()

        self.browser_do_login('reviewer', 'reviewer')
        self.browser.go(self.cons_url + '/invitations')
        self.assertAccessDenied(False)
        html = self.browser.get_html()
        self.assertTrue(key1 not in html)
        self.assertTrue(key2 in html)

        for form in self.browser._browser.forms():
            try:
                if form['key'] == key2:
                    break
            except: pass
        else:
            self.fail('Could not find invitation')
        self.browser.clicked(form, form.find_control('key'))
        self.browser.submit()

        self.assertFalse(self.consultation.invitations._invites[key2].enabled)

        self.browser_do_logout()

class InviteeCommentTestCase(NaayaFunctionalTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, 'myfolder', contributor='admin', submitted=1)
        start_date = (date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
        end_date = (date.today() + timedelta(days=10)).strftime('%d/%m/%Y')
        addNyTalkBackConsultation(self.portal.myfolder, title="Test consultation",
            start_date=start_date, end_date=end_date,
            contributor='admin', submitted=1)
        consultation = self.portal.myfolder['test-consultation']
        consultation.invitations._send_invitation(
            name='The Invitee', email='invitee@thinkle.edu',
            organization='Thinkle University', notes='Knows his shit',
            inviter_userid='contributor', inviter_name='Contributor Test', message='')
        consultation.addSection(
            id='test-section', title='Test section',
            body='<p>First paragraph</p><p>Second paragraph</p>')
        transaction.commit()

        self.consultation = self.portal.myfolder['test-consultation']
        self.invite_key = self.consultation.invitations._invites.values()[0].key
        self.diverted_mail = divert_mail()
        self.cons_url = 'http://localhost/portal/myfolder/test-consultation'

    def beforeTearDown(self):
        divert_mail(False)
        self.portal.manage_delObjects(['myfolder'])
        transaction.commit()

    def test_key_auth(self):
        self.browser.go(self.cons_url + '/invitations/welcome?key=' + self.invite_key)
        html = self.browser.get_html()
        self.assertTrue('You have been invited' in html)
        self.assertTrue('The Invitee' in html)
        self.assertTrue('Test consultation' in html)
        self.assertTrue('Contributor Test' in html)
        self.assertFalse(self.invite_key in html)

        self.browser.go(self.cons_url + '/test-section/000')
        html = self.browser.get_html()
        self.assertTrue('The Invitee' in html)
        form = self.browser.get_form('frmAdd')
        form_controls = set(c.name for c in form.controls)
        self.assertTrue('contributor_name:utf8:ustring' not in form_controls)
        form['message:utf8:ustring'] = 'The invitee speaks!'
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()

        paragraph = self.consultation['test-section']['000']
        self.assertEqual(len(paragraph.objectIds()), 1)
        comment = paragraph.objectValues()[0]
        self.assertEqual(comment.contributor, 'invite:' + self.invite_key)
        self.assertEqual(comment.message, 'The invitee speaks!')

        self.browser.go(self.cons_url + '/test-section/000')
        html = self.browser.get_html()
        self.assertTrue('The Invitee (invited by Contributor Test)' in html)

    def test_invalid_or_revoked_key(self):
        self.browser.go(self.cons_url + '/invitations/welcome?key=INVALIDVALUE')
        html = self.browser.get_html()
        self.assertTrue('Invalid key' in html)

        self.browser.go(self.cons_url + '/test-section/000')
        self.assertFalse('The Invitee' in self.browser.get_html())
        self.assertEqual(self.browser.get_form('frmAdd'), None)

        self.browser.go(self.cons_url + '/invitations/welcome?key=' + self.invite_key)
        self.assertTrue('You have been invited' in self.browser.get_html())

        self.consultation.invitations._invites[self.invite_key].enabled = False
        transaction.commit()

        self.browser.go(self.cons_url + '/invitations/welcome?key=' + self.invite_key)
        html = self.browser.get_html()
        self.assertFalse('You have been invited' in html)
        self.assertTrue('Invalid key' in html)

        self.browser.go(self.cons_url + '/test-section/000')
        self.assertFalse('The Invitee' in self.browser.get_html())
        self.assertEqual(self.browser.get_form('frmAdd'), None)

    def test_hide_unapproved(self):
        comment_id = addComment(self.consultation['test-section']['000'],
                                contributor='invite:' + self.invite_key,
                                message=u'invitee comment',
                                approved=False)
        transaction.commit()

        self.browser.go(self.cons_url + '/test-section/000')
        html = self.browser.get_html()
        self.assertFalse('The Invitee (invited by Contributor Test)' in html)
        self.assertFalse('invitee comment' in html)
        self.assertFalse('This comment is awaiting approval' in html)

        self.browser.go(self.cons_url + '/invitations/welcome?key=' + self.invite_key)
        self.browser.go(self.cons_url + '/test-section/000')
        html = self.browser.get_html()
        self.assertTrue('The Invitee (invited by Contributor Test)' in html)
        self.assertTrue('invitee comment' in html)
        self.assertTrue('This comment is awaiting approval' in html)

        comment = self.consultation['test-section']['000'][comment_id]
        comment.approved = True
        transaction.commit()

        self.browser.go(self.cons_url + '/test-section/000')
        html = self.browser.get_html()
        self.assertTrue('The Invitee (invited by Contributor Test)' in html)
        self.assertTrue('invitee comment' in html)
        self.assertFalse('This comment is awaiting approval' in html)

    def test_approve(self):
        comment_id = addComment(self.consultation['test-section']['000'],
                                contributor='invite:' + self.invite_key,
                                message=u'invitee comment',
                                approved=False)
        transaction.commit()
        paragraph_url = self.cons_url + '/test-section/000'
        approve_url = paragraph_url + '/' + comment_id + '/approve'

        comment = self.consultation['test-section']['000'][comment_id]
        self.assertFalse(comment.approved)

        self.browser_do_login('contributor', 'contributor')

        self.browser.go(paragraph_url)
        for form in self.browser._browser.forms():
            if form.action == approve_url:
                break
        else:
            self.fail('Could not find approve form')
        self.browser.clicked(form, form.controls[0])
        self.browser.submit()

        self.assertTrue(comment.approved)
        self.assertEqual(self.browser.get_url(), paragraph_url)

        self.browser.go(paragraph_url)
        for form in self.browser._browser.forms():
            if form.action == approve_url:
                self.fail('no comments should be awaiting approval')

        self.browser_do_logout()

    def test_invited_comments_admin(self):
        comment_id = addComment(self.consultation['test-section']['000'],
                                contributor='invite:' + self.invite_key,
                                message=u'invitee comment')
        transaction.commit()

        self.browser_do_login('contributor', 'contributor')

        edit_url = '%s/test-section/000/%s/edit_html' % (self.cons_url, comment_id)
        self.browser.go('%s/test-section/000' % self.cons_url)
        self.assertTrue(edit_url in self.browser.get_html())

        self.browser.go(edit_url)
        self.assertRedirectUnauthorizedPage(False)

        form = self.browser.get_form('frmEdit')
        form['message:utf8:ustring'] = 'edited'
        self.browser.clicked(form, form.find_control('message:utf8:ustring'))
        self.browser.submit()
        self.assertRedirectUnauthorizedPage(False)

        self.browser_do_logout()

    def test_restricted_access(self):
        self.portal.myfolder._View_Permission = ('Administrator', 'Reviewer')
        transaction.commit()

        section_url = self.cons_url + '/test-section'
        paragraph_url = section_url + '/000'
        paragraph_embedded_url = paragraph_url + '/embedded_html'
        invite_url = self.cons_url + '/invitations/welcome?key=' + self.invite_key

        for url in [self.cons_url, section_url,
                    paragraph_url, paragraph_embedded_url]:
            self.browser.go(url)
            self.assertAccessDenied(True, url)

        self.browser.go(invite_url)

        for url in [self.cons_url, section_url,
                    paragraph_url, paragraph_embedded_url]:
            self.browser.go(url)
            self.assertAccessDenied(False, url)

        self.browser.go(self.cons_url + '/manage_main')
        self.assertAccessDenied()

    def test_auth_precedence(self):
        welcome_url = self.cons_url + '/invitations/welcome'

        # first, try as 'admin'
        self.browser_do_login('admin', '')
        self.browser.go(self.cons_url)
        self.assertTrue('Manage comments' in self.browser.get_html())
        self.browser.go(self.cons_url + '/invitations')
        self.assertAccessDenied(False)

        # next authenticate using a key. we should not see admin buttons anymore.
        self.browser.go(welcome_url + '?key=' + self.invite_key)
        self.assertTrue(welcome_url + '?logout=on' in self.browser.get_html())
        self.browser.go(self.cons_url)
        self.assertTrue('Manage comments' not in self.browser.get_html())
        # but if we really go to a protected page, zope will authenticate us as admin
        self.browser.go(self.cons_url + '/invitations')
        self.assertAccessDenied(False)

        # 'log out' from invited access; should resume 'admin' login
        self.browser.go(welcome_url + '?logout=on')
        self.browser.go(self.cons_url)
        self.assertTrue('Manage comments' in self.browser.get_html())
        self.browser.go(self.cons_url + '/invitations')
        self.assertAccessDenied(False)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(InvitationTestCase))
    suite.addTest(makeSuite(InviteeCommentTestCase))
    return suite
