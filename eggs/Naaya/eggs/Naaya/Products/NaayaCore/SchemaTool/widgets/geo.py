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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

from decimal import Decimal as D

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
