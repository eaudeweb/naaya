# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
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

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
