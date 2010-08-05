#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "Atlas"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA). Portions created by Eau de Web are Copyright (C)
#2007 by European Environment Agency. All Rights Reserved.
#
#Contributor(s):
#  Original Code:
#    Alin Voinea (Eau de Web)

import xml.dom.minidom
from urllib import urlencode
from urllib2 import urlopen

class Yahoo:

    BASE_URL = "http://api.local.yahoo.com/MapsService/V1/geocode?%s"
    PRECISION = {
        'empty':    14,
        'country':  12,
        'state':    10,
        'zip':       7,
        'zip+2':     6,
        'zip+4':     4,
        'street':    2,
        'address':   1,
    }

    def __init__(self, app_id, format_string='%s'):
        self.app_id = app_id
        self.format_string = format_string

    def get_base_url(self, string):
        params = {'location': self.format_string % string,
                  'output': 'xml',
                  'appid': self.app_id
                 }
        return self.BASE_URL % urlencode(params)

    def get_zoom_level(self, string, default=15):
        try:
            return self._get_zoom_level(string, default)
        except Exception, err:
            return default

    def _get_zoom_level(self, string, default=15):
        url = self.get_base_url(string)
        page = urlopen(url)

        doc = xml.dom.minidom.parseString(page.read())
        results = doc.getElementsByTagName('Result')

        result = results[0]
        precision = result.getAttribute('precision').lower()

        return self.PRECISION.get(precision, default)
