from time import time
import logging
import simplejson as json
from naaya.core.backport import any

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

country_map = dict((name, i) for (i, name) in enumerate(country_list))


def all_shadows(site):
    for shadow in site['country-fiches-viewer'].iter_assessments():
        yield shadow
    for shadow in site['virtual-library-viewer'].iter_assessments():
        yield shadow


def filter_shadows(request, shadow_iter):
    # prepare filters
    form_country = request.form.get('country[]', [])
    if isinstance(form_country, basestring):
        form_country = [form_country]

    if form_country:
        search_countries = set()
        for name in form_country:
            try:
                i = country_map.get(name)
            except KeyError:
                log.warn('Country not found in list: %r', name)
            else:
                search_countries.add(i)
    else:
        search_countries = set(country_map.values())

    # perform the actual search
    for shadow in shadow_iter:
        #title = shadow.getLocalProperty('title', 'en')

        if not any(i in search_countries for i in shadow.geo_coverage_country):
            continue

        yield shadow


def do_search(ctx, request):
    t0 = time()

    documents = []
    for shadow in filter_shadows(request, all_shadows(ctx.getSite())):
        documents.append({
            "title": shadow.getLocalProperty('title', 'en'),
            "country": [country_list[i] for i in shadow.geo_coverage_country],
            "theme": shadow.theme,
        })

    return json.dumps({
        'query-time': time() - t0,
        'documents': documents,
    })
