from unittest import TestSuite, makeSuite
from Products.Naaya.tests.NaayaTestCase import FunctionalTestCase

def divert_mail():
    from Products.NaayaCore.EmailTool import EmailTool

    class smtplib_replacement(object):
        class SMTP:
            def __init__(s, server, port):
                mail_log.append( ('init', {}) )

            def sendmail(s, from_addr, to_addr, message):
                mail_log.append( ('sendmail',
                                  {'from': from_addr,
                                   'to': to_addr,
                                   'message': message}) )

            def quit(s):
                mail_log.append( ('quit', {}) )

    _orig_smtplib = EmailTool.smtplib
    EmailTool.smtplib = smtplib_replacement
    mail_log = []

    def restore():
        EmailTool.smtplib = _orig_smtplib

    return mail_log, restore

class EmailTestCase(FunctionalTestCase):
    def setUp(self):
        self.mail_log, self._restore_mail = divert_mail()

    def tearDown(self):
        self._restore_mail()

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

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(EmailTestCase))
    return suite
