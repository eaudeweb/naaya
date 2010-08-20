from unittest import TestSuite, makeSuite
from Products.Naaya.tests.NaayaTestCase import FunctionalTestCase

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

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(EmailTestCase))
    return suite
