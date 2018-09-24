import importlib
import time
from xml.dom import minidom
from datetime import datetime


def initialize(context):
    source = 'Products.NaayaCore.GeoMapTool.GeoMapTool'
    geomap_tool = importlib.import_module(source).GeoMapTool
    geomap_tool.export_geo_rss_dzt = export_geo_rss_dzt
    geomap_tool.list_locations = list_locations


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
            getattr(item, 'postaladdress', '').encode('utf-8').decode('utf-8'))
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


def list_locations(self, REQUEST=None, **kw):
    """" """
    if REQUEST is not None:
        kw.update(REQUEST.form)
    lat_min, lat_max, lon_min, lon_max = \
        kw.get('lat_min', ''),\
        kw.get('lat_max', ''),\
        kw.get('lon_min', ''),\
        kw.get('lon_max', '')
    try:
        float(lat_min)
    except ValueError:
        # incorrect format of the coordinate
        lat_min = ''
    try:
        float(lat_max)
    except ValueError:
        # incorrect format of the coordinate
        lat_max = ''
    try:
        float(lon_min)
    except ValueError:
        # incorrect format of the coordinate
        lon_min = ''
    try:
        float(lon_max)
    except ValueError:
        # incorrect format of the coordinate
        lon_max = ''
    geo_types = kw.get('geo_types', [])
    if not geo_types:
        # this method cannot be called without geo_types, so this is a bot
        return
    if isinstance(geo_types, str):
        geo_types = geo_types.split(',')
    category = kw.get('category', '')
    gstc_criteria = kw.get('gstc_criteria', '')
    sustainability = kw.get('sustainability', '')
    credibility = kw.get('credibility', '')
    certificate_services = kw.get('certificate_services', [])
    if isinstance(certificate_services, basestring):
        certificate_services = certificate_services.split(',')
    administrative_level = kw.get('administrative_level', [])
    if administrative_level == '':
        administrative_level = []
    if isinstance(administrative_level, str):
        administrative_level = administrative_level.split(',')
    landscape_type = kw.get('landscape_type', [])
    if landscape_type == '':
        landscape_type = []
    if isinstance(landscape_type, str):
        landscape_type = landscape_type.split(',')
    topics = kw.get('topics', [])
    if topics == '':
        topics = []
    if isinstance(topics, str):
        topics = topics.split(',')
    geo_query = kw.get('geo_query', '')
    country = kw.get('country', '')

    sort_on, sort_order = '', ''
    if kw.get('sortable', ''):
        sort_on = kw.get('sort_on', '')
        sort_order = kw.get('sort_order', '')

    first_letter = kw.get('first_letter', '')

    results = self.search_geo_objects(
        lat_min=lat_min, lat_max=lat_max, lon_min=lon_min,
        lon_max=lon_max, geo_types=geo_types, category=category,
        sustainability=sustainability, credibility=credibility,
        certificate_services=certificate_services, query=geo_query,
        administrative_level=administrative_level,
        landscape_type=landscape_type, topics=topics,
        first_letter=first_letter, sort_on=sort_on, sort_order=sort_order,
        country=country, gstc_criteria=gstc_criteria,
    )
    options = {}
    options['lat_min'] = lat_min
    options['lat_max'] = lat_max
    options['lon_min'] = lon_min
    options['lon_max'] = lon_max
    options['geo_types'] = geo_types
    options['category'] = category
    options['sustainability'] = sustainability
    options['credibility'] = credibility
    options['certificate_services'] = certificate_services
    options['administrative_level'] = administrative_level
    options['landscape_type'] = landscape_type
    options['topics'] = topics
    options['geo_query'] = geo_query
    options['country'] = country
    try:
        options['step'] = int(kw.get('step', '50'))
    except ValueError:
        options['step'] = 50
    step = options['step']
    try:
        options['start'] = int(kw.get('start', '0'))
    except ValueError:
        options['start'] = 0
    try:
        options['end'] = kw.get('all_records') and len(results) or int(
            kw.get('end', step))
    except ValueError:
        options['end'] = int(step)
    options['sortable'] = kw.get('sortable', 'True')
    options['sort_on'] = sort_on
    options['sort_order'] = sort_order
    options['first_letter'] = first_letter
    options['results'] = len(results)
    options['next_start'] = options['end']
    options['next_end'] = options['end'] + step
    options['prev_start'] = options['start'] - step
    options['prev_end'] = options['start']
    options['records'] = results[options['start']:options['end']]
    options['ratable_records'] = self._ratable_results(
        results[options['start']:options['end']])
    return self._list_locations(**options)
