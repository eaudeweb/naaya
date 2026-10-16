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

from unittest import TestSuite, TestLoader, TestCase
from unittest.mock import Mock, MagicMock
from datetime import date, timedelta
from io import BytesIO

import openpyxl

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.talkback.tbconsultation_item import addNyTalkBackConsultation
from naaya.content.talkback.comment_item import addComment
from naaya.content.talkback.invitations import InvitationsContainer
from Products.NaayaCore.EmailTool.EmailTool import divert_mail
from naaya.content.talkback.tests import (invite_contributor,
                                          use_temp_sites_log)


class InvitationTestCase(NaayaFunctionalTestCase):
    def afterSetUp(self):
        use_temp_sites_log(self)
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
        i = list(self.consultation.invitations._invites.values())[0]
        self.assertEqual(i.name, data['name'])
        self.assertEqual(i.email, data['email'])
        self.assertEqual(i.organization, data['organization'])
        self.assertEqual(i.notes, data['notes'])
        self.assertEqual(i.inviter_userid, 'someguy')

        self.assertEqual(len(self.diverted_mail), 1)
        body, addr_to, addr_cc, addr_from, subject = self.diverted_mail[0]
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
        form['name:utf8:string'] = data['name']
        form['email'] = data['email']
        form['organization:utf8:string'] = data['organization']
        form['notes:utf8:string'] = data['notes']
        form['message:utf8:string'] = data['message']
        send_button = form._form.xpath(
            './/input[@name="do"][@value="Send invitation"]')[0]
        self.browser.clicked(form, send_button)
        self.browser.submit()
        self.assertEqual(len(self.consultation.invitations._invites), 1)
        i = list(self.consultation.invitations._invites.values())[0]
        self.assertEqual(i.name, data['name'])
        self.assertEqual(i.email, data['email'])
        self.assertEqual(i.organization, data['organization'])
        self.assertEqual(i.notes, data['notes'])
        self.assertEqual(i.inviter_userid, 'admin')
        self.assertEqual(i.create_date, date.today())

        self.assertEqual(len(self.diverted_mail), 1)
        body, addr_to, addr_cc, addr_from, subject = self.diverted_mail[0]
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
        self.assertFalse(form['allow_reviewer_invites:boolean'])
        form['allow_reviewer_invites:boolean'] = ['on']
        self.browser.clicked(form, form.find_control('title:utf8:string'))
        self.browser.submit()

        self.assertEqual(get_inviter_roles(), ['Reviewer'])

        self.browser.go('http://localhost/portal/myfolder/test-consultation/edit_html')
        form = self.browser.get_form('frmEdit')
        self.assertTrue(form['allow_reviewer_invites:boolean'])

        self.browser.go('http://localhost/portal/myfolder/talkbackconsultation_add_html')
        form = self.browser.get_form('frmAdd')
        self.assertFalse(form['allow_reviewer_invites:boolean'])

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
        use_temp_sites_log(self)
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
        self.invite_key = list(
            self.consultation.invitations._invites.values())[0].key
        self.diverted_mail = divert_mail()
        self.cons_url = 'http://localhost/portal/myfolder/test-consultation'

    def beforeTearDown(self):
        divert_mail(False)
        self.portal.manage_delObjects(['myfolder'])
        transaction.commit()

    def test_key_auth(self):
        # a valid key redirects to the consultation index
        self.browser.go(self.cons_url + '/invitations/welcome?key=' + self.invite_key)
        self.assertEqual(self.browser.get_url(), self.cons_url)
        html = self.browser.get_html()
        self.assertTrue('Welcome, The Invitee.' in html)
        self.assertTrue('Test consultation' in html)
        self.assertFalse(self.invite_key in html)

        self.browser.go(self.cons_url + '/test-section/000')
        html = self.browser.get_html()
        self.assertTrue('The Invitee' in html)
        form = self.browser.get_form('frmAdd')
        form_controls = set(c.name for c in form.controls)
        self.assertTrue('contributor.name:utf8:string:record'
                        not in form_controls)
        form['message:utf8:string'] = 'The invitee speaks!'
        self.browser.clicked(form, form.find_control('message:utf8:string'))
        self.browser.submit()

        paragraph = self.consultation['test-section']['000']
        self.assertEqual(len(paragraph.objectIds()), 1)
        comment = paragraph.objectValues()[0]
        self.assertEqual(comment.contributor.source, 'invite')
        self.assertEqual(comment.contributor.invite, self.invite_key)
        self.assertEqual(comment.message, 'The invitee speaks!')

        self.browser.go(self.cons_url + '/test-section/000')
        html = self.browser.get_html()
        self.assertTrue('The Invitee (invited by Contributor Test)' in html)

    def test_invitee_logout_link(self):
        self.browser.go(self.cons_url)
        self.assertFalse('Commenting as invitee' in self.browser.get_html())

        self.browser.go(self.cons_url + '/invitations/welcome?key=' +
                        self.invite_key)
        html = self.browser.get_html()
        self.assertTrue('Commenting as invitee' in html)
        self.assertTrue('/invitations/welcome?logout=on' in html)

        self.browser.go(self.cons_url + '/invitations/welcome?logout=on')
        self.assertEqual(self.browser.get_url(), self.cons_url)
        self.assertFalse('Commenting as invitee' in self.browser.get_html())
        self.browser.go(self.cons_url + '/test-section/000')
        self.assertRaises(LookupError, self.browser.get_form, 'frmAdd')

    def test_invitee_logout_link(self):
        self.browser.go(self.cons_url)
        self.assertFalse('Commenting as invitee' in self.browser.get_html())

        self.browser.go(self.cons_url + '/invitations/welcome?key=' +
                        self.invite_key)
        html = self.browser.get_html()
        self.assertTrue('Commenting as invitee' in html)
        self.assertTrue('/invitations/welcome?logout=on' in html)

        self.browser.go(self.cons_url + '/invitations/welcome?logout=on')
        self.assertEqual(self.browser.get_url(), self.cons_url)
        self.assertFalse('Commenting as invitee' in self.browser.get_html())
        self.browser.go(self.cons_url + '/test-section/000')
        self.assertRaises(LookupError, self.browser.get_form, 'frmAdd')

    def test_invalid_or_revoked_key(self):
        self.browser.go(self.cons_url + '/invitations/welcome?key=INVALIDVALUE')
        html = self.browser.get_html()
        self.assertTrue('Invalid key' in html)

        self.browser.go(self.cons_url + '/test-section/000')
        self.assertFalse('The Invitee' in self.browser.get_html())
        self.assertRaises(LookupError, self.browser.get_form, 'frmAdd')

        self.browser.go(self.cons_url + '/invitations/welcome?key=' + self.invite_key)
        self.assertTrue('Welcome, The Invitee.' in self.browser.get_html())

        self.consultation.invitations._invites[self.invite_key].enabled = False
        transaction.commit()

        self.browser.go(self.cons_url + '/invitations/welcome?key=' + self.invite_key)
        html = self.browser.get_html()
        self.assertFalse('Welcome, The Invitee.' in html)
        self.assertTrue('Invalid key' in html)

        self.browser.go(self.cons_url + '/test-section/000')
        self.assertFalse('The Invitee' in self.browser.get_html())
        self.assertRaises(LookupError, self.browser.get_form, 'frmAdd')


    def test_invited_comments_admin(self):
        invitation = self.consultation.invitations.get_invitation(
            self.invite_key)
        comment_id = addComment(self.consultation['test-section']['000'],
                                contributor=invite_contributor(invitation),
                                message='invitee comment')
        transaction.commit()

        self.browser_do_login('contributor', 'contributor')

        edit_url = '%s/test-section/000/%s/edit_html' % (self.cons_url, comment_id)
        self.browser.go('%s/test-section/000' % self.cons_url)
        self.assertTrue(edit_url in self.browser.get_html())

        self.browser.go(edit_url)
        self.assertRedirectUnauthorizedPage(False)

        form = self.browser.get_form('frmEdit')
        form['message:utf8:string'] = 'edited'
        self.browser.clicked(form, form.find_control('message:utf8:string'))
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
        self.assertTrue('Welcome, The Invitee.' in self.browser.get_html())
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

