"""Geocoding with the Nominatim API (OpenStreetMap), a compatible provider or Google.

Settings (environment): GEOCODING_PROVIDER (nominatim or google), GEOCODING_URL,
GEOCODING_KEY, GEOCODING_CONTACT; GOOGLE_GEOLOCATION_API_KEY for google.
"""
import collections
import copy
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_URL = 'https://nominatim.openstreetmap.org'
GOOGLE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
DEFAULT_CONTACT = 'naaya geocoding; helpdesk@eaudeweb.ro'
MIN_INTERVAL = 1.0  # seconds between requests (Nominatim usage policy)
TIMEOUT = 10
CACHE_SIZE = 1000
NO_RESULTS = 'Geocoding status error: ZERO_RESULTS'

_lock = threading.Lock()
_last_request = 0.0
_cache = collections.OrderedDict()
_cache_lock = threading.Lock()
_NOT_FOUND = object()


class GeocoderServiceError(Exception):
    pass


class GeocoderOverQuotaLimit(GeocoderServiceError):
    """HTTP 429/403 from the provider; the message contains 'quota'."""


def _settings():
    url = os.environ.get('GEOCODING_URL') or DEFAULT_URL
    contact = os.environ.get('GEOCODING_CONTACT') or DEFAULT_CONTACT
    return url.rstrip('/'), os.environ.get('GEOCODING_KEY', ''), contact


def _use_google():
    return (os.environ.get('GEOCODING_PROVIDER') or '').lower() == 'google'


def _google_url(params, key=None):
    params = list(params)
    key = key or os.environ.get('GOOGLE_GEOLOCATION_API_KEY', '')
    if key:
        params.append(('key', key))
    return GOOGLE_URL + '?' + urllib.parse.urlencode(params)


def _build_url(path, params, key=None):
    base, env_key = _settings()[:2]
    params = list(params)
    key = key or env_key
    if key:
        params.append(('key', key))
    return base + path + '?' + urllib.parse.urlencode(params)


def _wait_turn():
    global _last_request
    wait = _last_request + MIN_INTERVAL - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()


def _get_url_data(url, throttle=True):
    """Return the decoded JSON response for url or raise GeocoderServiceError."""
    contact = _settings()[2]
    request = urllib.request.Request(url, headers={
        'User-Agent': contact, 'Accept-Language': 'en'})
    with _lock:
        if throttle:
            _wait_turn()
        try:
            response = urllib.request.urlopen(request, timeout=TIMEOUT)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                raise GeocoderOverQuotaLimit(
                    'Geocoding over quota: HTTP %s' % e.code)
            if e.code == 404:  # LocationIQ answers 404 for no results
                raise GeocoderServiceError(NO_RESULTS)
            raise GeocoderServiceError('URLError: %s' % e.reason)
        except urllib.error.URLError as e:
            raise GeocoderServiceError('URLError: %s' % e.reason)
        except OSError as e:
            raise GeocoderServiceError('URLError: %s' % e)
    try:
        with response:
            return json.load(response)
    except ValueError:
        raise GeocoderServiceError('Geocoding result parse error')


def _normalize(address):
    return ' '.join(str(address).lower().split())


def _cache_get(address):
    with _cache_lock:
        value = _cache.get(address)
        if value is not None:
            _cache.move_to_end(address)
        return value


def _cache_set(address, value):
    with _cache_lock:
        _cache[address] = value
        _cache.move_to_end(address)
        while len(_cache) > CACHE_SIZE:
            _cache.popitem(last=False)


def clear_cache():
    with _cache_lock:
        _cache.clear()


