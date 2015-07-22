from Products.NaayaCore.GeoMapTool import engine_google
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


class UpdateGoogleMapsAPIKey(UpdateScript):
    """ Updates google maps api key with the one present in sources """
    title = 'Update Google Maps API Key'
    creation_date = 'Oct 24, 2012'
    authors = ['Mihnea Simian']
    description = 'Updates Google Maps API Key with the one present in sources'

    def _update(self, portal):
        # no longer support API keys

        raise NotImplementedError

        geomap = portal.getGeoMapTool()
        latest_key = engine_google.DEFAULT_API_KEY
        for engine in geomap.objectValues():
            if isinstance(engine, engine_google.GoogleMapEngine):
                self.log.debug("Found Google Maps engine")
                if engine.api_keys != latest_key:
                    self.log.debug("Updating key from %s to %s",
                                   engine.api_keys, latest_key)
                    engine.api_keys = latest_key
                else:
                    self.log.debug("Key already newest, skipping")
        return True
