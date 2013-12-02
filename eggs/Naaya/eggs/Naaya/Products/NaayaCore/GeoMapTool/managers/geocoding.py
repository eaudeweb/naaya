""" Backwards compatibility module
"""

from naaya.core import ggeocoding


def location_geocode(address):
    """ Returns a tuple of geo coordinates for the address
    """
    address = ggeocoding.geocode(address)

    # Sometimes google doesn't return proper address on first request
    if address == None:
        address = ggeocoding.geocode(address)

    lat, lon = address
    return (str(lat), str(lon))


def geocode(portal_map, address):
    """ Returns a tuple of geo coordinates for the address
    """

    return location_geocode(address)
