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


def catalog_filters_for_shadows(site):
    return {
        'meta_type': "Naaya EW_AOA Shadow Object",
        'path': [
            ofs_path(site['virtual-library-viewer']),
            ofs_path(site['country-fiches-viewer']),
        ],
    }


def shadow_to_dict(shadow):
    return {
        "title": shadow.viewer_title_en,
        "country": shadow.viewer_country,
        "theme": shadow.viewer_main_theme,
        "document_type": shadow.viewer_document_type,
        "year": shadow.viewer_year,
        "author": shadow.viewer_author,
        "url": shadow.url,
    }


def all_documents(site):
    for shadow in site['country-fiches-viewer'].iter_assessments():
        yield shadow_to_dict(shadow)

    for shadow in site['virtual-library-viewer'].iter_assessments():
        yield shadow_to_dict(shadow)


def filter_documents(ctx, request):
    site = ctx.getSite()
    lang = site.gl_get_selected_language()

    def get_field(name, default=None):
        value = request.form.get(name, '').decode('utf-8').strip()
        return value or default

    country = request.form.get('country[]', [])
    if isinstance(country, basestring):
        country = [country]

    filters = catalog_filters_for_shadows(site)
    filters.update({
        'viewer_country': {'query': country, 'operator': 'and'},
        'viewer_main_theme': get_field('theme'),
        'viewer_year': get_field('year'),
        'viewer_title_'+lang: get_field('text', ''),
    })

    library = get_field('library')
    if library == 'virtual-library':
        filters['path'] = [ofs_path(site['virtual-library-viewer'])]
    elif library == 'other-objects':
        filters['path'] = [ofs_path(site['country-fiches-viewer'])]

    for name in ['viewer_country', 'viewer_main_theme', 'viewer_year']:
        if filters[name] in (None, []):
            del filters[name]

    for brain in site.getCatalogTool()(**filters):
        yield shadow_to_dict(brain.getObject())


def do_search(ctx, request):
    t0 = time()
    documents = list(filter_documents(ctx, request))

    return json.dumps({
        'query-time': time() - t0,
        'documents': documents,
    })


class SearchMapDocuments(BrowserPage):
    def __call__(self):
        aoa_devel_hook(__name__)
        aoa_devel_hook('naaya.ew_aoa_library.shadow')
        return do_search(self.aq_parent, self.request)


def documents_summary(site):
    t0 = time()
    for brain in site.getCatalogTool()(**catalog_filters_for_shadows(site)):
        yield {
            'countries': brain['viewer_country'],
            'themes': brain['viewer_main_theme'],
        }
    #print 'documents_summary:', time() - t0


def search_map_initial_data(site):
    from shadow import get_countries_mapping
    cf_viewer = site['country-fiches-viewer']
    cf_survey = cf_viewer.target_survey()
    country_index = dict((v,k) for k, v in
                         get_countries_mapping(cf_survey).iteritems())

    return {
        'document_types': get_document_types(site),
        'documents_summary': list(documents_summary(site)),
        'country_code': country_code,
        'country_index': country_index,
    }


class SearchMapInitial(BrowserPage):
    def __call__(self):
        aoa_devel_hook(__name__)
        aoa_devel_hook('naaya.ew_aoa_library.shadow')
        return json.dumps(search_map_initial_data(self.aq_parent.getSite()))


def get_document_types(site):
    vl_viewer = site['virtual-library-viewer']
    vl_survey = vl_viewer.target_survey()
    vl_document_types = vl_survey['w_type-document'].getChoices()[1:]

    cf_viewer = site['country-fiches-viewer']
    cf_survey = cf_viewer.target_survey()
    cf_document_types = cf_survey['w_type-document'].getChoices()[1:]

    document_types = set(force_to_unicode(t) for t in
                         cf_document_types + vl_document_types)
    return sorted(document_types)


tiles_url = getConfiguration().environment.get('AOA_MAP_TILES', '')

def map_config_for_document(shadow):
    return {
        'tiles_url': tiles_url,
        'debug': bool(Globals.DevelopmentMode),
        'www_prefix': "++resource++naaya.ew_aoa_library-www",
        'document_countries': shadow.viewer_country,
    }
