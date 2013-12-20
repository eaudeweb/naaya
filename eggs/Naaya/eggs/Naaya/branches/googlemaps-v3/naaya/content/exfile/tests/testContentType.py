from unittest import TestSuite, makeSuite
from naaya.content.exfile.exfile_item import addNyExFile
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()

    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Extended Files """
        #add NyExFile
        addNyExFile(self._portal().info, id='file1', title='file1', lang='en')
        addNyExFile(self._portal().info, id='file1_fr', title='file1_fr', lang='fr')

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Extended File'])

        #get added NyExFile
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'file1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'file1_fr':
                meta_fr = x

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'file1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'file1_fr')

        #change NyExFile title
        meta.saveProperties(title='file1_edited', lang='en')
        meta_fr.saveProperties(title='file1_fr_edited', lang='fr')

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'file1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'file1_fr_edited')

        #delete NyExFile
        self._portal().info.manage_delObjects([meta.getId()])
        self._portal().info.manage_delObjects([meta_fr.getId()])

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Extended File'])
        self.assertEqual(meta, [])
