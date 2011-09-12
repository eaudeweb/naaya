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
region_countries = json.load(open(os.path.join(os.path.dirname(__file__),
                                               'region_countries.json')))


def shadow_to_dict(shadow):
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
    }


def get_country_index(site):
    from shadow import get_choice_mapping
    cf_viewer = site['country-fiches-viewer']
    cf_survey = cf_viewer.target_survey()
    choice_map = get_choice_mapping(cf_survey, 'w_country')
    return dict((v,k) for k, v in choice_map.iteritems())


def get_map_async_config(site):
    t0 = time()
    vl_viewer = site['virtual-library-viewer']

    TOP_DOCS_COUNT = 20
    top_docs = [(None, None) for c in range(TOP_DOCS_COUNT)]

    documents = []
    for n, shadow in enumerate(vl_viewer.iter_assessments()):
        documents.append(shadow_to_dict(shadow))
        doc_time = shadow.creation_date.timeTime()
        if doc_time > top_docs[-1][0]:
            top_docs[-1] = (doc_time, n)
            top_docs.sort(reverse=True)


    return {
        'country_code': country_code,
        'country_index': get_country_index(site),
        'region_countries': region_countries,
        'documents': documents,
        'recent': [p[1] for p in top_docs if p[0] is not None],
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
