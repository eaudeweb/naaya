from lxml import etree
from lxml.builder import ElementMaker
from hashlib import md5
from Products.NaayaCore.managers.utils import html2text, get_nsmap
from naaya.core.zope2util import path_in_site


def index_rdf_extended(context, REQUEST=None, RESPONSE=None):
    """ RDF feed """
    if not path_in_site(context).startswith(
            'who-who/market-place/certifiers-section'):
        return REQUEST.response.redirect(context.absolute_url() + '/index_rdf')
    s_tool = context.getSyndicationTool()
    if context.meta_type in context.get_naaya_containers_metatypes():
        objects = context.getPublishedContent()
    else:
        objects = [context]
    return syndicateMore(s_tool, context.absolute_url(), objects)


def syndicateMore(self, p_url, p_items=[], lang=None):
    s = self.getSite()
    if lang is None:
        lang = self.gl_get_selected_language()
    namespaces = self.getNamespaceItemsList()
    nsmap = {}
    header = []
    for n in namespaces:
        if n.prefix != '':
            nsmap[n.prefix] = n.value
        else:
            nsmap[None] = n.value
        header.append(str(n))
    rdf_namespace = nsmap['rdf']
    dc_namespace = nsmap['dc']
    Rdf = ElementMaker(namespace=rdf_namespace, nsmap=nsmap)
    Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
    E = ElementMaker(None, nsmap=nsmap)
    received_items = ''.join([syndicateThisExtended(i) for i in p_items])
    received = '<rdf:RDF %s>%s</rdf:RDF>' % (' '.join(header), received_items)
    xml_received = etree.XML(received, etree.XMLParser(strip_cdata=False))
    xml = Rdf.RDF(
        E.channel(
            E.title(s.title),
            E.link(p_url),
            E.description(html2text(s.description, trim_length=None)),
            Dc.description(s.description),
            Dc.identifier(p_url),
            Dc.date(self.utShowFullDateTimeHTML(self.utGetTodayDate())),
            Dc.hash(md5(received_items).hexdigest()),
            Dc.publisher(s.publisher),
            Dc.source(s.publisher),
            Dc.subject(s.title),
            Dc.subject(s.site_subtitle),
            Dc.language(lang),
            E.items(),
            {'{%s}about' % rdf_namespace: s.absolute_url()}
        )
    )
    channel = xml[0]
    items = channel[-1]
    seq = etree.SubElement(items, '{%s}Seq' % rdf_namespace)
    for i in p_items:
        etree.SubElement(seq, '{%s}li' % rdf_namespace,
                         resource=i.absolute_url())
    if self.hasImage():
        image = E.image(
            E.title(s.title),
            E.url(self.getImagePath()),
            E.link(s.absolute_url()),
            E.description(self.utToUtf8(s.description))
        )
        xml.append(image)
    xml.extend(xml_received)
    self.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
    return etree.tostring(xml, xml_declaration=True, encoding="utf-8")


def syndicateThisExtended(self):
    """
    Generates RDF item tag for an object.

    B{This method can be overwritten by some types of objects in order to
    add specific tags.}
    @param lang: content language
    @type lang: string
    """

    if self.meta_type != 'Naaya Contact':
        return self.syndicateThis()
    l_site = self.getSite()
    lang = self.gl_get_selected_language()
    map_tool = self.getGeoMapTool()
    syndication_tool = self.getSyndicationTool()
    namespaces = syndication_tool.getNamespaceItemsList()
    nsmap = get_nsmap(namespaces)
    rdf_namespace = nsmap['rdf']
    dc_namespace = nsmap['dc']
    Rdf = ElementMaker(namespace=rdf_namespace, nsmap=nsmap)
    Dc = ElementMaker(namespace=dc_namespace, nsmap=nsmap)
    E = ElementMaker(None, nsmap=nsmap)
    address = getattr(self.geo_location, 'address', '')
    lat = str(getattr(self.geo_location, 'lat', ''))
    lon = str(getattr(self.geo_location, 'lon', ''))
    xml = Rdf.RDF(
        E.item(
            {'{%s}about' % rdf_namespace: self.absolute_url()},
            Dc.title(self.non_empty_title(lang)),
            Dc.identifier(self.identifier()),
            Dc.description(self.getLocalProperty('description', lang)),
            Dc.address(address),
            Dc.lat(lat),
            Dc.lon(lon),
            Dc.marketplace_category(
                map_tool.getSymbolTitle(getattr(self,
                                                'category-marketplace'))),
            Dc.expiry_date(display_date(getattr(self, 'expiry_date', None))),
            Dc.id_number(str(getattr(self, 'id_number', ''))),
            Dc.language(lang)
        )
    )
    item = xml[0]
    for k in self.getLocalProperty('coverage', lang).split(','):
        item.append(Dc.coverage(k.strip()))
    the_rest = (
        Dc.publisher(l_site.getLocalProperty('publisher', lang)),
        Dc.format(self.format()),
        Dc.source(l_site.getLocalProperty('publisher', lang)),
    )
    item.extend(the_rest)
    return etree.tostring(item, xml_declaration=False, encoding="utf-8")


def display_date(expiry_date):
    if not expiry_date:
        return ''
    else:
        return expiry_date.strftime('%d %B %Y')
