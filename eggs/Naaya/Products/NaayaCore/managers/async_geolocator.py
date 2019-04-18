import logging
import time
import transaction
from Products.NaayaCore.GeoMapTool.managers import geocoding
from datetime import datetime, timedelta
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from naaya.core.ggeocoding import GeocoderServiceError
LOG = logging.getLogger(__name__)


def _cron_geolocate(site, heartbeat):

    if not getattr(site, 'geolocation_queue', None):
        return
    # Google restricts geolocation to 2500 requests per site
    # per day so when reached we need to wait a day
    when = heartbeat.when
    previous = getattr(site, 'previous_geolocation', None)
    if not previous or when > previous + timedelta(hours=1):
        geolocate_queue(site)


def geolocate_queue(site):
    for site_path in list(site.geolocation_queue):
        try:
            obj = site.unrestrictedTraverse(site_path)
        except KeyError:
            # the object is not there anymore
            site.geolocation_queue.remove(site_path)
            site._p_changed = True
            LOG.debug('object not found %s' % site_path)
            transaction.commit()
            continue
        lat = obj.geo_location.lat
        lon = obj.geo_location.lon
        address = obj.geo_location.address
        if address and not (lat and lon):
            try:
                # Google also restricts requests per second, so we need
                # to be careful for this, too
                time.sleep(2)
                lat, lon = geocoding.location_geocode(address.encode('utf-8'))
                if lat and lon:
                    obj.geo_location = Geo(lat, lon, address)
                    obj.recatalogNyObject(obj)
                site.geolocation_queue.remove(site_path)
                site._p_changed = True
                LOG.info('coodrdinates %s and %s found for %s' %
                         (lat, lon, address))
                transaction.commit()
            except GeocoderServiceError, e:
                if 'ZERO_RESULTS' in e.args[0]:
                    LOG.info('coodrdinates not found for %s' % address)
                    site.geolocation_queue.remove(site_path)
                else:
                    LOG.info(e)
                    site.previous_geolocation = datetime.now()
                    site._p_changed = True
                    break
        else:
            LOG.info('object already geolocated %s' % site_path)
            site.geolocation_queue.remove(site_path)
            site._p_changed = True
            transaction.commit()
