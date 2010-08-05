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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
#$Id: $
""" Decorators
"""
from webdav.common import rfc1123_date

_marker = []

def cachable(method):
    def wrapper(self, REQUEST, RESPONSE, **kwargs):
        """ Look in cache:
            - if item exists in cache:
                if If-Modified-Sience in REQUEST headers:
                  set status 304, Not Modified
                  return ''
                return cached value
            - else
                compute result, cache and return it.
        """
        RESPONSE.setHeader('Cache-Control', 'public,max-age=3600')
        kwargs.update(REQUEST.form)
        
        # Get page from cache if exists
        keyset = None
        if self.ZCacheable_isCachingEnabled():
            # Prepare a cache key.
            keyset = kwargs.copy()
            keyset['*'] = ()
            result = self.ZCacheable_get(keywords=keyset, default=_marker)
            if result is not _marker:
                last_mod_req = REQUEST.get_header('If-Modified-Since', None)
                if not last_mod_req:
                    # Return from server cache
                    REQUEST.RESPONSE.setHeader('Last-Modified', rfc1123_date())
                    return result
                # Return from client cache
                RESPONSE.setStatus(304)
                return ''
        
        # Compute result
        result = method(self, REQUEST=REQUEST, RESPONSE=RESPONSE, **kwargs)

        # Update cache
        if keyset is not None:
            self.ZCacheable_set(result, keywords=keyset)
        REQUEST.RESPONSE.setHeader('Last-Modified', rfc1123_date())
        return result
    return wrapper

def content_type_xml(method):
    def wrapper(self, REQUEST, RESPONSE, **kwargs):
        """ Set RESPONSE Content-Type header to text/xml.
        """
        RESPONSE.setHeader('Content-Type', 'text/xml')
        return method(self, REQUEST=REQUEST, RESPONSE=RESPONSE, **kwargs)
    return wrapper
