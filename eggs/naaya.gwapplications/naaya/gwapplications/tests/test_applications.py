import unittest
from unittest.mock import Mock, patch

from naaya.groupware.tests import GWTestCase
from naaya.gwapplications import application_item
from naaya.gwapplications.application_item import GWApplication, make_unicode
from naaya.gwapplications.applications import GWApplications


class MakeUnicodeTest(unittest.TestCase):

    def test_make_unicode(self):
        self.assertEqual(make_unicode('Ion'), 'Ion')
        self.assertEqual(make_unicode('Șt'.encode('utf-8')), 'Șt')
        self.assertEqual(make_unicode(b'Fran\xe7ois'), 'Fran\xe7ois')


class ApplicationsTest(GWTestCase):

    def afterSetUp(self):
        self.app._setObject('applications', GWApplications(
            'applications', 'Applications', 'admin@example.com',
            'from@example.com'))
        self.applications = self.app.applications
        self.applications._setObject('newig-x', GWApplication(
            'newig-x', 'New IG', 'anne', useremail='anne@example.com',
            username=b'Ana-Maria \xc8\x98t', site_title='New IG'))
        self.application = self.applications['newig-x']
        self.source = Mock()
        self.patches = [
            patch.object(GWApplications.email_sender, 'sendEmail'),
            patch('Products.NaayaCore.AuthenticationTool.AuthenticationTool.'
                  'AuthenticationTool.manageAddSource'),
            patch('Products.NaayaCore.AuthenticationTool.AuthenticationTool.'
                  'AuthenticationTool.getSources',
                  Mock(return_value=[self.source])),
            patch.object(application_item, 'notify'),
        ]
        self.send_email, self.add_source = [p.start()
                                            for p in self.patches[:2]]
        for p in self.patches[2:]:
            p.start()

    def beforeTearDown(self):
        for p in self.patches:
            p.stop()

    def test_approve(self):
        self.application.approve(id='newig', title='New IG',
                                 subtitle='Sub', description='About',
                                 admin_comments='Welcome')
        portal = self.app['newig']
        self.assertEqual(portal.title, 'New IG')
        self.assertEqual(portal.administrator_email, 'anne@example.com')
        self.assertEqual(self.add_source.call_args.args[0],
                         self.app.acl_users.absolute_url(1))
        self.source.addUserRoles.assert_called_once_with(
            name='anne', roles=['Administrator'], user_location='Users')
        self.assertTrue(self.application.approved)
        self.assertFalse(self.application.rejected)
        self.assertEqual(len(self.application.approved_on), 1)
        self.assertEqual(self.application.created_path, 'newig')
        self.assertEqual(self.application.created_url(),
                         portal.absolute_url())
        body, mail_to, mail_from, subject = self.send_email.call_args.args
        self.assertEqual((mail_to, mail_from, subject),
                         ('anne@example.com', 'from@example.com',
                          'IG application approved'))
        self.assertIn('Welcome', body)
        self.assertIn(portal.absolute_url(), body)
        event, = application_item.notify.call_args.args
        self.assertIs(event.application, self.application)

    def test_reject(self):
        self.application.reject(admin_comments='Not now')
        self.assertTrue(self.application.rejected)
        self.assertFalse(self.application.approved)
        self.assertIsNotNone(self.application.pretty_rejected_date)
        body, mail_to, mail_from, subject = self.send_email.call_args.args
        self.assertEqual((mail_to, mail_from), ('anne@example.com',
                                                'from@example.com'))
        self.assertIn('Not now', body)
        self.assertNotIn('newig', self.app.objectIds())

    def test_new_application_mail(self):
        self.applications.send_new_application_mail(self.application)
        body, mail_to, mail_from, subject = self.send_email.call_args.args
        self.assertEqual((mail_to, mail_from), ('admin@example.com',
                                                'from@example.com'))
        self.assertIn('Ana-Maria Șt', body)
        self.assertIn(self.applications.absolute_url() + '/basket_html',
                      body)

    def test_application_data(self):
        data = self.application.get_application_data()
        self.assertEqual(data['username'], 'Ana-Maria Șt')
        self.assertIsNone(self.application.get_latest_approval_date())
        self.assertIsNone(self.application.pretty_approved_date)
