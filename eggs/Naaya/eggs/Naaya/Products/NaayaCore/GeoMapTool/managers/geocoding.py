""" Backwards compatibility module
"""

from naaya.core import ggeocoding

def location_geocode(address):
    return ggeocoding.geocode(address)

def geocode(portal_map, address):
    address = location_geocode(address)

    # Sometimes google doesn't return proper address on first request
    if address == None:
        address = location_geocode(address)

    lat, lon = address

    return (str(lat), str(lon))
