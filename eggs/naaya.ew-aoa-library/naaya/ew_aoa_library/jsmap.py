import os.path
from time import time
import logging
import simplejson as json
from naaya.core.backport import any
from naaya.core.zope2util import ofs_path
from naaya.core.utils import force_to_unicode
import Globals
from App.config import getConfiguration
from zope.publisher.browser import BrowserPage

from devel import aoa_devel_hook

log = logging.getLogger(__name__)


country_code = json.load(open(os.path.join(os.path.dirname(__file__),
                                           'country_code.json')))


def shadow_to_dict(shadow):
    pth = shadow.getPhysicalPath()
    if 'virtual-library-viewer' in pth:
        library = 'virtual-library'
    elif 'country-fiches-viewer' in pth:
        library = 'other-objects'
    else:
        library = None

    return {
        "title": shadow.viewer_title_en,
        "country": shadow.viewer_country,
        "region": shadow.viewer_region,
        "geolevel": shadow.viewer_geolevel,
        "theme": shadow.viewer_main_theme,
        "document_type": shadow.viewer_document_type,
        "year": shadow.viewer_year,
        "author": shadow.viewer_author,
        "url": shadow.url,
        "library": library,
    }


def all_documents(site):
    for shadow in site['country-fiches-viewer'].iter_assessments():
        yield shadow_to_dict(shadow)

    for shadow in site['virtual-library-viewer'].iter_assessments():
        yield shadow_to_dict(shadow)


def get_country_index(site):
    from shadow import get_countries_mapping
    cf_viewer = site['country-fiches-viewer']
    cf_survey = cf_viewer.target_survey()
    return dict((v,k) for k, v in get_countries_mapping(cf_survey).iteritems())


def get_map_async_config(site):
    t0 = time()
    return {
        'country_code': country_code,
        'country_index': get_country_index(site),
        'documents': list(all_documents(site)),
        'query-time': time() - t0,
    }


class SearchMapDocuments(BrowserPage):
    def __call__(self):
        aoa_devel_hook(__name__)
        aoa_devel_hook('naaya.ew_aoa_library.shadow')
        site = self.aq_parent.getSite()
        return json.dumps(get_map_async_config(site))


tiles_url = getConfiguration().environment.get('AOA_MAP_TILES', '')

def map_config_for_document(shadow):
    return {
        'tiles_url': tiles_url,
        'debug': bool(Globals.DevelopmentMode),
        'www_prefix': "++resource++naaya.ew_aoa_library-www",
        'document_countries': shadow.viewer_country,
    }
