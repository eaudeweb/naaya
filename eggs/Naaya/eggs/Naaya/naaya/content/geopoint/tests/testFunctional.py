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

import re
from unittest import TestSuite, makeSuite
from copy import deepcopy

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.SchemaTool.widgets.geo import Geo

class GeoPointMixin(object):
    """ testing mix-in that installs the Naaya GeoPoint content type """

    geopoint_metatype = 'Naaya GeoPoint'
    geopoint_permission = 'Naaya - Add Naaya GeoPoint objects'

    def geopoint_install(self):
        self.portal.manage_install_pluggableitem(self.geopoint_metatype)
        add_content_permissions = deepcopy(self.portal.acl_users.getPermission('Add content'))
        add_content_permissions['permissions'].append(self.geopoint_permission)
        self.portal.acl_users.editPermission('Add content', **add_content_permissions)

    def geopoint_uninstall(self):
        add_content_permissions = deepcopy(self.portal.acl_users.getPermission('Add content'))
        add_content_permissions['permissions'].remove(self.geopoint_permission)
        self.portal.acl_users.editPermission('Add content', **add_content_permissions)
        self.portal.manage_uninstall_pluggableitem(self.geopoint_metatype)

class NyGeoPointFunctionalTestCase(NaayaFunctionalTestCase, GeoPointMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.geopoint_install()
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaContent.NyGeoPoint.NyGeoPoint import addNyGeoPoint
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        self.portal.myfolder.folder_meta_types.append('Naaya GeoPoint')
        addNyGeoPoint(self.portal.myfolder, id='mygeopoint', title='My geopoint',
            submitted=1, contributor='contributor', geo_location=Geo('13', '13'))
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.geopoint_uninstall()
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/geopoint_add_html')
        self.failUnless('<h1>Submit GeoPoint</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
            'geo_location.lat:utf8:ustring', 'geo_location.lon:utf8:ustring',
            'geo_location.address:utf8:ustring',
            'geo_type:utf8:ustring', 'url:utf8:ustring', 'pointer:utf8:ustring',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_geopoint'
        form['description:utf8:ustring'] = 'test_geopoint_description'
        form['coverage:utf8:ustring'] = 'test_geopoint_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'
        form['geo_location.lat:utf8:ustring'] = '12.587142'
        form['geo_location.lon:utf8:ustring'] = '55.681004'
        form['geo_location.address:utf8:ustring'] = 'Kongens Nytorv 6, 1050 Copenhagen K, Denmark'
        #form['geo_type:utf8:ustring'] = ''
        form['url:utf8:ustring'] = 'http://www.eea.europa.eu'
        form['pointer:utf8:ustring'] = 'portal/info/contact'

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Thank you for your submission</h1>' in html)

        geopoint = self.portal.myfolder.testgeopoint
        self.failUnlessEqual(geopoint.title, 'test_geopoint')
        self.failUnlessEqual(geopoint.geo_location,
            Geo('12.587142', '55.681004',
            'Kongens Nytorv 6, 1050 Copenhagen K, Denmark'))
        self.failUnlessEqual(geopoint.url, 'http://www.eea.europa.eu')
        geopoint.approveThis()

        self.browser.go('http://localhost/portal/myfolder/testgeopoint')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_geopoint.*</h1>', html, re.DOTALL))
        self.failUnless('test_geopoint_description' in html)
        self.failUnless('test_geopoint_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/geopoint_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mygeopoint/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My geopoint')

        form['title:utf8:ustring'] = 'new_geopoint_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mygeopoint.title, 'new_geopoint_title')

        self.browser.go('http://localhost/portal/myfolder/mygeopoint/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mygeopoint.title, 'new_geopoint_title')
        self.failUnlessEqual(self.portal.myfolder.mygeopoint.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mygeopoint/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        form['title:utf8:ustring'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

class NyGeoPointVersioningFunctionalTestCase(NaayaFunctionalTestCase, GeoPointMixin):
    """ TestCase for NaayaContent object """
    def afterSetUp(self):
        self.geopoint_install()
        from Products.NaayaContent.NyGeoPoint.NyGeoPoint import addNyGeoPoint
        addNyGeoPoint(self.portal.info, id='ver_geopoint', title='ver_geopoint',
            submitted=1, geo_location=Geo('13', '13'))
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['ver_geopoint'])
        self.geopoint_uninstall()
        import transaction; transaction.commit()

    def test_start_version(self):
        from Products.NaayaContent.NyGeoPoint.geopoint_item import geopoint_item
        self.browser_do_login('admin', '')
        self.failUnlessEqual(self.portal.info.ver_geopoint.version, None)
        self.browser.go('http://localhost/portal/info/ver_geopoint/startVersion')
        self.failUnless(isinstance(self.portal.info.ver_geopoint.version, geopoint_item))
        self.browser_do_logout()

    def test_edit_version(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/ver_geopoint/startVersion')

        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'ver_geopoint_newtitle'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        ver_geopoint = self.portal.info.ver_geopoint
        self.failUnlessEqual(ver_geopoint.title, 'ver_geopoint')
        # we can't do ver_geopoint.version.title because version objects don't have the _languages property
        self.failUnlessEqual(ver_geopoint.version.getLocalProperty('title', 'en'), 'ver_geopoint_newtitle')

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyGeoPointFunctionalTestCase))
    suite.addTest(makeSuite(NyGeoPointVersioningFunctionalTestCase))
    return suite
