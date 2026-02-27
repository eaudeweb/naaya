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

import transaction
from unittest import TestSuite, makeSuite
from Products.Naaya.tests import NaayaTestCase
from naaya.content.semide.news.semnews_item import addNySemNews, config

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self._portal().manage_install_pluggableitem(config['meta_type'])
        self.login()

    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Semide News """
        addNySemNews(self._portal().info, id='doc1', title='doc1', lang='en',
                     news_date="12/12/2010", coverage="all", archive=1)
        addNySemNews(self._portal().info, id='doc1_fr', title='doc1_fr',
            lang='fr', news_date="12/11/2000", coverage="all", archive=1)
        transaction.commit()

        docs = self._portal().getCatalogedObjectsCheckView(
            meta_type=[config['meta_type']])

        #Get added
        for x in docs:
            if x.getLocalProperty('title', 'en') == 'doc1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'doc1_fr':
                meta_fr = x

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'doc1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'doc1_fr')

        self.assertEqual('/'.join(meta.getPhysicalPath()[:-1]),
                         '/portal/info/2010/12')
        self.assertEqual('/'.join(meta_fr.getPhysicalPath()[:-1]),
                         '/portal/info/2000/11')


        #Change title and date
        meta.saveProperties(title='doc1_edited', lang='en',
                            news_date="12/12/2000", coverage="all")
        meta_fr.saveProperties(title='doc1_fr_edited', lang='fr',
                               news_date="12/12/2000", coverage="all")

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'doc1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'),
                         'doc1_fr_edited')

        self.assertEqual(self._portal().info['2000']['12'].doc1.id, 'doc1')
        self.assertEqual(self._portal().info['2000']['12'].doc1_fr.id,
                         'doc1_fr')

        #delete
        self._portal().info['2000']['12'].manage_delObjects([meta.id])
        self._portal().info['2000']['12'].manage_delObjects([meta_fr.id])

        brains = self._portal().getCatalogedObjectsCheckView(
            meta_type=[config['meta_type']])
        self.assertEqual(len(brains), 0)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
