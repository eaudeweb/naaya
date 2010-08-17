from random import randint

from OFS.SimpleItem import SimpleItem
from persistent.list import PersistentList

def addPushPin(parent, catalog, latitude, longitude):
    if not hasattr(parent, 'last_pin_index'):
        parent.last_pin_index = -1
    index = parent.last_pin_index + 1

    id = 'pin_%d' % index
    pin = PushPin(id, latitude, longitude)
    parent.last_pin_index += 1

    parent._setOb(id, pin)
    catalog.catalog_object(pin, uid=id)

    return index


def resetPushPinRating(parent, catalog, index):
    id = 'pin_%d' % index
    pin_idx = catalog._catalog.indexes['id_pin']._index
    f = {'id_pin': id}

    # getting the unique data record ids
    brains = catalog(f)
    dict_rids = {}
    rids = []
    for b in brains:
        rid = b.data_record_id_
        if rid not in dict_rids:
            dict_rids[rid] = 1
            rids.append(rid)

    ratings = [catalog.getobject(rid) for rid in rids]
    for r in ratings:
        assert r.id_pin == id
    sum_ratings = sum(r.rating for r in ratings)
    pin = parent._getOb(id)
    pin.averageRating = sum_ratings / len(ratings)

    # recatalog pin
    catalog.uncatalog_object(id)
    catalog.catalog_object(pin, uid=id)

def removePushPin(parent, catalog, index):
    id = 'pin_%d' % index
    pin = parent._getOb(id)
    catalog.uncatalog_object(id)
    parent._delOb(id)

class PushPin(SimpleItem):
    def __init__(self, id, latitude, longitude):
        self._setId(id)
        self.latitude = latitude
        self.longitude = longitude
        self.averageRating = None


def ratePushPin(parent, catalog, pin_index, type, rating):
    if not hasattr(parent, 'last_rating_index'):
        parent.last_rating_index = -1
    index = parent.last_rating_index + 1

    id = 'rating_%d' % index
    id_pin = 'pin_%d' % pin_index
    rating = PinRate(id, id_pin, type, rating)
    parent.last_rating_index += 1

    parent._setOb(id, rating)
    catalog.catalog_object(rating, uid=id)
    resetPushPinRating(parent, catalog, pin_index)

    return index

def removeRating(parent, catalog, index):
    id = 'rating_%d' % index
    catalog.uncatalog_object(id)
    parent._delOb(id)

class PinRate(SimpleItem):
    def __init__(self, id, id_pin, type, rating):
        self._setId(id)
        self.id_pin = id_pin
        self.type = type
        self.rating = rating

