from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaBase.NyBase import rdf_ns_map
from naaya.content.news.news_item import addNyNews

from lxml import etree

class NySyndicationTestCase(NaayaFunctionalTestCase):
    def test_syndication(self):
        self.portal.publisher = 'The publisher'
        self.portal.creator = 'The creator'
        addNyNews(self.portal['info'], id='9000', title='The news', source='Me')
        news = self.portal['info']['9000']
        tree = etree.XML(news.syndicateThis())
        news_type = tree.xpath('./dc:type', namespaces=rdf_ns_map)[0]
        news_format = tree.xpath('./dc:format', namespaces=rdf_ns_map)[0]
        news_source = tree.xpath('./dc:source', namespaces=rdf_ns_map)[0]
        news_creator = tree.xpath('./dc:creator', namespaces=rdf_ns_map)[0]
        news_publisher = tree.xpath('./dc:publisher', namespaces=rdf_ns_map)[0]

        self.assertEqual(news_type.text, 'Text')
        self.assertEqual(news_format.text, 'text')
        self.assertEqual(news_source.text, news.source)
        self.assertEqual(news_creator.text, self.portal.creator)
        self.assertEqual(news_publisher.text, self.portal.publisher)