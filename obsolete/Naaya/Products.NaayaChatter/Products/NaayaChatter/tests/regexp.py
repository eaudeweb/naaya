import re
import unittest


def linkifyURLS(string):
    def replace(match):
        txt = match.group('uri').replace('&amp;', '&')
        #if txt.startswith('http://'):
        if match.group('uri_proto'):
            uri = txt
        else:
            uri = 'http://' + txt
        return '<a href="%s">%s</a>' % (uri, txt)
    
    
    initial_lookbehind = r'(?<![\d\w\-])'
    host_component = r'[\w\d\-]+'
    host_port = r'\:\d+'
    path = r'/[^\s]*'
    get_params = r'\?[\w\d\=\%\&\;\-]*(?<!;)'
    
    regexp = r'(?P<uri>' \
            + initial_lookbehind \
            + r'((?P<uri_proto>\w+\://)|www\.)' \
            + host_component + r'(\.' + host_component + r')*' + r'('+ host_port + r')?' \
            + r'(' + path + r')?' \
            + r'(' + get_params + r')?' \
        + r')'
    
    return re.sub(regexp, replace, string)



class TestLinkify(unittest.TestCase):


    def test_nolink(self):
        self.failUnlessEqual(linkifyURLS("a"), "a")

    def test_www_url(self):
        self.failUnlessEqual(linkifyURLS("www.google.com"), '<a href="http://www.google.com">www.google.com</a>')
        self.failUnlessEqual(linkifyURLS("blabla www.google.com yada yada"), 'blabla <a href="http://www.google.com">www.google.com</a> yada yada')
        self.failUnlessEqual(linkifyURLS("blabla www.google.com. yada yada"), 'blabla <a href="http://www.google.com">www.google.com</a>. yada yada')

    def test_http_url(self):
        self.failUnlessEqual(linkifyURLS("http://mail.google.com"), '<a href="http://mail.google.com">http://mail.google.com</a>')
        self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com. grr"), 'yarr <a href="http://mail.google.com">http://mail.google.com</a>. grr')

    def test_other_protocols(self):
        self.failUnlessEqual(linkifyURLS("yarr ftp://mail.google.com. grr"), 'yarr <a href="ftp://mail.google.com">ftp://mail.google.com</a>. grr')
        self.failUnlessEqual(linkifyURLS("yarr ssh://mail.google.com. grr"), 'yarr <a href="ssh://mail.google.com">ssh://mail.google.com</a>. grr')

    def test_http_numeric_url(self):
        self.failUnlessEqual(linkifyURLS("yarr http://10.0.0.1 grr"), 'yarr <a href="http://10.0.0.1">http://10.0.0.1</a> grr')
        self.failUnlessEqual(linkifyURLS("yarr http://10.0.0.1:8080/index.html grr"), 'yarr <a href="http://10.0.0.1:8080/index.html">http://10.0.0.1:8080/index.html</a> grr')

    def test_http_url_endings(self):
        self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com.uk grr"), 'yarr <a href="http://mail.google.com.uk">http://mail.google.com.uk</a> grr')
        self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com?a=lala&amp;b=weewee. grr"), 'yarr <a href="http://mail.google.com?a=lala&b=weewee">http://mail.google.com?a=lala&b=weewee</a>. grr')
        self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com?a=lala&amp;b=weewee, grr"), 'yarr <a href="http://mail.google.com?a=lala&b=weewee">http://mail.google.com?a=lala&b=weewee</a>, grr')
        self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com?a=lala-lala-ere&amp;b=weewee; grr"), 'yarr <a href="http://mail.google.com?a=lala-lala-ere&b=weewee">http://mail.google.com?a=lala-lala-ere&b=weewee</a>; grr')
        #self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com?a=lala&amp;b=weewee;t grr"), 'yarr <a href="http://mail.google.com?a=lala&b=weewee">http://mail.google.com?a=lala&b=weewee</a>;t grr')

    def test_with_parantheses(self):
        self.failUnlessEqual(linkifyURLS("yarr (http://mail.google.com?a=lala&amp;b=weewee) grr"), 'yarr (<a href="http://mail.google.com?a=lala&b=weewee">http://mail.google.com?a=lala&b=weewee</a>) grr')
        self.failUnlessEqual(linkifyURLS("yarr ( http://mail.google.com?a=lala&amp;b=weewee ) grr"), 'yarr ( <a href="http://mail.google.com?a=lala&b=weewee">http://mail.google.com?a=lala&b=weewee</a> ) grr')
        self.failUnlessEqual(linkifyURLS("yarr [http://mail.google.com?a=lala&amp;b=weewee] grr"), 'yarr [<a href="http://mail.google.com?a=lala&b=weewee">http://mail.google.com?a=lala&b=weewee</a>] grr')
        self.failUnlessEqual(linkifyURLS("yarr [ http://mail.google.com?a=lala&amp;b=weewee ] grr"), 'yarr [ <a href="http://mail.google.com?a=lala&b=weewee">http://mail.google.com?a=lala&b=weewee</a> ] grr')
        self.failUnlessEqual(linkifyURLS("yarr [ http://mail.google.com.uk?a=lala&amp;b=weewee ] grr"), 'yarr [ <a href="http://mail.google.com.uk?a=lala&b=weewee">http://mail.google.com.uk?a=lala&b=weewee</a> ] grr')

    def test_with_paths(self):
        self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com.uk/mail grr"), 'yarr <a href="http://mail.google.com.uk/mail">http://mail.google.com.uk/mail</a> grr')
        self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com.uk/mail/a/b.html grr"), 'yarr <a href="http://mail.google.com.uk/mail/a/b.html">http://mail.google.com.uk/mail/a/b.html</a> grr')
        self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com.uk/mail/a/ grr"), 'yarr <a href="http://mail.google.com.uk/mail/a/">http://mail.google.com.uk/mail/a/</a> grr')

    def test_with_get_params(self):
        self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com?a=lala&amp;b=weewee grr"), 'yarr <a href="http://mail.google.com?a=lala&b=weewee">http://mail.google.com?a=lala&b=weewee</a> grr')
        self.failUnlessEqual(linkifyURLS("yarr http://mail.google.com.uk/mail?user=david&amp;pass=david grr"), 'yarr <a href="http://mail.google.com.uk/mail?user=david&pass=david">http://mail.google.com.uk/mail?user=david&pass=david</a> grr')


if __name__ == "__main__":
    unittest.main()