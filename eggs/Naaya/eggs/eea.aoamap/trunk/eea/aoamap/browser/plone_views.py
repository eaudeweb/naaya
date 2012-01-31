""" Plone Views
"""
try:
    import simplejson
    json = simplejson
except ImportError:
    import json
import urllib
import logging
from StringIO import StringIO
import lxml.html.soupparser, lxml.etree, lxml.cssselect
from App.config import getConfiguration
from Products.Five.browser import BrowserView
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import i18n

log = logging.getLogger(__name__)

CONFIG = getConfiguration()
tiles_url = getattr(CONFIG, 'environment', {}).get('AOA_MAP_TILES', '')
aoa_url = getattr(CONFIG, 'environment', {}).get('AOA_PORTAL_URL', '')

def _to_unicode(s):
    """ To unicode
    """
    if isinstance(s, str):
        s = s.decode('utf-8')
    return s


class I18nTemplate(PageTemplateFile):
    """ hack Zope's page templates to give us sane translation behaviour """

    def __init__(self, template_name):
        super(I18nTemplate, self).__init__(template_name, globals())

    def __call__(self, lang, *args, **kwargs):
        self.__lang = lang
        return super(I18nTemplate, self).__call__(*args, **kwargs)

    def __translate(self, msgid, domain=None, mapping=None, default=None):
        """ Translate
        """
        if mapping is not None:
            for k in mapping:
                mapping[k] = _to_unicode(mapping[k])
        return i18n.translate(msgid, domain, mapping, default=default,
                              target_language=self.__lang)

    def pt_getEngineContext(self, namespace):
        """ Engine context
        """
        context = super(I18nTemplate, self).pt_getEngineContext(namespace)
        context.translate = self.__translate
        return context


map_template = I18nTemplate('map.pt')

def css(sel, target):
    """ CSS
    """
    return lxml.cssselect.CSSSelector(sel)(target)


class AoaMap(BrowserView):
    """
    The "AoA map search" page.
    """

    def _get_search_url(self):
        """ URL
        """
        return self._get_root_url() + '/aoa-map-search'

    def _get_current_language(self):
        """ Language
        """
        context = self.aq_parent
        return context.Language()

    def _get_root_url(self):
        """ Root
        """
        return self.aq_parent.getCanonical().absolute_url()

    def get_map_html(self):
        """ Map HTML
        """
        lang = self._get_current_language()
        if lang != 'ru':
            lang = 'en'

        map_config = {
            'tiles_url': tiles_url,
            'search_url': self._get_search_url(),
            'report_documents_url': self._get_root_url(),
            'debug': True,
            'www_prefix': "++resource++eea.aoamap",
            'language': lang,
        }

        options = {
            'map_config': json.dumps(map_config),
            'filter_options': {
                'themes': [u"Water", u"Green economy"],
            },
        }

        return map_template(lang, **options)


def get_aoa_response(relative_url):
    """ Response
    """
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
        """ URL
        """
        return (aoa_url + 'tools/virtual_library/'
                'bibliography-details-each-assessment?iframe=on')

class ImportFromAoa(BrowserView):
    """
    Import country fiches from AoA portal as Page objects
    """

    def aoa_data(self):
        """ Data
        """
        aoa_json = get_aoa_response('jsmap_search_map_documents')
        aoa_data = json.loads(aoa_json)

        return {
            'countries': sorted(v['en'] for
                                v in aoa_data['country_name'].values()),
            'regions': sorted(v['en'] for
                              v in aoa_data['region_name'].values()),
        }

    def submit(self):
        """ Submit
        """
        out = StringIO()

        print >> out, "Creating documents:\n"

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
                doc = update_country_fiche(self.aq_parent, country, theme,
                                           self.request.form['date'])

            print >> out, repr(doc)


        for region in self.request.form.get('region-info', []):
            doc = update_region_info(self.aq_parent, region)
            print >> out, repr(doc)


        print >> out, "\ndone"
        return out.getvalue()


def update_plone_document(folder, doc_id, title, text):
    """ Update document
    """
    try:
        doc = folder[doc_id]
    except Exception:
        folder.invokeFactory(type_name="Document", id=doc_id)
        doc = folder[doc_id]

    doc.setTitle(title)
    doc.getField('text').getMutator(doc)(text)

    return doc


def slug(name):
    """ Slug
    """
    return name.replace(' ', '-')


def update_country_profile(folder, country):
    """ Update country profile
    """
    doc_id = '%s-profile' % (slug(country),)
    title = "%s - country profile" % (country,)
    text = "Country profile HTML goes here"

    url = ('country_profile?toplone=1&country%%3Autf8%%3Austring=%s' % country)
    aoa_html = get_aoa_response(url)
    aoa_doc = lxml.html.soupparser.fromstring(aoa_html)
    cf_doc = css('div.aoa-cp-body', aoa_doc)[0]
    text = lxml.etree.tostring(cf_doc).decode('utf-8')

    return update_plone_document(folder, doc_id, title, text)


def update_country_fiche(folder, country, theme, date):
    """ Update country fiche
    """
    doc_id = '%s-%s' % (slug(country), slug(theme))
    title = "%s country fiche - %s (%s)" % (country, theme, date)

    url = (
        'viewer_aggregator?toplone=1&country%%3Autf8%%3Austring=%s&theme=%s' %
        (country, theme))
    aoa_html = get_aoa_response(url)
    aoa_doc = lxml.html.soupparser.fromstring(aoa_html)
    cf_doc = css('div.aoa-cf-content', aoa_doc)[0]
    text = lxml.etree.tostring(cf_doc).decode('utf-8')

    return update_plone_document(folder, doc_id, title, text)

def update_region_info(folder, region):
    """ Update region info
    """
    doc_id = '%s-info' % (slug(region),)
    title = "%s region" % (region,)

    url = ('region_info?toplone=1&region%%3Autf8%%3Austring=%s' % (region,))
    aoa_html = get_aoa_response(url)
    aoa_doc = lxml.html.soupparser.fromstring(aoa_html)
    cf_doc = css('div.aoa-ri-body', aoa_doc)[0]
    text = lxml.etree.tostring(cf_doc).decode('utf-8')

    return update_plone_document(folder, doc_id, title, text)
