from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaBase.NyBase import rdf_ns_map
from naaya.content.event.event_item import addNyEvent

from lxml import etree

class NySyndicationTestCase(NaayaFunctionalTestCase):
    def test_syndication(self):
        self.portal.publisher = 'The publisher'
        addNyEvent(self.portal['info'], id='9000', contributor='Me',
        title='Eveniment', lang='en', start_date='12/12/2012', end_date='13/12/2012', host='Me', location='Somewhere')
        event = self.portal['info']['9000']
        tree = etree.XML(event.syndicateThis())
        event_contrib = tree.xpath('./dc:contributor', namespaces=rdf_ns_map)[0]
        event_type = tree.xpath('./dc:type', namespaces=rdf_ns_map)[0]
        event_format = tree.xpath('./dc:format', namespaces=rdf_ns_map)[0]
        event_source = tree.xpath('./dc:source', namespaces=rdf_ns_map)[0]
        event_host = tree.xpath('./ev:organizer', namespaces=rdf_ns_map)[0]
        event_startdate = tree.xpath('./ev:startdate', namespaces=rdf_ns_map)[0]
        event_enddate = tree.xpath('./ev:enddate', namespaces=rdf_ns_map)[0]
        event_location = tree.xpath('./ev:location', namespaces=rdf_ns_map)[0]
        about = tree.xpath('//@rdf:about', namespaces=rdf_ns_map)[0]
        lang = self.portal.gl_get_selected_language()

        self.assertEqual(about, event.absolute_url())
        self.assertEqual(event_contrib.text, "Me")
        self.assertEqual(event_type.text, 'Event')
        self.assertEqual(event_format.text, 'text')
        self.assertEqual(event_source.text, self.portal.publisher)
        self.assertEqual(event_host.text, event.host)
        self.assertEqual(event_location.text, event.location)
        self.assertEqual(event_startdate.text, event.utShowFullDateTimeHTML(event.start_date))
        self.assertEqual(event_enddate.text, event.utShowFullDateTimeHTML(event.end_date))