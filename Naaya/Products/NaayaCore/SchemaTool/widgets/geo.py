from decimal import Decimal as D
import simplejson as json

class Geo(tuple):
    """ Immutable type representing individual geographical points """

    def __new__(cls, lat=None, lon=None, address=''):
        if lat is lon is None:
            pass
        elif None in (lat, lon):
            raise ValueError('latitude and longitude must both have values or be blank')
        else:
            def normalize_coord(value, name):
                try: return D(value)
                except: raise ValueError('Bad value %s for %s' % (repr(value), name))
            lat = normalize_coord(lat, 'latitude')
            lon = normalize_coord(lon, 'longitude')

        try:
            address = address.decode('utf-8')
        except UnicodeEncodeError:
            pass

        try:
            address = unicode(address)
        except:
            raise ValueError('Bad value for address')

        return tuple.__new__(cls, (lat, lon, address))

    @property
    def missing_lat_lon(self):
        return (None in (self.lat, self.lon))

    @property
    def lat(self):
        return self[0]

    @property
    def lon(self):
        return self[1]

    @property
    def address(self):
        return self[2]

    def __repr__(self):
        data = {
            'lat': str(self.lat),
            'lon': str(self.lon),
            'address': repr(self.address),
        }
        if self.address:
            return "Geo(lat=%(lat)s, lon=%(lon)s, address=%(address)s)" % data
        else:
            return "Geo(lat=%(lat)s, lon=%(lon)s)" % data

    def is_in_rectangle(self, lat_min, lat_max, lon_min, lon_max):
        return D(str(lat_max)) > self.lat > D(str(lat_min)) and\
                D(str(lon_max)) > self.lon > D(str(lon_min))

def json_encode_helper(value):
    if isinstance(value, D):
        return str(value)
    else:
        raise ValueError('Can not encode value %r' % value)

def geo_as_json(value):
    if value is None:
        return json.dumps(None)
    assert isinstance(value, Geo)
    if value.missing_lat_lon:
        return json.dumps(None)
    else:
        return json.dumps({'lat': value.lat, 'lon': value.lon},
                          default=json_encode_helper)
