import simplejson as json
import time
import urllib
import urllib2

RETRIES = 3

class GeocoderServiceError(Exception):
    pass


class GeocoderOverQuotaLimit(Exception):
    pass


def _build_url(params):
    GOOGLE_GEOCODE_BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'
    p = []
    for k, v in params:
        if isinstance(v, unicode):
            p.append((k, v.encode('utf-8')))
        else:
            p.append((k, v))

    return GOOGLE_GEOCODE_BASE_URL + '?' + urllib.urlencode(p)


def _get_url_data(url):
    """ Given a url, return a JSON result or raise error

    Code as recommended by:
    https://developers.google.com/maps/documentation/business/articles/usage_limits
    """

    attempts = 0

    while attempts < RETRIES:
        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError, e:
            raise GeocoderServiceError('URLError: %s' % e.reason)

        try:
            result = json.load(response)
            _check_result_is_valid(result)
            return result
        except GeocoderOverQuotaLimit:
            attempts += 1
            time.sleep(2)
            continue

    # this means that the daily limit has been reached
    raise GeocoderServiceError('URLError: Google servers report geocoding '
                               'query limit has been reached')


def _check_result_is_valid(result):
    if result is None:
        raise GeocoderServiceError('Geocoding service unavailable')
    elif not result.has_key('status'):
        raise GeocoderServiceError('Geocoding result parse error')
    elif result['status'] == 'OVER_QUERY_LIMIT':
        raise GeocoderOverQuotaLimit("Geocoding over quota")
    elif result['status'] != 'OK':
        raise GeocoderServiceError('Geocoding status error: %s'
                % result['status'])
    elif not result.has_key('results'):
        raise GeocoderServiceError('Geocoding result parse error')
    elif len(result['results']) == 0:
        raise GeocoderServiceError('No geocoding results')


def _unpack_geocode_data(result):

    fresult = result['results'][0]
    if not fresult.has_key('geometry'):
        raise GeocoderServiceError('Geocoding result parse error')
    elif not fresult['geometry'].has_key('location'):
        raise GeocoderServiceError('Geocoding result parse error')
    else:
        lresult = fresult['geometry']['location']
        if not (lresult.has_key('lat') and lresult.has_key('lng')):
            raise GeocoderServiceError('Geocoding result parse error')
        else:
            ne = fresult['geometry']['viewport']['northeast']
            sw = fresult['geometry']['viewport']['southwest']
            return {
                'location': {
                    'lat': lresult['lat'],
                    'lon': lresult['lng'],
                },
                'boundingbox': {
                    'top': ne['lat'],
                    'bottom': sw['lat'],
                    'left': sw['lng'],
                    'right': ne['lng'],
                },
            }


def _unpack_reverse_geocode_data(result):

    fresult = result['results'][0]

    if not fresult.has_key('formatted_address'):
        raise GeocoderServiceError('Geocoding result parse error')
    if not fresult.has_key('address_components'):
        raise GeocoderServiceError('Geocoding result parse error')
    for comp in fresult['address_components']:
        if not comp.has_key('long_name') or not comp.has_key('types'):
            raise GeocoderServiceError('Geocoding result parse error')

    full_address = fresult['formatted_address']
    countries = [comp['long_name']
                 for comp in fresult['address_components']
                 if 'country' in comp['types']]

    if len(countries) == 0:
        raise GeocoderServiceError('Geocoding result parse error')

    return full_address, countries[0]


def geocode(address):
    """
    Geocode a given address using the Google API. Returns a tuple of
    (lat, lon) float values.

    >>> geocode("Kongens Nytorv 6, 1050 Copenhagen K, Denmark")
    (55.68114360, 12.58664570)
    """
    params = [('address', address), ('sensor', 'false')]
    url = _build_url(params)
    result = _get_url_data(url)
    location = _unpack_geocode_data(result)['location']
    return location['lat'], location['lon']


def geocode2(address):
    """
    Geocode a given address using the Google API. Returns a dictionary
    with "location" and "boundingbox":

    >>> from pprint import pprint
    >>> pprint(geocode("Kongens Nytorv 6, 1050 Copenhagen K, Denmark"))
    {'boundingbox': {'bottom': 55.6797946197085,
                     'left': 12.5852967197085,
                     'right': 12.5879946802915,
                     'top': 55.6824925802915},
     'location': {'lat': 55.6811436, 'lon': 12.5866457}}
    """
    params = [('address', address), ('sensor', 'false')]
    url = _build_url(params)
    result = _get_url_data(url)
    return _unpack_geocode_data(result)


def reverse_geocode(lat, lng):
    """ Given a geo coordinate, returns the human readable name of address
    """
    params = [('latlng', str(lat) + ',' + str(lng)), ('sensor', 'false')]
    url = _build_url(params)
    result = _get_url_data(url)
    return _unpack_reverse_geocode_data(result)