def _unpack_geocode_data(result):
    """Convert a Nominatim search result list to location and boundingbox."""
    if not isinstance(result, list):
        raise GeocoderServiceError('Geocoding result parse error')
    if not result:
        raise GeocoderServiceError(NO_RESULTS)
    first = result[0]
    try:
        bottom, top, left, right = [float(v) for v in first['boundingbox']]
        return {
            'location': {'lat': float(first['lat']),
                         'lon': float(first['lon'])},
            'boundingbox': {'top': top, 'bottom': bottom,
                            'left': left, 'right': right},
        }
    except (KeyError, TypeError, ValueError):
        raise GeocoderServiceError('Geocoding result parse error')


def _unpack_reverse_geocode_data(result):
    """Return (full address, country) from a Nominatim reverse result."""
    if not isinstance(result, dict):
        raise GeocoderServiceError('Geocoding result parse error')
    if 'error' in result:
        raise GeocoderServiceError(NO_RESULTS)
    country = (result.get('address') or {}).get('country')
    if not result.get('display_name') or not country:
        raise GeocoderServiceError('Geocoding result parse error')
    return result['display_name'], country


def _google_result(data):
    """First result of a Google Geocoding API response."""
    status = data.get('status') if isinstance(data, dict) else None
    if status == 'OVER_QUERY_LIMIT':
        raise GeocoderOverQuotaLimit('Geocoding over quota')
    if status == 'ZERO_RESULTS':
        raise GeocoderServiceError(NO_RESULTS)
    if status != 'OK' or not data.get('results'):
        raise GeocoderServiceError('Geocoding status error: %s' % status)
    return data['results'][0]


def _unpack_google_geocode_data(data):
    result = _google_result(data)
    try:
        location = result['geometry']['location']
        ne = result['geometry']['viewport']['northeast']
        sw = result['geometry']['viewport']['southwest']
        return {
            'location': {'lat': float(location['lat']),
                         'lon': float(location['lng'])},
            'boundingbox': {'top': float(ne['lat']), 'bottom': float(sw['lat']),
                            'left': float(sw['lng']), 'right': float(ne['lng'])},
        }
    except (KeyError, TypeError, ValueError):
        raise GeocoderServiceError('Geocoding result parse error')


def _unpack_google_reverse_data(data):
    result = _google_result(data)
    countries = [c.get('long_name') for c in result.get('address_components', [])
                 if 'country' in c.get('types', [])]
    if not result.get('formatted_address') or not countries:
        raise GeocoderServiceError('Geocoding result parse error')
    return result['formatted_address'], countries[0]


def _fetch_search(address, key=None):
    if _use_google():
        url = _google_url([('address', address)], key)
        return _unpack_google_geocode_data(_get_url_data(url, throttle=False))
    url = _build_url('/search', [('format', 'jsonv2'), ('q', address),
                                 ('limit', '1')], key)
    return _unpack_geocode_data(_get_url_data(url))


def _search(address, key=None):
    normalized = _normalize(address)
    cached = _cache_get(normalized)
    if cached is _NOT_FOUND:
        raise GeocoderServiceError(NO_RESULTS)
    if cached is not None:
        return cached
    try:
        data = _fetch_search(address, key)
    except GeocoderServiceError as e:
        if str(e) == NO_RESULTS:
            _cache_set(normalized, _NOT_FOUND)
        raise
    _cache_set(normalized, data)
    return data


def geocode(address, key=None):
    """Return (lat, lon) floats for the address."""
    location = _search(address, key)['location']
    return location['lat'], location['lon']


def geocode2(address):
    """Return a dict with "location" (lat, lon) and "boundingbox" (top, bottom, left, right)."""
    return copy.deepcopy(_search(address))


def reverse_geocode(lat, lng):
    """Return (full address, country) for the coordinates."""
    if _use_google():
        url = _google_url([('latlng', '%s,%s' % (lat, lng))])
        return _unpack_google_reverse_data(_get_url_data(url, throttle=False))
    url = _build_url('/reverse', [('format', 'jsonv2'), ('lat', str(lat)),
                                  ('lon', str(lng))])
    return _unpack_reverse_geocode_data(_get_url_data(url))
