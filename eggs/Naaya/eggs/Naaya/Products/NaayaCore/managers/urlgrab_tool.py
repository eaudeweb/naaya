import urllib



class urlgrab_tool(urllib.FancyURLopener):
    """ Create sub-class in order to overide error 206.  This error means a
       partial file is being sent, which is ok in this case.  Do nothing with this error.
    """
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass

    def http_error_404(self, url, fp, errcode, errmsg, headers, data=None):
        pass
