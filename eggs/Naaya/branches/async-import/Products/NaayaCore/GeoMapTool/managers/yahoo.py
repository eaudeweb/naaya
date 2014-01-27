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
