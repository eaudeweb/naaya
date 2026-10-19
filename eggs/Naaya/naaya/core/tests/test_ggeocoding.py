import io
import json
import os
import unittest
import urllib.error
import urllib.parse
from unittest import mock

from naaya.core import ggeocoding
from Products.NaayaCore.GeoMapTool.managers import geocoding
from Products.NaayaCore.managers import async_geolocator

SEARCH_RESULT = [{
    'lat': '55.6811436',
    'lon': '12.5866457',
    'boundingbox': ['55.6797946', '55.6824925', '12.5852967', '12.5879946'],
    'display_name': 'Kongens Nytorv 6, København, Denmark',
}]

REVERSE_RESULT = {
    'lat': '55.68',
    'lon': '12.58',
    'display_name': 'Kongens Nytorv 6, 1050 København, Denmark',
    'address': {'city': 'København', 'country': 'Denmark',
                'country_code': 'dk'},
}


GOOGLE_RESULT = {'status': 'OK', 'results': [{
    'formatted_address': 'Kongens Nytorv 6, 1050 København, Denmark',
    'address_components': [{'long_name': 'Denmark', 'types': ['country']}],
    'geometry': {'location': {'lat': 55.6811436, 'lng': 12.5866457},
                 'viewport': {'northeast': {'lat': 55.68, 'lng': 12.59},
                              'southwest': {'lat': 55.67, 'lng': 12.58}}},
}]}
GOOGLE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'


def http_error(code, reason):
    return urllib.error.HTTPError('http://x', code, reason, {},
                                  io.BytesIO(b''))


