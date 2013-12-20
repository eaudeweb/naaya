from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaBase.NyBase import rss_item_for_object
from naaya.content.event.event_item import addNyEvent

class NySyndicationTestCase(NaayaFunctionalTestCase):
    def test_rss_item_for_object(self):
        syndication_tool = self.portal.getSyndicationTool()
        namespaces = {}
        for n in syndication_tool.getNamespaceItemsList():
            if n.prefix!='':
                namespaces[n.prefix] = n.value
            else:
                namespaces['a'] = n.value
        addNyEvent(self.portal['info'], id='9000', contributor='Me',
                   title='Eveniment', start_date='12/12/2012', 
                   description='About something')
        event = self.portal['info']['9000']
        event.approveThis()
        self.portal.recatalogNyObject(self.portal['info']['9000'])
        lang = self.portal.gl_get_selected_language()
        self.portal._setLocalPropValue('rights', lang, 'No rights')
        tree = rss_item_for_object(event, lang)
        title = tree.xpath('./title',namespaces=namespaces)[0]
        link = tree.xpath('./link', namespaces=namespaces)[0]
        description = tree.xpath('./description', namespaces=namespaces)[0]
        dc_title = tree.xpath('./dc:title',namespaces=namespaces)[0]
        identifier = tree.xpath('./dc:identifier',namespaces=namespaces)[0]
        dc_description = tree.xpath('./dc:description', namespaces=namespaces)[0]
        contributor = tree.xpath('./dc:contributor', namespaces=namespaces)[0]
        language = tree.xpath('./dc:language', namespaces=namespaces)[0]
        rights = tree.xpath('./dc:rights', namespaces=namespaces)[0]

        self.assertEqual(title.text, event.title)
        self.assertEqual(link.text, event.absolute_url())
        self.assertEqual(description.text, event.description)
        self.assertEqual(dc_title.text, event.title)
        self.assertEqual(identifier.text, event.absolute_url())
        self.assertEqual(dc_description.text, event.description)
        self.assertEqual(contributor.text, event.contributor)
        self.assertEqual(language.text, lang)
        self.assertEqual(rights.text, event.rights)
