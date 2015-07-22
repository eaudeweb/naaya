from unittest import TestSuite, makeSuite
from Products.Naaya.tests.NaayaTestCase import FunctionalTestCase

class EmailTestCase(FunctionalTestCase):
    def test_mail(self):
        self.layer.mail_divert.clear_log()
        
        self.portal.getEmailTool().sendEmail('test_content', 'test_to', 'test_from', 'test_subject')
        
        smtp_log = self.layer.mail_divert.log
        
        self.failUnlessEqual(len(smtp_log), 3)
        self.failUnlessEqual(smtp_log[0][0], 'init')
        self.failUnlessEqual(smtp_log[1][0], 'sendmail')
        self.failUnlessEqual(smtp_log[2][0], 'quit')
        
        self.failUnlessEqual(smtp_log[1][1]['from'], 'test_from')
        self.failUnlessEqual(smtp_log[1][1]['to'], ['test_to'])
        self.failUnless('Subject: test_subject\n' in smtp_log[1][1]['message'])
        self.failUnless('test_content' in smtp_log[1][1]['message'])
        self.failUnless('Content-Type: text/plain;' in smtp_log[1][1]['message'])
    
    def test_mail_from(self):
        self.layer.mail_divert.clear_log()
        
        self.portal.getEmailTool().sendEmail('test_content', 'test_to_1, test_to_2', 'test_from', 'test_subject')
        
        smtp_log = self.layer.mail_divert.log
        to = smtp_log[1][1]['to']
        
        self.failUnlessEqual(len(to), 2)
        self.failUnless('test_to_1' in to)
        self.failUnless('test_to_2' in to)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(EmailTestCase))
    return suite
