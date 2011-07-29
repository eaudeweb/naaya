from unittest import TestSuite, makeSuite
from naaya.content.pointer.pointer_item import addNyPointer
from Products.Naaya.tests import NaayaTestCase

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
        addNyPointer(self._portal().info, id='pointer1', title='pointer1',
                     lang='en')
        addNyPointer(self._portal().info, id='pointer1_fr',
                     title='pointer1_fr', lang='fr')
        slash_pointer = addNyPointer(self._portal().info, id='pointer_slash',
                     title='pointer_slash', pointer=u'/info', lang='en')

        #Check if slash is removed
        assert getattr(self._portal().info.pointer_slash, 'pointer') == u'info'
        self._portal().info.manage_delObjects([slash_pointer])

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Pointer'])

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
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Pointer'])
        self.assertEqual(meta, [])
