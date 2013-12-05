import os
import time
import random
from email import message_from_file
import tempfile
import shutil
import unittest

from mock import patch, MagicMock

from Products.Naaya.tests.NaayaTestCase import FunctionalTestCase
from Products.NaayaCore.EmailTool.EmailTool import (EmailTool,
                                             save_bulk_email, get_bulk_emails,
                                             check_and_update_valid_emails)
from Products.NaayaCore.EmailTool import EmailTool as EmailToolModule

class EmailTestCase(FunctionalTestCase):
    def test_mail(self):
        self.portal.getEmailTool().sendEmail('test_content',
            'test_to@example.com', 'test_from@example.com', 'test_subject')

        smtp_log = self.mail_log

        self.failUnlessEqual(len(smtp_log), 3)
        self.failUnlessEqual(smtp_log[0][0], 'init')
        self.failUnlessEqual(smtp_log[1][0], 'sendmail')
        self.failUnlessEqual(smtp_log[2][0], 'quit')

        self.failUnlessEqual(smtp_log[1][1]['from'], 'test_from@example.com')
        self.failUnlessEqual(smtp_log[1][1]['to'], ['test_to@example.com'])
        self.failUnless('Subject: test_subject\n' in smtp_log[1][1]['message'])
        self.failUnless('test_content' in smtp_log[1][1]['message'])
        self.failUnless('Content-Type: text/plain;' in
                        smtp_log[1][1]['message'])

    def test_mail_from(self):
        self.portal.getEmailTool().sendEmail('test_content',
            'test_to_1@example.com, test_to_2@example.com',
            'test_from@example.com', 'test_subject')

        smtp_log = self.mail_log
        self.assertEqual(len(smtp_log), 3)
        to = smtp_log[1][1]['to']

        self.failUnlessEqual(len(to), 2)
        self.failUnless('test_to_1@example.com' in to)
        self.failUnless('test_to_2@example.com' in to)

    @patch('Products.NaayaCore.EmailTool.EmailTool.validate_email')
    def test_check_and_update_valid_emails(self, mock_validate_email):
        # make resolvation function always return true (valid)
        mock_validate_email.return_value = True
        emails = ['alreadyBad@edw.ro', 'alreadyBadButExpired@edw.ro', 'notInCache@edw.ro']
        now = time.time()

        obj = MagicMock()
        # init the cache with one value already resolved to invalid
        # we expect the resolvation function not to be called for this email
        obj.checked_emails = {'alreadyBad@edw.ro': (False, now),
                              'alreadyBadButExpired@edw.ro': (False, now - (EmailToolModule.VERIFY_EMAIL_BADADDRESS_TTL + 1)),
                            }
        expected_invalid = ['alreadyBad@edw.ro']
        invalid_emails = check_and_update_valid_emails(obj, emails)
        self.assertEqual(invalid_emails, expected_invalid)

class EmailSaveTestCase(unittest.TestCase):
    def setUp(self):
        from App.config import getConfiguration
        from Products.Naaya.NySite import NySite

        self.config = getConfiguration()
        self.config_patch = patch.object(self.config, 'environment', {},
                                         create=True)
        self.config_patch.start()

        self.environ_patch = patch.dict(os.environ)
        self.environ_patch.start()

        self.portal = NySite('test')
        self.portal.portal_email = EmailTool('id_email_tool', 'Test email tool')

        self.TMP_FOLDER = tempfile.mkdtemp()

    def tearDown(self):
        self.environ_patch.stop()
        self.config_patch.stop()
        shutil.rmtree(self.TMP_FOLDER)

    @patch('naaya.core.site_logging.get_zope_env')
    def test_save_mail(self, get_zope_env):
        get_zope_env.return_value = self.TMP_FOLDER
        tos = ['to1@edw.ro', 'to2@edw.ro']
        filename = save_bulk_email(self.portal, tos[:],
                                   'from@edw.ro', 'Hello!', '\nHello World!\n\n')
        self.assertTrue(os.path.isfile(filename))

        emails = get_bulk_emails(self.portal)

        self.assertEqual(len(emails), 1)
        self.failUnless('content' in emails[0])
        self.failUnless('date' in emails[0])
        self.failUnless('subject' in emails[0])
        self.failUnless('sender' in emails[0])
        self.failUnless('recipients' in emails[0])

        self.assertEqual(emails[0]['content'], '<br/>Hello World!</p><p>')
        self.assertEqual(emails[0]['subject'], 'Hello!')
        self.assertEqual(emails[0]['sender'], 'from@edw.ro')
        self.assertEqual(emails[0]['recipients'], ['to1@edw.ro', 'to2@edw.ro'])
