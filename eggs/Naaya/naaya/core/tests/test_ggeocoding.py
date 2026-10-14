import io
import json
import unittest
import urllib.error
import urllib.parse
from unittest import mock

from naaya.core import ggeocoding
from Products.NaayaCore.GeoMapTool.managers import geocoding

GEOCODE_RESULT = {
    'status': 'OK',
    'results': [{
        'formatted_address': 'Kongens Nytorv 6, 1050 København, Denmark',
        'address_components': [
            {'long_name': 'København', 'types': ['locality']},
            {'long_name': 'Denmark', 'types': ['country', 'political']},
        ],
        'geometry': {
            'location': {'lat': 55.6811436, 'lng': 12.5866457},
            'viewport': {
                'northeast': {'lat': 55.6824925, 'lng': 12.5879946},
                'southwest': {'lat': 55.6797946, 'lng': 12.5852967},
            },
        },
    }],
}


def json_response(data):
    return io.BytesIO(json.dumps(data).encode('utf-8'))


class GeocodingTest(unittest.TestCase):

    def setUp(self):
        self.urls = []
        self.responses = []
        # patch the module ggeocoding uses, sys.modules may hold another one
        patcher = mock.patch.object(ggeocoding.urllib.request, 'urlopen',
                                    self.urlopen)
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch.object(ggeocoding.time, 'sleep')
        self.sleep = patcher.start()
        self.addCleanup(patcher.stop)

    def urlopen(self, url):
        self.urls.append(url)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return json_response(response)

    def query(self, n=0):
        url = self.urls[n]
        base, query = url.split('?', 1)
        self.assertEqual(base,
                         'https://maps.googleapis.com/maps/api/geocode/json')
        return urllib.parse.parse_qsl(query)

    def test_build_url(self):
        url = ggeocoding._build_url([('address', 'București 1&2'),
                                     ('sensor', 'false')])
        self.assertEqual(url, 'https://maps.googleapis.com/maps/api/geocode/'
                              'json?address=Bucure%C8%99ti+1%262&sensor=false')

    def test_geocode(self):
        self.responses.append(GEOCODE_RESULT)
        self.assertEqual(ggeocoding.geocode('Kongens Nytorv 6', 'secret'),
                         (55.6811436, 12.5866457))
        self.assertEqual(self.query(), [('address', 'Kongens Nytorv 6'),
                                        ('sensor', 'false'),
                                        ('key', 'secret')])

    def test_geocode_without_key(self):
        self.responses.append(GEOCODE_RESULT)
        ggeocoding.geocode('Kongens Nytorv 6')
        self.assertEqual(self.query(), [('address', 'Kongens Nytorv 6'),
                                        ('sensor', 'false')])

    def test_geocode2(self):
        self.responses.append(GEOCODE_RESULT)
        self.assertEqual(ggeocoding.geocode2('Kongens Nytorv 6'), {
            'location': {'lat': 55.6811436, 'lon': 12.5866457},
            'boundingbox': {'top': 55.6824925, 'bottom': 55.6797946,
                            'left': 12.5852967, 'right': 12.5879946},
        })

    def test_reverse_geocode(self):
        self.responses.append(GEOCODE_RESULT)
        self.assertEqual(ggeocoding.reverse_geocode(55.68, 12.58), (
            'Kongens Nytorv 6, 1050 København, Denmark', 'Denmark'))
        self.assertEqual(self.query(), [('latlng', '55.68,12.58'),
                                        ('sensor', 'false')])

    def test_reverse_geocode_without_country(self):
        result = json.loads(json.dumps(GEOCODE_RESULT))
        del result['results'][0]['address_components'][1]
        self.responses.append(result)
        with self.assertRaises(ggeocoding.GeocoderServiceError):
            ggeocoding.reverse_geocode(55.68, 12.58)

    def test_over_quota_retries(self):
        self.responses.extend([{'status': 'OVER_QUERY_LIMIT'},
                               GEOCODE_RESULT])
        self.assertEqual(ggeocoding.geocode('x'), (55.6811436, 12.5866457))
        self.assertEqual(len(self.urls), 2)
        self.sleep.assert_called_once_with(2)

    def test_over_quota_gives_up(self):
        self.responses.extend([{'status': 'OVER_QUERY_LIMIT'}] *
                              ggeocoding.RETRIES)
        with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
            ggeocoding.geocode('x')
        self.assertIn('query limit has been reached', str(cm.exception))
        self.assertEqual(len(self.urls), ggeocoding.RETRIES)

    def test_url_error(self):
        self.responses.append(urllib.error.URLError('no route'))
        with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
            ggeocoding.geocode('x')
        self.assertEqual(str(cm.exception), 'URLError: no route')

    def test_http_error(self):
        self.responses.append(urllib.error.HTTPError(
            'http://x', 500, 'Server Error', {}, io.BytesIO(b'oops')))
        with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
            ggeocoding.geocode('x')
        self.assertEqual(str(cm.exception), 'URLError: Server Error')

    def test_check_result(self):
        check = ggeocoding._check_result_is_valid
        error = ggeocoding.GeocoderServiceError
        cases = [(None, 'Geocoding service unavailable'),
                 ({}, 'Geocoding result parse error'),
                 ({'status': 'ZERO_RESULTS'},
                  'Geocoding status error: ZERO_RESULTS'),
                 ({'status': 'OK'}, 'Geocoding result parse error'),
                 ({'status': 'OK', 'results': []}, 'No geocoding results')]
        for result, message in cases:
            with self.assertRaises(error) as cm:
                check(result)
            self.assertEqual(str(cm.exception), message)
        self.assertRaises(ggeocoding.GeocoderOverQuotaLimit, check,
                          {'status': 'OVER_QUERY_LIMIT'})
        self.assertIsNone(check(GEOCODE_RESULT))

    def test_unpack_bad_geometry(self):
        for geometry in [None, {}, {'location': {'lat': 1}}]:
            fresult = {} if geometry is None else {'geometry': geometry}
            with self.assertRaises(ggeocoding.GeocoderServiceError):
                ggeocoding._unpack_geocode_data({'results': [fresult]})

    def test_location_geocode(self):
        self.responses.append(GEOCODE_RESULT)
        with mock.patch.object(geocoding, 'get_zope_env',
                               return_value='secret'):
            self.assertEqual(geocoding.geocode(None, 'Kongens Nytorv 6'),
                             ('55.6811436', '12.5866457'))
        self.assertIn(('key', 'secret'), self.query())