class GeocodingTest(unittest.TestCase):

    def setUp(self):
        self.requests = []
        self.responses = []
        # patch the module ggeocoding uses, sys.modules may hold another one
        patcher = mock.patch.object(ggeocoding.urllib.request, 'urlopen',
                                    self.urlopen)
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch.object(ggeocoding.time, 'sleep')
        self.sleep = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in ('GEOCODING_URL', 'GEOCODING_KEY', 'GEOCODING_CONTACT',
                     'GEOCODING_PROVIDER', 'GOOGLE_GEOLOCATION_API_KEY'):
            os.environ.pop(name, None)
        ggeocoding.clear_cache()
        self.addCleanup(ggeocoding.clear_cache)
        ggeocoding._last_request = 0.0

    def urlopen(self, request, timeout=None):
        self.requests.append(request)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return io.BytesIO(json.dumps(response).encode('utf-8'))

    def query(self, n=0, base='https://nominatim.openstreetmap.org/search'):
        url = self.requests[n].full_url
        url_base, query = url.split('?', 1)
        self.assertEqual(url_base, base)
        return urllib.parse.parse_qsl(query)

    def test_geocode(self):
        self.responses.append(SEARCH_RESULT)
        self.assertEqual(ggeocoding.geocode('Kongens Nytorv 6'),
                         (55.6811436, 12.5866457))
        self.assertEqual(self.query(), [('format', 'jsonv2'),
                                        ('q', 'Kongens Nytorv 6'),
                                        ('limit', '1')])
        request = self.requests[0]
        self.assertEqual(request.get_header('User-agent'),
                         'naaya geocoding; helpdesk@eaudeweb.ro')
        self.assertEqual(request.get_header('Accept-language'), 'en')

    def test_geocode_with_key(self):
        self.responses.append(SEARCH_RESULT)
        ggeocoding.geocode('Kongens Nytorv 6', 'secret')
        self.assertIn(('key', 'secret'), self.query())

    def test_settings_from_environment(self):
        os.environ.update({'GEOCODING_URL': 'https://eu1.locationiq.com/v1/',
                           'GEOCODING_KEY': 'envkey',
                           'GEOCODING_CONTACT': 'site; admin@example.com'})
        self.responses.append(SEARCH_RESULT)
        ggeocoding.geocode('Kongens Nytorv 6')
        query = self.query(base='https://eu1.locationiq.com/v1/search')
        self.assertIn(('key', 'envkey'), query)
        self.assertEqual(self.requests[0].get_header('User-agent'),
                         'site; admin@example.com')

    def use_google(self):
        os.environ.update({'GEOCODING_PROVIDER': 'google',
                           'GOOGLE_GEOLOCATION_API_KEY': 'gkey'})

    def test_google_geocode2(self):
        self.use_google()
        self.responses.append(GOOGLE_RESULT)
        self.assertEqual(ggeocoding.geocode2('Kongens Nytorv 6'), {
            'location': {'lat': 55.6811436, 'lon': 12.5866457},
            'boundingbox': {'top': 55.68, 'bottom': 55.67,
                            'left': 12.58, 'right': 12.59},
        })
        self.assertEqual(self.query(base=GOOGLE_URL), [
            ('address', 'Kongens Nytorv 6'), ('key', 'gkey')])

    def test_google_reverse_geocode(self):
        self.use_google()
        self.responses.append(GOOGLE_RESULT)
        self.assertEqual(ggeocoding.reverse_geocode(55.68, 12.58), (
            'Kongens Nytorv 6, 1050 København, Denmark', 'Denmark'))
        self.assertEqual(self.query(base=GOOGLE_URL), [
            ('latlng', '55.68,12.58'), ('key', 'gkey')])

    def test_google_errors(self):
        self.use_google()
        self.responses.append({'status': 'OVER_QUERY_LIMIT', 'results': []})
        with self.assertRaises(ggeocoding.GeocoderOverQuotaLimit):
            ggeocoding.geocode('a')
        self.responses.append({'status': 'ZERO_RESULTS', 'results': []})
        with self.assertRaisesRegex(ggeocoding.GeocoderServiceError,
                                    'ZERO_RESULTS'):
            ggeocoding.geocode('b')
        self.assertFalse(self.sleep.called)

    def test_geocode2(self):
        self.responses.append(SEARCH_RESULT)
        self.assertEqual(ggeocoding.geocode2('Kongens Nytorv 6'), {
            'location': {'lat': 55.6811436, 'lon': 12.5866457},
            'boundingbox': {'top': 55.6824925, 'bottom': 55.6797946,
                            'left': 12.5852967, 'right': 12.5879946},
        })

    def test_reverse_geocode(self):
        self.responses.append(REVERSE_RESULT)
        self.assertEqual(ggeocoding.reverse_geocode(55.68, 12.58), (
            'Kongens Nytorv 6, 1050 København, Denmark', 'Denmark'))
        base = 'https://nominatim.openstreetmap.org/reverse'
        self.assertEqual(self.query(base=base), [
            ('format', 'jsonv2'), ('lat', '55.68'), ('lon', '12.58')])

    def test_reverse_geocode_without_country(self):
        result = json.loads(json.dumps(REVERSE_RESULT))
        del result['address']['country']
        self.responses.append(result)
        with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
            ggeocoding.reverse_geocode(55.68, 12.58)
        self.assertEqual(str(cm.exception), 'Geocoding result parse error')

    def test_reverse_geocode_not_found(self):
        self.responses.append({'error': 'Unable to geocode'})
        with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
            ggeocoding.reverse_geocode(0, 0)
        self.assertIn('ZERO_RESULTS', str(cm.exception))

    def test_no_results(self):
        self.responses.append([])
        with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
            ggeocoding.geocode('nowhere')
        self.assertIn('ZERO_RESULTS', str(cm.exception))

    def test_not_found_404(self):
        self.responses.append(http_error(404, 'Not Found'))
        with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
            ggeocoding.geocode('nowhere')
        self.assertIn('ZERO_RESULTS', str(cm.exception))

    def test_cache(self):
        self.responses.append(SEARCH_RESULT)
        first = ggeocoding.geocode('Kongens  Nytorv 6')
        self.assertEqual(ggeocoding.geocode(' kongens nytorv\t6 '), first)
        self.assertEqual(len(self.requests), 1)

    def test_cache_not_found(self):
        self.responses.append([])
        for i in range(2):
            with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
                ggeocoding.geocode('Nowhere')
            self.assertIn('ZERO_RESULTS', str(cm.exception))
        self.assertEqual(len(self.requests), 1)

    def test_errors_not_cached(self):
        self.responses.extend([http_error(500, 'Server Error'),
                               SEARCH_RESULT])
        with self.assertRaises(ggeocoding.GeocoderServiceError):
            ggeocoding.geocode('x')
        self.assertEqual(ggeocoding.geocode('x'), (55.6811436, 12.5866457))

    def test_cache_size(self):
        with mock.patch.object(ggeocoding, 'CACHE_SIZE', 2):
            self.responses.extend([SEARCH_RESULT] * 4)
            for address in ('a', 'b', 'c', 'a'):
                ggeocoding.geocode(address)
        self.assertEqual(len(self.requests), 4)
        self.assertEqual(list(ggeocoding._cache), ['c', 'a'])

    def test_geocode2_returns_copy(self):
        self.responses.append(SEARCH_RESULT)
        ggeocoding.geocode2('x')['location']['lat'] = 0
        self.assertEqual(ggeocoding.geocode('x'), (55.6811436, 12.5866457))

    def test_rate_limit_between_requests(self):
        self.responses.extend([SEARCH_RESULT, SEARCH_RESULT])
        with mock.patch.object(ggeocoding.time, 'monotonic',
                               side_effect=[100.0, 100.0, 100.25, 101.0]):
            ggeocoding.geocode('a')
            ggeocoding.geocode('b')
        self.sleep.assert_called_once_with(0.75)

    def test_over_quota(self):
        for code in (429, 403):
            self.responses.append(http_error(code, 'Too Many Requests'))
            with self.assertRaises(ggeocoding.GeocoderOverQuotaLimit) as cm:
                ggeocoding.geocode('x')
            self.assertIn('quota', str(cm.exception))
            self.assertIsInstance(cm.exception,
                                  ggeocoding.GeocoderServiceError)

    def test_url_error(self):
        self.responses.append(urllib.error.URLError('no route'))
        with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
            ggeocoding.geocode('x')
        self.assertEqual(str(cm.exception), 'URLError: no route')

    def test_http_error(self):
        self.responses.append(http_error(500, 'Server Error'))
        with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
            ggeocoding.geocode('x')
        self.assertEqual(str(cm.exception), 'URLError: Server Error')

    def test_timeout(self):
        self.responses.append(TimeoutError('timed out'))
        with self.assertRaises(ggeocoding.GeocoderServiceError):
            ggeocoding.geocode('x')

    def test_unpack_bad_results(self):
        for result in [None, {}, [{}], [{'lat': '1', 'lon': '2'}],
                       [{'lat': 'x', 'lon': '2',
                         'boundingbox': ['1', '2', '3', '4']}]]:
            with self.assertRaises(ggeocoding.GeocoderServiceError) as cm:
                ggeocoding._unpack_geocode_data(result)
            self.assertEqual(str(cm.exception),
                             'Geocoding result parse error')

    def test_location_geocode(self):
        self.responses.append(SEARCH_RESULT)
        self.assertEqual(geocoding.geocode(None, 'Kongens Nytorv 6'),
                         ('55.6811436', '12.5866457'))


