from time import time
import logging
import simplejson as json
from naaya.core.backport import any
import Globals
from App.config import getConfiguration
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

log = logging.getLogger(__name__)

country_list = [ # TODO `country_list` should not be duplicated here
    "Albania",
    "Andorra",
    "Armenia",
    "Austria",
    "Azerbaijan",
    "Belarus",
    "Belgium",
    "Bosnia and Herzegovina",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Georgia",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Kazakhstan",
    "Kyrgyzstan",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "FYR of Macedonia",
    "Malta",
    "Republic of Moldova",
    "Monaco",
    "Montenegro",
    "the Netherlands",
    "Norway",
    "Poland",
    "Portugal",
    "Romania",
    "Russian Federation",
    "San Marino",
    "Serbia",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "Tajikistan",
    "Turkey",
    "Turkmenistan",
    "Ukraine",
    "the United Kingdom",
    "Uzbekistan",
    "Kosovo under un security council 1244/9950",
    "Afghanistan",
    "Algeria",
    "Australia",
    "Brazil",
    "Cambodia",
    "Cameroun",
    "Canada",
    "China",
    "Costa Rica",
    "Egypt",
    "Honduras",
    "India",
    "Indonesia",
    "Iran",
    "Israel",
    "Japan",
    "Jordan",
    "Kenya",
    "Korea",
    "Lebanon",
    "Libya",
    "Mauritius",
    "Morocco",
    "Nepal",
    "Nigeria",
    "Palestinian territory",
    "Singapore",
    "Syria",
    "Tunisia",
    "Uganda",
    "USA",
    "others",
]


def get_filter_mappings(site):
    vl_viewer = site['virtual-library-viewer']
    vl_survey = vl_viewer.target_survey()

    cf_viewer = site['country-fiches-viewer']
    cf_survey = cf_viewer.target_survey()

    flat = lambda x: list(enumerate(x))

    return {
        'cf': {
            'document_types': flat(cf_survey['w_type-document'].getChoices())[1:],
            'themes': flat(cf_survey['w_theme'].getChoices()),
        },
        'vl': {
            'document_types': flat(vl_survey['w_type-document'].getChoices())[1:],
            'themes': flat(vl_survey['w_theme'].getChoices()),
        },
    }


def all_documents(site):
    mappings = get_filter_mappings(site)
    cf_document_types = dict(mappings['cf']['document_types'])
    vl_document_types = dict(mappings['vl']['document_types'])

    for shadow in site['country-fiches-viewer'].iter_assessments():
        document_type = []
        if shadow.document_type != 0:
            document_type = [cf_document_types[shadow.document_type]]
        yield {
            "title": shadow.getLocalProperty('title', 'en'),
            "country": [country_list[i] for i in shadow.geo_coverage_country],
            "theme": shadow.theme,
            "document_type": document_type,
            "year": shadow.publication_year,
            "author": shadow.author,
            "url": shadow.url,
            "library_url": shadow.absolute_url(),
        }

    for shadow in site['virtual-library-viewer'].iter_assessments():
        document_type = []
        if shadow.document_type != 0:
            document_type = [vl_document_types[shadow.document_type]]
        yield {
            "title": shadow.getLocalProperty('title', 'en'),
            "country": [country_list[i] for i in shadow.geo_coverage_country],
            "theme": shadow.theme,
            "document_type": document_type,
            "year": shadow.publication_year,
            "author": shadow.uploader, # is `uploader` the right field here?
            "url": shadow.url,
            "library_url": shadow.absolute_url(),
        }


def filter_documents(request, ctx):
    text = request.form.get('text', '').decode('utf-8').strip().lower()

    document_type = request.form.get('document-type', None)

    theme = request.form.get('theme', None)

    year = request.form.get('year', '').strip()

    if not year:
        year = None

    country = request.form.get('country[]', [])
    if isinstance(country, basestring):
        country = [country]

    search_countries = set(country or country_list)


    # perform the actual filtering
    for document in all_documents(ctx.getSite()):

        if document_type is not None:
            if document_type != document['document_type']:
                continue

        if theme is not None:
            if theme not in document['theme']:
                continue

        if year is not None:
            if year != document['year']:
                continue

        if text not in document['title'].lower():
            continue

        if not any(i in search_countries for i in document['country']):
            continue

        yield document


def do_search(ctx, request):
    t0 = time()
    documents = list(filter_documents(request, ctx))

    return json.dumps({
        'query-time': time() - t0,
        'documents': documents,
    })


def docs_and_countries(site):
    t0 = time()
    for document in all_documents(site):
        yield document['country']
    #print 'docs_and_countries:', time() - t0


def portlet_template_options(site):
    vl_viewer = site['virtual-library-viewer']

    vl_survey = vl_viewer.target_survey()
    document_types = vl_survey['w_type-document'].getChoices()
    themes = vl_survey['w_theme'].getChoices()

    search_url = (vl_viewer.absolute_url() + '/do_map_search')

    mappings = get_filter_mappings(site)
    themes = set(dict(mappings['cf']['themes']).values() +
                 dict(mappings['vl']['themes']).values())
    document_types = set(dict(mappings['cf']['document_types']).values() +
                         dict(mappings['vl']['document_types']).values())

    map_config = {
        'tiles_url': tiles_url,
        'search_url': search_url,
        'debug': bool(Globals.DevelopmentMode),
        'www_prefix': "++resource++naaya.ew_aoa_library-www",
        'docs_and_countries': list(docs_and_countries(site)),
    }

    return {
        'map_config': map_config,
        'filter_options': {
            'themes': sorted(themes),
            'document_types': sorted(document_types),
        },
    }


tiles_url = getConfiguration().environment.get('AOA_MAP_TILES', '')

class AoaSearchMapPortlet(object):
    title = 'AoA Search Map'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        #import sys; reload(sys.modules[__name__])
        tmpl_options = portlet_template_options(self.site)
        tmpl_options['macro'] = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(**tmpl_options)

    template = NaayaPageTemplateFile('zpt/search_map', globals(),
                'naaya.ew_aoa_library.search_map')
