#####################################################################
#
# GrabUrl.py  Grabbs the XML schema 
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
#
#####################################################################

#Python imports
import urllib

#Zope imports

#Product imports

class GrabUrl(urllib.FancyURLopener):
   """ Create sub-class in order to overide error 206.  This error means a
      partial file is being sent, which is ok in this case.  Do nothing with this error.
   """
   def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
       pass

   def http_error_404(self, url, fp, errcode, errmsg, headers, data=None):
       pass
                   
def grabFromUrl(p_url, p_http_proxy, p_params):
   #gets data from specified URL
   try:
       l_urlgrab = GrabUrl()
       if p_http_proxy != '': l_urlgrab.proxies['http'] = p_http_proxy
       if p_params is None:
           webPage = l_urlgrab.open(p_url)
       else:
           webPage = l_urlgrab.open(p_url, urllib.urlencode(p_params))
       data = webPage.read()
       ctype = webPage.headers['Content-Type']
       return (data, ctype)
   except:
       return (None, 'text/x-unknown-content-type')