class GeolocateQueueTest(unittest.TestCase):

    def setUp(self):
        for name in ('transaction', 'time', 'Geo'):
            patcher = mock.patch.object(async_geolocator, name)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.obj = mock.Mock()
        self.obj.geo_location.lat = self.obj.geo_location.lon = None
        self.obj.geo_location.address = 'Kongens Nytorv 6'
        self.site = mock.Mock(geolocation_queue=['a', 'b'],
                              previous_geolocation=None)
        self.site.unrestrictedTraverse.return_value = self.obj

    def run_queue(self, error):
        with mock.patch.object(geocoding, 'location_geocode',
                               side_effect=error):
            async_geolocator.geolocate_queue(self.site)

    def test_over_quota_stops(self):
        self.run_queue(ggeocoding.GeocoderOverQuotaLimit(
            'Geocoding over quota: HTTP 429'))
        self.assertEqual(self.site.geolocation_queue, ['a', 'b'])
        self.assertIsNotNone(self.site.previous_geolocation)

    def test_no_results_removed(self):
        self.run_queue(ggeocoding.GeocoderServiceError(ggeocoding.NO_RESULTS))
        self.assertEqual(self.site.geolocation_queue, [])
        self.assertIsNone(self.site.previous_geolocation)

    def test_found(self):
        self.run_queue([('55.68', '12.58'), ('1', '2')])
        self.assertEqual(self.site.geolocation_queue, [])
        async_geolocator.time.sleep.assert_called_with(2)
