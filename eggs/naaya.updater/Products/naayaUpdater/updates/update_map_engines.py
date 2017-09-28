from AccessControl import ClassSecurityInfo

from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateMapEngines(UpdateScript):
    """ Update script  """
    title = 'Update properties of portal_map'
    creation_date = 'May 26, 2010'
    authors = ['ALex Morega']
    description = 'Rename configuration parameters and calculate icon sizes'
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        portal_map = portal.getGeoMapTool()
        repr(portal_map) # make sure it's loaded

        portal_map._p_changed = True

        try:
            address = portal_map.__dict__.pop('center_locality')
        except KeyError:
            pass
        else:
            portal_map.initial_address = address
            self.log.info('set `initial_address` to %r' % address)

        try:
            map_height_px = portal_map.__dict__.pop('map_height')
        except KeyError:
            pass
        else:
            portal_map.map_height_px = map_height_px
            self.log.info('set `map_height_px` to %r' % map_height_px)

        portal_map.__dict__.pop('center_zoom', None)


        try:
            objmap_height_px = portal_map.__dict__.pop('detailed_map_height')
        except KeyError:
            pass
        else:
            portal_map.objmap_height_px = objmap_height_px
            self.log.info('set `objmap_height_px` to %r' % objmap_height_px)

        try:
            objmap_width_px = portal_map.__dict__.pop('detailed_map_width')
        except KeyError:
            pass
        else:
            portal_map.objmap_width_px = objmap_width_px
            self.log.info('set `objmap_width_px` to %r' % objmap_width_px)

        portal_map.__dict__.setdefault('initial_address', u'Europe')
        portal_map.__dict__.setdefault('map_height_px', 500)
        portal_map.__dict__.setdefault('objmap_height_px', 400)
        portal_map.__dict__.setdefault('objmap_width_px', 400)

        portal_map.__dict__.pop('detailed_zoom', None)
        portal_map.__dict__.pop('map_width', None)
        portal_map.__dict__.pop('map_types', None)


        allow_mouse_scroll = portal_map.__dict__.pop('enableKeyControls', True)

        google_keys = portal_map.__dict__.pop('googleApiKey', '')
        if isinstance(google_keys, list):
            google_keys = '\n'.join(google_keys)
        yahoo_keys = portal_map.__dict__.pop('mapsapikey', '')
        if isinstance(yahoo_keys, list):
            yahoo_keys = '\n'.join(yahoo_keys)

        base_layer = {
                'YAHOO_MAP_SAT': 'satellite',
                'YAHOO_MAP_HYB': 'hybrid',
                'YAHOO_MAP_REG': 'map',
            }[portal_map.__dict__.pop('default_type', 'YAHOO_MAP_REG')]

        selected_engine = portal_map.__dict__.pop('map_engine', None)
        assert selected_engine in ('yahoo', 'google', None)

        has_google = ('engine_google' in portal_map.objectIds())
        has_yahoo = ('engine_yahoo' in portal_map.objectIds())

        if (selected_engine == 'google' or google_keys) and not has_google:
            portal_map.set_map_engine('google')
            ge = portal_map.get_map_engine()
            if google_keys:
                ge.api_keys = google_keys
            ge.base_layer = base_layer
            ge.allow_mouse_scroll = bool(allow_mouse_scroll)
            self.log.info('configured google engine: '
                          'keys=%r, base_layer=%r, allow_mouse_scroll=%r' %
                          (google_keys, base_layer, allow_mouse_scroll))

        if (selected_engine == 'yahoo' or yahoo_keys) and not has_yahoo:
            portal_map.set_map_engine('yahoo')
            ye = portal_map.get_map_engine()
            if yahoo_keys:
                ye.api_keys = yahoo_keys
            ye.base_layer = base_layer
            self.log.info('configured yahoo engine: keys=%r, base_layer=%r' %
                          (yahoo_keys, base_layer))

        if not (has_google or has_yahoo) and selected_engine is None:
            selected_engine = 'google'

        if selected_engine is not None:
            portal_map.set_map_engine(selected_engine)
            self.log.info('set map engine to %r' % selected_engine)

        image_size_count = 0
        for symbol in portal_map.getSymbolsList():
            if 'image_size' not in symbol.__dict__:
                symbol.__dict__['image_size'] = symbol._calculate_image_size()
                image_size_count += 1
        if image_size_count:
            self.log.info('calculated size for %r symbols' % image_size_count)

        return True
