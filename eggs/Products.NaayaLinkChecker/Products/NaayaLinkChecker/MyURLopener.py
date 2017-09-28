__version__ = '''$Revision$'''
import urllib

class MyURLopener(urllib.FancyURLopener):

    http_error_default = urllib.URLopener.http_error_default

    version = "Naaya Link Checker/%s" % __version__

    def __init__(self, *args, **kw):
        urllib.FancyURLopener.__init__(self, *args, **kw)

    def http_error_401(self, url, fp, errcode, errmsg, headers):
        return self.http_error_default(url, fp, errcode, errmsg, headers)
