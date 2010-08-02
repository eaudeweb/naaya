#Python imports
import urllib
import urllib2
import simplejson

#Zope imports
from zope.interface import Interface, implements

#Naaya imports
from interfaces import IGeocoder

class Geocoder(object):
    implements(IGeocoder)

    GOOGLE_GEOCODING_BASE_URL = 'http://maps.google.com/maps/api/geocode/json'

    def geocode(self, address):
        # build url
        params = [('address', address),
                ('sensor', 'false')]
        url = self.GOOGLE_GEOCODING_BASE_URL + '?' + urllib.urlencode(params)

        # call
        page = urllib2.urlopen(url)

        # unpack the data
        result = simplejson.load(page)
        if result is None:
            raise 'Geocoding service unavailable'
        elif result['status'] != 'OK':
            raise 'Geocoding service error'
        elif len(result['results']) == 0:
            raise 'No geocoding results'
        else:
            fresult = result['results'][0]
            if not fresult.has_key('geometry'):
                raise 'Geocoding result parse error'
            elif not fresult['geometry'].has_key('location'):
                raise 'Geocoding result parse error'
            else:
                lresult = fresult['geometry']['location']
                if not (lresult.has_key('lat') and lresult.has_key('lng')):
                    raise 'Geocoding result parse error'
                else:
                    return lresult['lat'], lresult['lng']

    def reverse_geocode(self, lat, lng):
        # build url
        params = [('latlng', str(lat) + ',' + str(lng)),
                ('sensor', 'false')]
        url = self.GOOGLE_GEOCODING_BASE_URL + '?' + urllib.urlencode(params)

        # call
        page = urllib2.urlopen(url)

        # unpack the data
        result = simplejson.load(page)
        if result is None:
            raise 'Geocoding service unavailable'
        elif result['status'] != 'OK':
            raise 'Geocoding service error'
        elif len(result['results']) == 0:
            raise 'No geocoding results'
        else:
            fresult = result['results'][0]
            if not fresult.has_key('formatted_address'):
                raise 'Geocoding result parse error'
            else:
                return fresult['formatted_address']


