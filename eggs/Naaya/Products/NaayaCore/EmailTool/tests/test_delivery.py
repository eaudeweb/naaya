import os
import shutil
import tempfile
import unittest
from unittest import mock

import transaction
from zope.component import getGlobalSiteManager, queryUtility
from zope.sendmail.interfaces import IMailDelivery

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.EmailTool import EmailTool as email_module
from Products.NaayaCore.EmailTool.EmailTool import (
    EmailTool, check_cached_valid_emails, configure_mail_queue,
    create_message, get_mail_queue, send_by_delivery, _mail_in_queue)


class EmailHelpersTest(unittest.TestCase):

    def test_filter_disabled_users(self):
        agent = mock.Mock()
        agent.search_user_by_email.side_effect = lambda e: {
            'off@example.com': [{'status': 'disabled'}],
            'on@example.com': [{'status': ''}]}.get(e, [])
        tool = EmailTool('id_email_tool', 'Email tool')
        self.assertEqual(sorted(tool._filter_disabled_users(
            ['off@example.com', 'on@example.com', 'x@example.com'], agent)),
            ['on@example.com', 'x@example.com'])

    def test_check_cached_valid_emails(self):
        self.assertEqual(check_cached_valid_emails(None, 'a@example.com'),
                         ({}, []))
        self.assertEqual(
            check_cached_valid_emails(None, ['a@example.com', 'no-at-sign',
                                             'b@bad']),
            ({'no-at-sign': False, 'b@bad': False}, []))


class MailQueueTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.queue_path = os.path.join(self.tmp, 'queue')
        patcher = mock.patch.dict(os.environ,
                                  {'NAAYA_MAIL_QUEUE': self.queue_path})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.gsm = getGlobalSiteManager()
        self.old_delivery = queryUtility(IMailDelivery, 'naaya-mail-delivery')

    def tearDown(self):
        self.gsm.unregisterUtility(provided=IMailDelivery,
                                   name='naaya-mail-delivery')
        if self.old_delivery is not None:
            self.gsm.registerUtility(self.old_delivery, IMailDelivery,
                                     'naaya-mail-delivery')
        shutil.rmtree(self.tmp)

    def test_queue(self):
        configure_mail_queue()
        delivery = queryUtility(IMailDelivery, 'naaya-mail-delivery')
        message = create_message('queued body', ['to@example.com'],
                                 'from@example.com', 'Queued')
        transaction.begin()
        send_by_delivery(delivery, 'from@example.com', ['to@example.com'],
                         message)
        self.assertEqual(get_mail_queue(None), [])
        transaction.commit()

        [queued] = get_mail_queue(None)
        self.assertEqual(queued['subject'], 'Queued')
        self.assertEqual(queued['recipients'], ['to@example.com'])
        self.assertEqual(queued['content'], b'queued body')
        check = {'recipients': ['to@example.com'], 'subject': 'Queued'}
        self.assertEqual(_mail_in_queue(None, queued['filename'], check),
                         'In sending queue')
        self.assertEqual(_mail_in_queue(None, 'other.name', check), 'Sent')

    def test_abort_discards_message(self):
        configure_mail_queue()
        delivery = queryUtility(IMailDelivery, 'naaya-mail-delivery')
        transaction.begin()
        send_by_delivery(delivery, 'from@example.com', ['to@example.com'],
                         create_message('x', ['to@example.com'],
                                        'from@example.com', 'Aborted'))
        transaction.abort()
        self.assertEqual(get_mail_queue(None), [])


class SendEmailTest(NaayaTestCase):

    def test_cc_recipients_split(self):
        diverted = email_module.divert_mail()
        try:
            self.portal.getEmailTool().sendEmail(
                'body', 'to@example.com', 'from@example.com', 'Subject',
                p_cc='a@example.com; b@example.com,c@example.com')
            self.assertEqual(diverted[0][1], ['to@example.com'])
            self.assertEqual(diverted[0][2], ['a@example.com',
                                              'b@example.com',
                                              'c@example.com'])
        finally:
            email_module.divert_mail(False)

    def test_addr_from(self):
        email_tool = self.portal.getEmailTool()
        self.portal.mail_address_from = 'site@example.com'
        self.assertEqual(email_tool.get_addr_from(), 'site@example.com')
        self.portal.mail_address_from = ''
        self.assertTrue(email_tool.get_addr_from().startswith(
            'notifications@'))
