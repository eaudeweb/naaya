from unittest import TestSuite, makeSuite
from naaya.content.event.event_item import addNyEvent
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()

    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Events """
        #add NyEvent
        addNyEvent(self._portal().info, id='event1', title='event1', lang='en', start_date="10/10/2000")
        addNyEvent(self._portal().info, id='event1_fr', title='event1_fr', lang='fr', start_date="10/10/2000")

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Event'])

        #get added NyEvent
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'event1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'event1_fr':
                meta_fr = x

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'event1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'event1_fr')

        #change NyEvent title
        meta.saveProperties(title='event1_edited', lang='en', start_date='10/10/2000')
        meta_fr.saveProperties(title='event1_fr_edited', lang='fr', start_date='10/10/2000')

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'event1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'event1_fr_edited')

        #delete NyEvent
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Event'])
        self.assertEqual(meta, [])

    def test_change_topitem_status(self):
        """ show/hide event on the front page """
        #add NyEvent
        addNyEvent(self._portal().info, id='event1', title='event1', lang='en', start_date="10/10/2000", topitem=False)

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Event'], topitem=1)
        self.assertEqual(meta, [])

        #show event on the front page
        self._portal().info.event1.change_topitem_status()
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Event'], topitem=1)
        self.assertEqual(meta[0].getLocalProperty('title', 'en'), 'event1')

        #hide event from the front page
        self._portal().info.event1.change_topitem_status()
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Event'], topitem=1)
        self.assertEqual(meta, [])
