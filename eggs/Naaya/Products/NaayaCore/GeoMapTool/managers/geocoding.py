""" Backwards compatibility module
"""

from naaya.core import ggeocoding


def location_geocode(address):
    """ Returns a tuple of geo coordinates for the address
    """
    lat, lon = ggeocoding.geocode(address)
    return (str(lat), str(lon))


def geocode(portal_map, address):
    """ Returns a tuple of geo coordinates for the address
    """

    return location_geocode(address)
