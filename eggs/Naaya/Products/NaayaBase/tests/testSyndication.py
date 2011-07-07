from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.SyndicationTool.managers.namespaces_tool import namespaces_tool
from Products.NaayaBase import NyBase
from naaya.content.url.url_item import addNyURL

from lxml import etree

class NySyndicationTestCase(NaayaFunctionalTestCase):
    def test_latestuploads(self):
        syndication_tool = self.portal.getSyndicationTool()
        namespaces = {}
        for n in syndication_tool.getNamespaceItemsList():
            if n.prefix!='':
                namespaces[n.prefix] = n.value
            else:
                namespaces['a'] = n.value
        addNyURL(self.portal['info'], 'testurl', title="URL")
        testurl =  self.portal['info']['testurl']
        testurl.approveThis()
        self.portal.recatalogNyObject(self.portal['info']['testurl'])
        tree = etree.XML(self.portal.portal_syndication['latestuploads_rdf'].index_html())
        found = 0
        resources = tree.xpath('//rdf:li[@resource]', namespaces=namespaces)
        for resource in resources:
            if resource.attrib['resource']==testurl.absolute_url():
                found = 1
        namespace = namespaces['a']
        rdf_namespace = namespaces['rdf']
        items = tree.xpath('./a:item', namespaces=namespaces)
        my_url_item = tree.xpath("./a:item[@rdf:about='%s']"%testurl.absolute_url(),
                                 namespaces=namespaces)[0]
        contributor = my_url_item.xpath('./dc:contributor',namespaces=namespaces)[0]
        format = my_url_item.xpath('./dc:format', namespaces=namespaces)[0]

        self.assertEqual(found,1)
        self.assertEqual(contributor.text, self.portal['info']['testurl'].contributor)
        self.assertEqual(format.text, 'text/html')
