""" Backwards compatibility module
"""

from naaya.core import ggeocoding
from naaya.core.zope2util import get_zope_env


def location_geocode(address):
    """ Returns a tuple of geo coordinates for the address
    """
    key = get_zope_env('GOOGLE_GEOLOCATION_API_KEY')
    address = ggeocoding.geocode(address, key)

    # Sometimes google doesn't return proper address on first request
    if address is None:
        address = ggeocoding.geocode(address, key)

    lat, lon = address
    return (str(lat), str(lon))


def geocode(portal_map, address):
    """ Returns a tuple of geo coordinates for the address
    """

    return location_geocode(address)
