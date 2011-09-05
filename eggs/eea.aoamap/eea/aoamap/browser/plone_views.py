import simplejson as json
import urllib
import logging
import lxml.html.soupparser, lxml.etree, lxml.cssselect
from App.config import getConfiguration
from Products.Five.browser import BrowserView
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

log = logging.getLogger(__name__)

tiles_url = getConfiguration().environment.get('AOA_MAP_TILES', '')
aoa_url = getConfiguration().environment.get('AOA_PORTAL_URL', '')


map_template = PageTemplateFile('map.pt', globals())


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

        return map_template.__of__(self.aq_parent)(**options)


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

class ImportCountryFiches(BrowserView):
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
        msg = "Created documents:\n"
        for country in self.request.form['country']:
            for theme, theme_code in [("Water", 'wa'), ("Green Economy", 'ge')]:
                url = ('viewer_aggregator'
                       '?country%%3Autf8%%3Austring=%s'
                       '&theme=%s') % (country, theme)
                aoa_html = get_aoa_response(url)
                aoa_doc = lxml.html.soupparser.fromstring(aoa_html)
                cf_doc = css('div.filter-results', aoa_doc)[0]
                cf_data = {
                    'country': country,
                    'country_code': country,
                    'theme': theme,
                    'theme_code': theme_code,
                    'html_content': lxml.etree.tostring(cf_doc).decode('utf-8'),
                }
                doc = update_country_fiche(self.aq_parent, cf_data)
                msg += "%r\n" % doc

        msg += "done\n"

        return msg


def update_country_fiche(folder, cf_data):
    doc_id = 'cf-%s-%s' % (cf_data['country_code'], cf_data['theme_code'])

    try:
        doc = folder[doc_id]
    except:
        folder.invokeFactory(type_name="Document", id=doc_id)
        doc = folder[doc_id]

    title = "Country fiche %s - %s" % (cf_data['country'], cf_data['theme'])
    doc.setTitle(title)
    doc.getField('text').getMutator(doc)(cf_data['html_content'])

    return doc
