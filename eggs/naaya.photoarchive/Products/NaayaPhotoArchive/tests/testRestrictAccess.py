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

from unittest import TestSuite, makeSuite

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.tests.NaayaTestCase import load_test_file

class PhotoRestrictAccessTestCase(NaayaFunctionalTestCase):
    """ check that original photo size download restrictions are enforced """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaPhotoArchive.NyPhotoGallery import manage_addNyPhotoGallery
        from Products.NaayaPhotoArchive.NyPhotoFolder import manage_addNyPhotoFolder
        from Products.NaayaPhotoArchive.NyPhoto import addNyPhoto
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        manage_addNyPhotoGallery(self.portal.myfolder, id='g', title='My gallery', submitted=1, contributor='admin')
        manage_addNyPhotoFolder(self.portal.myfolder.g, id='f', title='My folder', submitted=1, contributor='admin')
        addNyPhoto(self.portal.myfolder.g.f, id='myphoto', title='My photo', submitted=1, contributor='contributor')
        import transaction; transaction.commit()
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        transaction.commit()

    def test_restrict_original(self):
        # first make sure the photo object has a photo
        picture_file = load_test_file('data/pink.png', globals())
        picture_data = picture_file.getvalue()
        gallery = self.portal.myfolder.g
        gallery.f.myphoto.update_data(picture_file)
        transaction.commit()

        photo_url = 'http://localhost/portal/myfolder/g/f/myphoto'

        # download the photo, making sure it's public by default
        self.browser.go(photo_url + '/view')
        self.assertEqual(picture_data, self.browser.get_html())

        # also get a thumbnail
        self.browser.go(photo_url + '/view?display=Small')
        picture_data_small = self.browser.get_html()
        self.assertTrue(picture_data_small.startswith('\x89PNG'))
        self.assertNotEqual(picture_data_small, picture_data)

        # restrict access to original photo
        gallery.f.restrict_original = True
        transaction.commit()

        # try to download original and thumbnail
        self.browser.go(photo_url + '/view')
        self.assertNotEqual(picture_data, self.browser.get_html())
        self.assertTrue(self.browser.get_url().startswith(
            'http://localhost/portal/login_html'))
        self.browser.go(photo_url + '/view?display=Small')
        self.assertEqual(picture_data_small, self.browser.get_html())

        # log in, try to download it again
        self.browser_do_login('admin', '')
        self.browser.go(photo_url + '/view')
        self.assertEqual(picture_data, self.browser.get_html())
        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(PhotoRestrictAccessTestCase))
    return suite
