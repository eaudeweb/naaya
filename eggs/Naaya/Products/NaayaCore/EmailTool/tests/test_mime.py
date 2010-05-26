import unittest

from Products.NaayaCore.EmailTool.EmailTool import create_message

class MimeTest(unittest.TestCase):
    def test_simple_message(self):
        output = create_message('hello world!', 'x@edw.ro', 'y@edw.ro', 'hi')
        assert 'From: y@edw.ro' in output
        assert 'To: x@edw.ro' in output
        assert 'Subject: hi' in output
        assert 'hello world!' in output

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MimeTest))
    return suite
