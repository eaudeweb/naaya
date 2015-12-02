from Products.naayaUpdater.updates import UpdateScript

class UpdateApiKeyGoogleMap(UpdateScript):
    title = ("Remove the API key as it's no longer needed")
    description = ("Remove the API key recorded in the portal_map tool, "
                   "as it's not needed in Google Maps API v3")
    authors = ['Tiberiu Ichim']
    creation_date = 'Feb 26, 2014'

    def _update(self, portal):
        maptool = portal.getGeoMapTool()
        engine = maptool.get_map_engine('google')
        engine.api_keys = ''

        self.log.debug('Set api_keys to nothing for Google engine')
        return True
