from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Globals import InitializeClass
from Products.ZCatalog.ZCatalog import manage_addZCatalog
from Products.PluginIndexes.FieldIndex.FieldIndex import manage_addFieldIndex
from Products.PluginIndexes.DateIndex.DateIndex import manage_addDateIndex
from OFS.SimpleItem import SimpleItem

def manage_addNyObservatory(parent, REQUEST=None):
    """ """
    id='observatory'
    ob = NyObservatory(id)
    ob.title = 'Naaya Observatory'

    manage_addZCatalog(ob, 'catalog', 'Naaya Observatory Catalog')
    manage_addFieldIndex(ob.catalog, 'type')
    manage_addFieldIndex(ob.catalog, 'latitude')
    manage_addFieldIndex(ob.catalog, 'longitude')
    manage_addFieldIndex(ob.catalog, 'rating')
    manage_addFieldIndex(ob.catalog, 'approved_comment')
    manage_addDateIndex(ob.catalog, 'date')
    manage_addFieldIndex(ob.catalog, 'country')
    manage_addFieldIndex(ob.catalog, 'author')
    manage_addFieldIndex(ob.catalog, 'session_key')

    parent._setObject(id, ob)
    if REQUEST:
        return parent.manage_main(parent, REQUEST, update_menu=1)

class NyObservatory(BTreeFolder2):
    meta_type = 'Naaya Observatory'

    def __init__(self, id=None):
        BTreeFolder2.__init__(self, id)
        self._last_pin_index = -1

    def _generate_pin_id(self):
        self._last_pin_index += 1
        return 'pin_%d' % self._last_pin_index

    def add_pin(self, *args, **kwargs):
        id = self._generate_pin_id()
        pin = NyPushPin(id, *args, **kwargs)
        self._setOb(id, pin)
        self.catalog.catalog_object(pin, uid=id)
        return id

    def remove_pin(self, id):
        pin = self._getOb(id)
        self.catalog.uncatalog_object(id)
        self._delOb(id)

    def recatalog_pin(self, id):
        pin = self._getOb(id)
        self.catalog.uncatalog_object(id)
        self.catalog.catalog_object(pin, uid=id)

    def approve_pin_comment(self, id, approved):
        pin = self._getOb(id)
        pin.approved_comment = approved
        self.recatalog_pin(id)

    def get_pin(self, id):
        return self._getOb(id)

    def index_html(self, REQUEST):
        """ """
        return REQUEST.RESPONSE.redirect('%s/map' % self.absolute_url())

InitializeClass(NyObservatory)

RATING_VALUES = range(1, 5+1)
TYPE_VALUES = ['veg', 'wat', 'soil', 'cit']

class NyPushPin(SimpleItem):
    def __init__(self, id, type, latitude, longitude, address, country,
            rating, comment, date, author, session_key):
        assert type in TYPE_VALUES
        assert -90 < latitude < 90
        assert -180 < longitude < 180
        assert rating in RATING_VALUES
        if author == 'Anonymous User':
            assert session_key is not None
        if type == 'cit':
            assert comment != ''

        self._setId(id)
        self.type = type
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.country = country
        self.rating = rating
        self.comment = comment
        self.approved_comment = False
        self.date = date
        self.author = author
        self.session_key = session_key

InitializeClass(NyPushPin)


