import unittest

from Products.NaayaCore.EmailTool.EmailTool import create_message

class MimeTest(unittest.TestCase):
    def test_simple_message(self):
        output = create_message('hello world!', 'x@edw.ro', 'y@edw.ro', 'hi').as_string()
        assert 'From: y@edw.ro\n' in output
        assert 'To: x@edw.ro\n' in output
        assert 'Subject: hi\n' in output
        assert 'Date: ' in output
        assert 'hello world!' in output

    def test_unicode_body(self):
        body = u'h\u00E9ll\u00F8 w\u00F6rl\u1E0B\u203D'
        output = create_message(body, 'x@edw.ro', 'y@edw.ro', 'hi').as_string()
        assert 'Content-Type: text/plain; charset="utf-8"\n' in output
        assert 'Content-Transfer-Encoding: quoted-printable\n' in output
        assert 'h=C3=A9ll=C3=B8 w=C3=B6rl=E1=B8=8B=E2=80=BD' in output

    def test_unicode_subject(self):
        subject = u'h\u00E9ll\u00F8 w\u00F6rl\u1E0B\u203D'
        output = create_message('asdf', 'x@edw.ro', 'y@edw.ro', subject).as_string()
        assert 'Subject: =?utf-8?b?aMOpbGzDuCB3w7ZybOG4i+KAvQ==?=\n' in output

    def test_newline_in_subject(self):
        # prevent header injection
        subject = "Hello\nBcc: hacker@domain.com"
        output = create_message('asdf', 'x@edw.ro', 'y@edw.ro', subject).as_string()
        assert ('Subject: =?utf-8?q?Hello=0D=0A'
                'Bcc=3A_hacker=40domain=2Ecom?=\n' in output)

    def test_unicode_recipient(self):
        recipient = u'H\u00E9ll\u00F8 Sayer <hello.sayer@edw.ro>'
        output = create_message('hello world!', recipient, 'y@edw.ro', 'hi').as_string()
        assert ('To: =?utf-8?b?SMOpbGzDuCBTYXllciA8aGV'
                'sbG8uc2F5ZXJAZWR3LnJvPg==?=' in output)

    def test_multiple_recipients(self):
        recipients = ['%s@edw.ro' % name for name in 'abcdefghijklm']
        output = create_message('hello world!', recipients, 'y@edw.ro', 'hi').as_string()
        assert ('To: a@edw.ro, b@edw.ro, c@edw.ro, d@edw.ro, '
                'e@edw.ro, f@edw.ro, g@edw.ro,\n'
                '\th@edw.ro, i@edw.ro, j@edw.ro, '
                'k@edw.ro, l@edw.ro, m@edw.ro\n' in output)
