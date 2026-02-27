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
# David Batranu, Eau de Web
# Alin Voinea, Eau de Web

from unittest import TestSuite, makeSuite
from naaya.content.project.project_item import addNyProject
from Products.Naaya.tests import NaayaTestCase

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        self.install_content_type('Naaya Project')
        
    def beforeTearDown(self):
        self.remove_content_type('Naaya Project')
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Projects """
        #add NyProject
        addNyProject(self._portal().info, id='project', title='Project Title')
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Project'])
        
        #get added NyProject
        for x in meta:
            if x.title == 'Project Title':
                meta = x
        
        self.assertEqual(meta.title, 'Project Title')
        
        #change NyProject title
        meta.saveProperties(title='Project Title edited')
        
        self.assertEqual(meta.title, 'Project Title edited')
        
        self.assertEqual(meta.sortorder, 100)
        
        #delete NyProject
        self._portal().info.manage_delObjects([meta.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Project'])
        self.assertEqual(meta, [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
