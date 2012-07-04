import transaction

from Products.Naaya.tests import NaayaTestCase
from naaya.content.pointer.pointer_item import addNyPointer
from naaya.content.url.url_item import addNyURL
from naaya.core.zope2util import path_in_site
from Products.Naaya.NyFolder import addNyFolder

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()

    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Pointers """
        #add NyPointer
        addNyPointer(self.portal.info, id='pointer1', title='pointer1',
                     lang='en')
        addNyPointer(self.portal.info, id='pointer1_fr',
                     title='pointer1_fr', lang='fr')
        slash_pointer = addNyPointer(self.portal.info, id='pointer_slash',
                     title='pointer_slash', pointer=u'/info', lang='en')

        #Check if slash is removed
        assert getattr(self.portal.info.pointer_slash, 'pointer') == u'info'
        self.portal.info.manage_delObjects([slash_pointer])

        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Pointer'])

        #get added NyPointer
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'pointer1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'pointer1_fr':
                meta_fr = x

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'pointer1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'pointer1_fr')

        #change NyPointer title
        meta.saveProperties(title='pointer1_edited', lang='en', pointer='http://www.google.com')
        meta_fr.saveProperties(title='pointer1_fr_edited', lang='fr', pointer='http://fr.wikipedia.org')

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'pointer1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'pointer1_fr_edited')

        #delete NyPointer
        self.portal.info.manage_delObjects([meta.id])
        self.portal.info.manage_delObjects([meta_fr.id])

        meta = self.portal.getCatalogedObjectsCheckView(meta_type=['Naaya Pointer'])
        self.assertEqual(meta, [])

    def test_pointers_update_on_cut_paste_data(self):
        """ Moving an object that has a pointer to it, updates the pointer """
        cat = self.portal.getCatalogTool()
        cat.addIndex('pointer', 'FieldIndex')
        addNyURL(self.portal.info, id='some_url_ob', title='Some Url',
                 url='http://eaudeweb.ro', contributor='simiamih')
        addNyPointer(self.portal.info, id='point', title='point', lang='en',
                     pointer='info/some_url_ob')
        addNyFolder(self.portal.info, id='sub_info')
        transaction.commit()
        cp = self.portal.info.manage_cutObjects('some_url_ob')
        self.portal.info.sub_info.manage_pasteObjects(cp)
        new_path = path_in_site(self.portal.info.sub_info.some_url_ob)
        self.assertEqual(self.portal.info.point.pointer, new_path)
