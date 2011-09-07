import simplejson as json
import urllib
import logging
from StringIO import StringIO
import lxml.html.soupparser, lxml.etree, lxml.cssselect
from App.config import getConfiguration
from Products.Five.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

log = logging.getLogger(__name__)

tiles_url = getConfiguration().environment.get('AOA_MAP_TILES', '')
aoa_url = getConfiguration().environment.get('AOA_PORTAL_URL', '')


map_template = ViewPageTemplateFile('map.pt', globals())


def css(sel, target):
    return lxml.cssselect.CSSSelector(sel)(target)


class AoaMap(BrowserView):
    """
    The "AoA map search" page.
    """

    def _get_search_url(self):
        return self.context.absolute_url() + '/aoa-map-search'

    def get_map_html(self):
        map_config = {
            'tiles_url': tiles_url,
            'search_url': self._get_search_url(),
            'country_fiche_prefix': aoa_url + '/viewer_aggregator/',
            'debug': True,
            'www_prefix': "++resource++eea.aoamap",
        }

        options = {
            'map_config': json.dumps(map_config),
            'filter_options': {
                'themes': [u"Water", u"Green economy"],
            },
        }

        return map_template(self, **options)


def get_aoa_response(relative_url):
    response = urllib.urlopen(aoa_url + relative_url)
    try:
        return response.read()
    finally:
        response.close()


class AoaMapSearch(BrowserView):
    """
    Proxy search requests to the AoA portal.
    """

    def __call__(self):
        json_response = get_aoa_response('jsmap_search_map_documents')
        self.request.RESPONSE.setHeader('Content-Type', 'application/json')
        return json_response


class AddToVirtualLibrary(BrowserView):
    """
    Add entries to the Virtual Library
    """

    def get_vl_form_url(self):
        return (aoa_url + 'tools/virtual_library/'
                'bibliography-details-each-assessment?iframe=on')

class ImportFromAoa(BrowserView):
    """
    Import country fiches from AoA portal as Page objects
    """

    def aoa_data(self):
        aoa_html = get_aoa_response('viewer_aggregator')
        aoa_doc = lxml.html.soupparser.fromstring(aoa_html)

        return {
            'countries': [elem.attrib['value'] for elem in
                          css('select#country_select option', aoa_doc)],
        }

    def submit(self):
        out = StringIO()

        print>>out, "Creating documents:\n"

        theme_name = {
            'wa': "Water",
            'ge': "Green economy",
            'cp': None,
        }

        for country_document in self.request.form.get('country-document', []):
            country, theme_code = country_document.split('-')
            theme = theme_name[theme_code]

            if theme is None:
                doc = update_country_profile(self.aq_parent, country)
            else:
                doc = update_country_fiche(self.aq_parent, country, theme)

            print>>out, repr(doc)

        print>>out, "\ndone"
        return out.getvalue()


def update_plone_document(folder, doc_id, title, text):
    try:
        doc = folder[doc_id]
    except:
        folder.invokeFactory(type_name="Document", id=doc_id)
        doc = folder[doc_id]

    doc.setTitle(title)
    doc.getField('text').getMutator(doc)(text)

    return doc


def slug(name):
    return name.replace(' ', '-')


def update_country_profile(folder, country):
    doc_id = '%s-profile' % (slug(country),)
    title = "%s - country profile" % (country,)
    text = "Country profile HTML goes here"

    url = ('country_profile?toplone=1&country%%3Autf8%%3Austring=%s' % country)
    aoa_html = get_aoa_response(url)
    aoa_doc = lxml.html.soupparser.fromstring(aoa_html)
    cf_doc = css('div.aoa-cp-body', aoa_doc)[0]
    text = lxml.etree.tostring(cf_doc).decode('utf-8')

    return update_plone_document(folder, doc_id, title, text)


def update_country_fiche(folder, country, theme):
    doc_id = '%s-%s' % (slug(country), slug(theme))
    title = "%s country fiche - %s (02/09/2011)" % (country, theme)

    url = ('viewer_aggregator?toplone=1&country%%3Autf8%%3Austring=%s&theme=%s' %
           (country, theme))
    aoa_html = get_aoa_response(url)
    aoa_doc = lxml.html.soupparser.fromstring(aoa_html)
    cf_doc = css('div.aoa-cf-content', aoa_doc)[0]
    text = lxml.etree.tostring(cf_doc).decode('utf-8')

    return update_plone_document(folder, doc_id, title, text)
