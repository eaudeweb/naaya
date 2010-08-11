from Products.naayaUpdater.updates import UpdateScript

class AddObjMapZoom(UpdateScript):
    title = 'Add objmap_zoom'
    creation_date = 'Aug 11, 2010'
    authors = ['Andrei Laza']
    description = 'Add objmap_zoom attribute to geomap tool.'

    def _update(self, portal):
        if not hasattr(portal.portal_map, 'objmap_zoom'):
            portal.portal_map.objmap_zoom = 14
            self.log.debug('Added objmap_zoom attribute to geomap tool.')
        return True

