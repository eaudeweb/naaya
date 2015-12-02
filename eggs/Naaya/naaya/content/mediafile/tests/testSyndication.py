from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaBase.NyBase import rdf_ns_map
from naaya.content.mediafile.mediafile_item import addNyMediaFile

from lxml import etree

class NySyndicationTestCase(NaayaFunctionalTestCase):
    def test_syndication(self):
        self.portal.publisher = 'The publisher'
        self.portal.creator = 'The creator'
        addNyMediaFile(self.portal['info'], id='9000', title='The mediafile', _skip_videofile_check=True)
        mediafile = self.portal['info']['9000']
        tree = etree.XML(mediafile.syndicateThis())
        mediafile_type = tree.xpath('./dc:type', namespaces=rdf_ns_map)[0]
        mediafile_format = tree.xpath('./dc:format', namespaces=rdf_ns_map)[0]
        mediafile_source = tree.xpath('./dc:source', namespaces=rdf_ns_map)[0]
        mediafile_creator = tree.xpath('./dc:creator', namespaces=rdf_ns_map)[0]
        mediafile_publisher = tree.xpath('./dc:publisher', namespaces=rdf_ns_map)[0]

        self.assertEqual(mediafile_type.text, 'Text')
        self.assertEqual(mediafile_format.text, 'application')
        self.assertEqual(mediafile_source.text, self.portal.publisher)
        self.assertEqual(mediafile_creator.text, self.portal.creator)
        self.assertEqual(mediafile_publisher.text, self.portal.publisher)