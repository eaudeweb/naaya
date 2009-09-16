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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

import blob_patch

from unittest import TestSuite, makeSuite
from datetime import datetime
from StringIO import StringIO

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.bfile.bfile_item import addNyBFile

class NyBFileTestCase(NaayaTestCase):
    """ TestCase for Naaya BFile object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])

    def add_bfile(self, **kwargs):
        addNyBFile(self.portal.myfolder, submitted=1, contributor='contributor', **kwargs)

    def test_add_blank(self):
        # add blank file
        self.add_bfile(id='mybfile', title='My bfile')
        self.assertTrue('mybfile' in self.portal.myfolder.objectIds())

        mybfile = self.portal.myfolder.mybfile
        self.assertTrue(mybfile.id, 'mybfile')
        self.assertTrue(mybfile.title, 'My bfile')
        self.assertEqual(len(mybfile._versions), 0)
        self.assertEqual(mybfile.current_version, None)

    def test_add_with_file(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.txt'
        # TODO: set filename and content-type

        now_pre = datetime.utcnow()
        self.add_bfile(id='mybfile', title='My bfile', uploaded_file=myfile)
        now_post = datetime.utcnow()

        mybfile = self.portal.myfolder.mybfile
        self.assertTrue(mybfile.id, 'mybfile')
        self.assertTrue(mybfile.title, 'My bfile')
        self.assertEqual(len(mybfile._versions), 1)
        self.assertTrue(mybfile.current_version is mybfile._versions[0])

        ver = mybfile.current_version
        self.assertTrue(now_pre <= ver.timestamp <= now_post)
        self.assertEqual(ver.open().read(), 'hello data!')
        self.assertEqual(ver.filename, 'my.txt')
        #self.assertEqual(ver.content_type, 'text/plain')

    def test_change_file(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.txt'
        self.add_bfile(id='mybfile', title='My bfile', uploaded_file=myfile)
        mybfile = self.portal.myfolder.mybfile

        myfile2 = StringIO('new data')
        myfile2.filename = 'other.txt'
        mybfile._save_file(myfile2)

        self.assertEqual(len(mybfile._versions), 2)
        cv = mybfile.current_version
        self.assertEqual(cv.filename, 'other.txt')
        self.assertEqual(cv.open().read(), 'new data')

    def test_remove_version(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.txt'
        self.add_bfile(id='mybfile', title='My bfile', uploaded_file=myfile)
        mybfile = self.portal.myfolder.mybfile

        myfile2 = StringIO('new data')
        myfile2.filename = 'other.txt'
        mybfile._save_file(myfile2)

        mybfile.remove_version(1)
        self.assertEqual(mybfile._versions[1].open().read(), '')
        self.assertEqual(mybfile._versions[1].removed, True)
        self.assertTrue(mybfile.current_version is mybfile._versions[0])

        myfile3 = StringIO('even newer data')
        myfile3.filename = 'other.txt'
        mybfile._save_file(myfile3)
        self.assertTrue(mybfile.current_version is mybfile._versions[2])

        mybfile.remove_version(2)
        self.assertTrue(mybfile.current_version is mybfile._versions[0])

        mybfile.remove_version(0)
        self.assertTrue(mybfile.current_version is None)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyBFileTestCase))
    return suite