class InvitationsContainerTestCase(TestCase):
    def setUp(self):
       self.invitation = InvitationsContainer('bla')
       auth_tool = Mock()
       auth_tool.name_from_userid = Mock(return_value='anUserName')
       self.invitation.getAuthenticationTool = Mock(return_value=auth_tool)

    def test_xcel_export(self):
        # add datetime, list, tuple to the invite object
        keys_in_invite = ['name', 'name_from_userid', 'onlyInInvite']
        keys_in_request = ['name', 'name_from_userid', 'onlyInRequest']
        headers = ['Name', 'Name From Usaerid', 'OnlyInRequest']
        act1 = MagicMock()
        act2 = MagicMock()
        rev1 = MagicMock()
        active = [act1, act2]
        revoked = [rev1]
        for i, inv in enumerate(active + revoked):
            for j, k in enumerate(keys_in_invite):
                setattr(inv, k, 'aValue%d%d' % (i,j))
            # set this also, aotherwise Mock will report a MagicMock as attr fetch
            # and the id inside repr will always vary, ruining our test
            # this way we also test the replacement of None with ''
            setattr(inv, 'onlyInRequest', None)

        options = {
            'invites_active': active,
            'invites_revoked': revoked,
        }
        r = self.invitation._xcel_export_invitations(headers, keys_in_request, options)
        wb = openpyxl.load_workbook(BytesIO(r))
        self.assertEqual(wb.sheetnames,
                         ['Active Invitations', 'Revoked Invitations'])

        def rows(ws):
            return [[c if c is not None else '' for c in row]
                    for row in ws.iter_rows(values_only=True)]
        self.assertEqual(rows(wb['Active Invitations']), [
            headers,
            ['aValue00', 'anUserName', ''],
            ['aValue10', 'anUserName', ''],
        ])
        self.assertEqual(rows(wb['Revoked Invitations']), [
            headers,
            ['aValue20', 'anUserName', ''],
        ])


def test_suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(InvitationTestCase))
    suite.addTest(TestLoader().loadTestsFromTestCase(InviteeCommentTestCase))
    suite.addTest(TestLoader().loadTestsFromTestCase(InvitationsContainerTestCase))
    return suite
