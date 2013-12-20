from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaBase.NyBase import rdf_ns_map
from naaya.content.story.story_item import addNyStory

from lxml import etree

class NySyndicationTestCase(NaayaFunctionalTestCase):
    def test_syndication(self):
        self.portal.publisher = 'The publisher'
        self.portal.creator = 'The creator'
        addNyStory(self.portal['info'], id='9000', title='The story')
        story = self.portal['info']['9000']
        tree = etree.XML(story.syndicateThis())
        story_type = tree.xpath('./dc:type', namespaces=rdf_ns_map)[0]
        story_format = tree.xpath('./dc:format', namespaces=rdf_ns_map)[0]
        story_source = tree.xpath('./dc:source', namespaces=rdf_ns_map)[0]
        story_creator = tree.xpath('./dc:creator', namespaces=rdf_ns_map)[0]
        story_publisher = tree.xpath('./dc:publisher', namespaces=rdf_ns_map)[0]

        self.assertEqual(story_type.text, 'Text')
        self.assertEqual(story_format.text, 'text')
        self.assertEqual(story_source.text, self.portal.publisher)
        self.assertEqual(story_creator.text, self.portal.creator)
        self.assertEqual(story_publisher.text, self.portal.publisher)