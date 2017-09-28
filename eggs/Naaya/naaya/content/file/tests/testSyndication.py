from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaBase.NyBase import rdf_ns_map
from naaya.content.file.file_item import addNyFile

from lxml import etree

class NySyndicationTestCase(NaayaFunctionalTestCase):
    def test_syndication(self):
        self.portal.publisher = 'The publisher'
        self.portal.creator = 'The creator'
        addNyFile(self.portal['info'], id='9000', title='The file')
        file = self.portal['info']['9000']
        tree = etree.XML(file.syndicateThis())
        file_type = tree.xpath('./dc:type', namespaces=rdf_ns_map)[0]
        file_format = tree.xpath('./dc:format', namespaces=rdf_ns_map)[0]
        file_source = tree.xpath('./dc:source', namespaces=rdf_ns_map)[0]
        file_creator = tree.xpath('./dc:creator', namespaces=rdf_ns_map)[0]
        file_publisher = tree.xpath('./dc:publisher', namespaces=rdf_ns_map)[0]

        self.assertEqual(file_type.text, 'Text')
        self.assertEqual(file_format.text, 'application')
        self.assertEqual(file_source.text, self.portal.publisher)
        self.assertEqual(file_creator.text, self.portal.creator)
        self.assertEqual(file_publisher.text, self.portal.publisher)