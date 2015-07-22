# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
# Dragos Chirila - Finsiel Romania

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
