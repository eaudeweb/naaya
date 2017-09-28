from lxml import etree
from StringIO import StringIO
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

class Test_xml_feed_metadata(NaayaTestCase):
    """ Check the RDF feed for the expected metadata. """

    def test_xml_feed_metadata(self):
        self.portal.title = 'Site title'
        self.portal.description = 'About site'
        self.portal.publisher = 'X'
        self.portal.creator = 'Y'
        self.portal.site_subtitle = 'Site subtitle'

        xml_str = self.portal.localchannels_rdf()
        namespaces = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'ev': 'http://purl.org/rss/1.0/modules/event/',
            'a':'http://purl.org/rss/1.0/'}
        def xpath(tag, parent):
            return parent.xpath('./%s'%tag, namespaces=namespaces)

        tree = etree.parse(StringIO(xml_str))
        channel = tree.xpath('/rdf:RDF/a:channel', namespaces=namespaces)[0]
        title = xpath('a:title', channel)[0]
        link = xpath('a:link', channel)[0]
        description = xpath('a:description', channel)[0]
        dc_description = xpath('dc:description', channel)[0]
        identifier = xpath('dc:identifier', channel)[0]
        publisher = xpath('dc:publisher', channel)[0]
        creator = xpath('dc:creator', channel)[0]
        subject = xpath('dc:subject', channel)
        language = xpath('dc:language', channel)[0]
        resources = tree.xpath(
                            '/rdf:RDF/a:channel/a:items/rdf:Seq/rdf:li',
                             namespaces=namespaces)
        items = tree.xpath('/rdf:RDF/a:item', namespaces=namespaces)
        script_channels = self.portal.getSyndicationTool().get_script_channels()
        rdf_namespace = namespaces['rdf']

        self.assertEqual(channel.attrib['{%s}about'%rdf_namespace], self.portal.absolute_url())
        self.assertEqual(title.text, self.portal.title)
        self.assertEqual(link.text, self.portal.absolute_url())
        self.assertEqual(description.text, self.portal.description)
        self.assertEqual(dc_description.text, self.portal.description)
        self.assertEqual(publisher.text, self.portal.publisher)
        self.assertEqual(creator.text, self.portal.creator)
        self.assertEqual(identifier.text, self.portal.absolute_url())
        self.assertEqual(subject[0].text, self.portal.title)
        self.assertEqual(subject[1].text, self.portal.site_subtitle)
        self.assertEqual(language.text, self.portal.gl_get_selected_language())

        script_channels_urls = [s.absolute_url() for s in script_channels]
        about_attr = [item.attrib['{%s}about'%rdf_namespace] for item in items]
        resource_attr = [resource.attrib['resource'] for resource in resources]
        self.assertEqual(about_attr, script_channels_urls)
        self.assertEqual(resource_attr, script_channels_urls)
        for i in range(0, len(items)):
            link = xpath('a:link', items[i])[0]
            self.assertEqual(link.text, script_channels_urls[i])
