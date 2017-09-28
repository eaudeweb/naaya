import os
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


_pth = lambda *name: os.path.join(os.path.dirname(__file__), *name)
_invert_en = lambda dic: dict((v['en'],k) for (k,v) in dic.iteritems())

country_name = json.load(open(_pth('country_name.json')))
country_code = _invert_en(country_name)
region_name = json.load(open(_pth('region_name.json')))
region_code = _invert_en(region_name)
region_countries = json.load(open(_pth('region_countries.json')))
theme_name = json.load(open(_pth('theme_name.json')))
theme_code = _invert_en(theme_name)


def map_if_available(mapping, values):
    for v in values:
        if v in mapping:
            yield mapping[v]


def load_patch():
    f = open(_pth('map_patch.js'), 'rb')
    data = f.read().decode('utf-8')
    f.close()
    return data


def shadow_to_dict(shadow):
    return {
        "title": {'en': shadow.viewer_title_en, 'ru': shadow.viewer_title_ru},
        "country": list(map_if_available(country_code, shadow.viewer_country)),
        "region": list(map_if_available(region_code, shadow.viewer_region)),
        "geolevel": shadow.viewer_geolevel,
        "theme": list(map_if_available(theme_code, shadow.viewer_main_theme)),
        "document_type": shadow.viewer_document_type,
        "year": shadow.viewer_year,
        "author": shadow.viewer_author,
        "url": shadow.url,
        "upload-time": shadow.creation_date.timeTime(),
    }


def get_country_index(site):
    from shadow import get_choice_mapping
    cf_viewer = site['country-fiches-viewer']
    cf_survey = cf_viewer.target_survey()
    choice_map = get_choice_mapping(cf_survey, 'w_country')
    return dict((country_code[name], idx)
                for (idx, name) in choice_map.iteritems())


def get_map_async_config(site):
    t0 = time()
    vl_viewer = site['virtual-library-viewer']

    documents = []
    for n, shadow in enumerate(vl_viewer.iter_assessments()):
        doc = shadow_to_dict(shadow)
        documents.append(doc)


    return {
        'country_name': country_name,
        'country_index': get_country_index(site),
        'region_countries': region_countries,
        'region_name': region_name,
        'theme_name': theme_name,
        'documents': documents,
        'query-time': time() - t0,
        'timestamp': time(),
        "patch": load_patch(),
    }


class SearchMapDocuments(BrowserPage):
    def __call__(self):
        aoa_devel_hook(__name__)
        aoa_devel_hook('naaya.ew_aoa_library.shadow')
        site = self.aq_parent.getSite()
        return json.dumps(get_map_async_config(site))


CONFIG = getConfiguration()
CONFIG.environment.update(os.environ)
tiles_url = CONFIG.environment.get('AOA_MAP_TILES', '')

def map_config_for_document(shadow):
    return {
        'tiles_url': tiles_url,
        'debug': bool(Globals.DevelopmentMode),
        'www_prefix': "++resource++naaya.ew_aoa_library-www",
        'document_countries': shadow.viewer_country,
    }
