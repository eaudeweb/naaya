from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaBase.NyBase import rdf_ns_map
from naaya.content.exfile.exfile_item import addNyExFile

from lxml import etree

class NySyndicationTestCase(NaayaFunctionalTestCase):
    def test_syndication(self):
        self.portal.publisher = 'The publisher'
        self.portal.creator = 'The creator'
        addNyExFile(self.portal['info'], id='9000', title='The exfile')
        exfile = self.portal['info']['9000']
        tree = etree.XML(exfile.syndicateThis())
        exfile_type = tree.xpath('./dc:type', namespaces=rdf_ns_map)[0]
        exfile_format = tree.xpath('./dc:format', namespaces=rdf_ns_map)[0]
        exfile_source = tree.xpath('./dc:source', namespaces=rdf_ns_map)[0]
        exfile_creator = tree.xpath('./dc:creator', namespaces=rdf_ns_map)[0]
        exfile_publisher = tree.xpath('./dc:publisher', namespaces=rdf_ns_map)[0]

        self.assertEqual(exfile_type.text, 'Text')
        self.assertEqual(exfile_format.text, 'application')
        self.assertEqual(exfile_source.text, self.portal.publisher)
        self.assertEqual(exfile_creator.text, self.portal.creator)
        self.assertEqual(exfile_publisher.text, self.portal.publisher)