GOOGLE_KEY = "ABQIAAAAQCK1IGdQs-eHPQQcsyl1VRS9VkEdG8mA4sC2td9bhXvB5ADSOBR2LUE_eY13ZeERnAJGWadztaooDA"
YAHOO_KEY = "YwGAZ8bV34Ed1qyqJwrfxoI7pjyilV8oeXCmYOGDScw3Lg2ixQ81UrWgP69KXQ--"

import urllib
from xml.dom.minidom import parse
from Products.PythonScripts.standard import url_quote
import time

def google_geocode(address):
    google_key = GOOGLE_KEY
    adress = address.replace(" ", "+").encode('utf-8')
    if isinstance(address, unicode):
        address = address.encode('utf-8')
    url = "http://maps.google.com/maps/geo?q=%s&output=csv&key=%s" % (url_quote(adress), google_key)
    u = urllib.urlopen(url)
    buffer = u.read()

    try:
        control_code, acc, latitude, longitude = str(buffer).split(',')
        if (control_code == '200'):
            res = (latitude, longitude)
        else:
            res = None #err
    except:
        res = None #err
    return res

def maps_google_geocode(address):
    time.sleep(3)
    try:
        parms={'q':address}
        url = 'http://maps.google.com/maps?%s' % urllib.urlencode(parms)
        page = urllib.urlopen(url).read()
        if page.find('ll=') > -1:
            a = page[page.find('ll=')+3:]
            b = a[:a.find('&')]
            return tuple(b.split(','))
        else:
            return None
    except:
        return None

def location_geocode(address):
    output = google_geocode(address)
    if output is None:
        output = google_geocode(address)
    return output


def yahoo_geocode(address):
    """ """
    addresses = []
    parms = {'appid': YAHOO_KEY, 'location': address}
    try:
        url = 'http://api.local.yahoo.com/MapsService/V1/geocode?%s' % urllib.urlencode(parms)
        # parse the xml contents of the url into a dom
        dom = parse(urllib.urlopen(url))
        results = dom.getElementsByTagName('Result')
        result_count = len(results)
        for result in results:
            d = {'precision': result.getAttribute('precision'), 'warning': result.getAttribute('warning')}
            for itm in result.childNodes:
                # if precision is zip, Address childNode will not exist
                if itm.childNodes:
                    d[itm.nodeName] = itm.childNodes[0].data
                else:
                    d[itm.nodeName] = ''
            addresses.append(d)
    except:
        return None
    if not addresses: return None
    addr = addresses[0] #take the first one, it should be the good one
    return (addr['Latitude'].encode('utf-8'), addr['Longitude'].encode('utf-8'))

def geocode(portal_map, address):
    if portal_map.current_engine == 'yahoo':
        return yahoo_geocode(address)
    elif portal_map.current_engine == 'google':
        return location_geocode(address)
    else:
        return None
