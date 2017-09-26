import importlib
import time
from xml.dom import minidom
from datetime import datetime


def initialize(context):
    source = 'Products.NaayaCore.GeoMapTool.GeoMapTool'
    geomap_tool = importlib.import_module(source).GeoMapTool
    geomap_tool.export_geo_rss_dzt = export_geo_rss_dzt


def export_geo_rss_dzt(self, sort_on='', sort_order='',
                       REQUEST=None, **kwargs):
    """ """
    timestamp = datetime.fromtimestamp(time.time())
    timestamp = str(timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
    rss = ["""<feed xmlns="http://www.w3.org/2005/Atom"
          xmlns:georss="http://www.georss.org/georss"
          xmlns:extData="http://destinet.eu/extData">
          <title>%s</title>
          <id>%s</id>
          <link rel="self" href="%s" />
          <author><name>European Environment Agency</name></author>
          <updated>%s</updated>
          """ % (self.title, self.absolute_url(), self.absolute_url(),
                 timestamp)]
    items = self.search_geo_objects(REQUEST=REQUEST, sort_on=sort_on,
                                    sort_order=sort_order, **kwargs)

    for item in items:
        doc = minidom.Document()
        entry = doc.createElement("entry")

        id_node = doc.createElement("id")
        id_node.appendChild(doc.createTextNode("%s" %
                                               (item.absolute_url(1))))
        entry.appendChild(id_node)

        link_node = doc.createElement("link")
        link_node.setAttribute("href", item.absolute_url())
        entry.appendChild(link_node)

        title_node = doc.createElement("title")
        if item.title:
            title = doc.createTextNode(
                item.title.encode('utf-8').decode('utf-8'))
        else:
            title = doc.createTextNode(str(item.getId()))
        title_node.appendChild(title)
        entry.appendChild(title_node)
        summary_node = doc.createElement("summary")
        summary_node.setAttribute("type", "html")
        description = [item.description.encode('utf-8').decode('utf-8')]
        description.append(
            "<b>Address</b>: %s" %
            item.geo_location.address.encode('utf-8').decode('utf-8'))
        if hasattr(item.aq_self, 'webpage'):
            description.append(
                "<b>Webpage:</b>: %s" %
                item.webpage.encode('utf-8').decode('utf-8'))
        if hasattr(item.aq_self, 'contact'):
            description.append(
                "<b>Contact:</b>: %s" %
                item.contact.encode('utf-8').decode('utf-8'))
        if hasattr(item.aq_self, 'source') and item.source:
            description.append(
                "<b>Source:</b>: %s" %
                item.source.encode('utf-8').decode('utf-8'))
        summary_node.appendChild(doc.createTextNode(
            "%s" % ("<br />".join(description))))
        entry.appendChild(summary_node)

        type_node = doc.createElement("georss:featuretypetag")
        coords = doc.createTextNode(
            getattr(self.getSymbol(item.geo_type), 'title', ''))
        type_node.appendChild(coords)
        entry.appendChild(type_node)

        geo_node = doc.createElement("georss:point")
        coords = doc.createTextNode("%s %s" % (item.geo_location.lat,
                                               item.geo_location.lon))
        geo_node.appendChild(coords)
        entry.appendChild(geo_node)

        url_node = doc.createElement("extData:url")
        url = doc.createTextNode(item.webpage.encode('utf-8').decode('utf-8'))
        url_node.appendChild(url)
        entry.appendChild(url_node)

        address_node = doc.createElement("extData:address")
        address = doc.createTextNode(
            item.postaladdress.encode('utf-8').decode('utf-8'))
        address_node.appendChild(address)
        entry.appendChild(address_node)

        certificate_node = doc.createElement("extData:certificate")
        certificate = doc.createTextNode(
            getattr(item, 'keywords', '').encode('utf-8').decode('utf-8'))
        certificate_node.appendChild(certificate)
        entry.appendChild(certificate_node)

        type_node = doc.createElement("extData:type")
        symbol_title = self.getSymbolTitle(
            getattr(item, 'category-marketplace', ''))
        type = doc.createTextNode(
            symbol_title.encode('utf-8').decode('utf-8'))
        type_node.appendChild(type)
        entry.appendChild(type_node)

        lat_node = doc.createElement("extData:lat")
        lat = doc.createTextNode(str(item.geo_location.lat))
        lat_node.appendChild(lat)
        entry.appendChild(lat_node)

        lng_node = doc.createElement("extData:lng")
        lng = doc.createTextNode(str(item.geo_location.lon))
        lng_node.appendChild(lng)
        entry.appendChild(lng_node)

        try:
            rss.append(entry.toprettyxml())
        except UnicodeDecodeError:
            print entry
    if REQUEST:
        REQUEST.RESPONSE.setHeader('Content-Type', 'application/atom+xml')
        REQUEST.RESPONSE.setHeader('Content-Disposition',
                                   'attachment;filename=locations.xml')
    rss.append("</feed>")
    return '\n'.join(rss)
