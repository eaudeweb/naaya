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
from urllib import quote
from StringIO import StringIO
from unittest import TestSuite, makeSuite
from random import random
from Testing import ZopeTestCase
import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaContent.discover import get_pluggable_content
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaContent.NyGeoPoint.tests.testFunctional import GeoPointMixin
from Products.NaayaContent.NyExFile.tests.testFunctional import ExFileMixin
from Products.NaayaContent.NyMediaFile.tests.testFunctional import MediaFileMixin
from Products.NaayaContent.NyContact.tests.testFunctional import ContactMixin

# not all content types will pass all tests
SCHEMA_EXCEPTIONS = []
DYNAMIC_PROPERTIES_EXCEPTIONS = []
FORM_REMEMBER_DATA_EXCEPTIONS = []
TRANSLATE_OBJECT_EXCEPTIONS = []

# these content types don't support dynamic properties
DYNAMIC_PROPERTIES_EXCEPTIONS += [ 'NyExFile', 'NyMediaFile', 'NyGeoPoint' ]

# NySMAP* products need an EnviroWindows site to function properly
# so we can't easily test them here
SCHEMA_EXCEPTIONS += ['NySMAPExpert', 'NySMAPProject']
DYNAMIC_PROPERTIES_EXCEPTIONS += ['NySMAPExpert', 'NySMAPProject']
FORM_REMEMBER_DATA_EXCEPTIONS += ['NySMAPExpert', 'NySMAPProject']
TRANSLATE_OBJECT_EXCEPTIONS += ['NySMAPExpert', 'NySMAPProject']

# Ny(Simlple)?Consultation is also non-conformant
consultation_products = ['NyConsultation', 'NySimpleConsultation', 'NyTalkBackConsultation']
SCHEMA_EXCEPTIONS += consultation_products
DYNAMIC_PROPERTIES_EXCEPTIONS += consultation_products
FORM_REMEMBER_DATA_EXCEPTIONS += consultation_products
TRANSLATE_OBJECT_EXCEPTIONS += consultation_products

def _list_content_types():
    for content_type in get_pluggable_content().values():
        if content_type.get('_class', None) is None:
            continue
        yield content_type
content_types = list(_list_content_types())

class ContentTypeConformanceTestCase(ZopeTestCase.TestCase):
    """
    Make sure all the Naaya content types meet certain correctness requirements
    """

    def test_NyContentData_getattr(self):
        """
        The __getattr__ method defined by NyContentData must be the
        __getattr__ method of all Naaya content type classes. It will do the
        right thing and invoke the next __getattr__ in the MRO (method
        resolution order).
        """
        for content_type in content_types:
            if content_type['module'] in SCHEMA_EXCEPTIONS:
                continue
            self.failUnlessEqual(content_type['_class'].__getattr__.im_func,
                NyContentData.__getattr__.im_func,
                '__getattr__ method of "%s" is wrong' % content_type['meta_type'])

class ConformanceFunctionalTestCase(NaayaFunctionalTestCase, GeoPointMixin, ExFileMixin, MediaFileMixin, ContactMixin):
    """
    Test all content types to make sure they all do certain things
    """

    def afterSetUp(self):
        self.geopoint_install()
        self.exfile_install()
        self.mediafile_install()
        self.contact_install()
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'xz_folder', contributor='contributor', submitted=1)
        self.portal.switch_language = 1
        self.portal.gl_add_site_language('fr')
        transaction.commit()
        self.browser_do_login('admin', '')

    def beforeTearDown(self):
        self.browser_do_logout()
        self.portal.gl_del_site_languages(['fr'])
        self.portal.switch_language = 0
        self.portal.manage_delObjects(['xz_folder'])
        self.contact_uninstall()
        self.mediafile_uninstall()
        self.exfile_uninstall()
        self.geopoint_uninstall()
        transaction.commit()

    def test_new_schema_property(self):
        """
        Check that we can add a new schema property and have
        it editable and visible end-to-end for each content type
        """
        n = 1

        for content_type in content_types:
            if content_type['module'] in SCHEMA_EXCEPTIONS:
                continue

            type_name = content_type['module']
            schema = self.portal.portal_schemas.getSchemaForMetatype(content_type['meta_type'])
            schema.addWidget('xzzx', sortorder=200, widget_type='String', label='zxxz')
            transaction.commit()

            # add an object
            self.browser.go('http://localhost/portal/xz_folder/%s' % content_type['addform'])
            form = self.browser.get_form('frmAdd')
            self.failUnless('xzzx:utf8:ustring' in (c.name for c in form.controls),
                'missing "xzzx" control for %s when adding' % type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            form['title:utf8:ustring'] = 'some title %d' % n
            form['xzzx:utf8:ustring'] = 'the XzZx one true value'
            self._fill_specific_form_fields(form, type_name)
            self.browser.submit()

            # make sure the value was set
            obj = self.portal.xz_folder['some-title-%d' % n]
            self.failUnlessEqual(getattr(obj, 'xzzx', None), 'the XzZx one true value',
                'bad/missing "xzzx" value for %s' % type_name)

            # edit the object
            self.browser.go('http://localhost/portal/xz_folder/some-title-%d/edit_html' % n)
            form = self.browser.get_form('frmEdit')
            self.failUnless('xzzx:utf8:ustring' in (c.name for c in form.controls),
                'missing "xzzx" control for %s when editing' % type_name)
            self.browser.clicked(form, form.find_control('saveProperties:method'))
            self.failUnlessEqual(form['xzzx:utf8:ustring'], 'the XzZx one true value',
                'bad "xzzx" value in edit form for %s' % type_name)
            form['xzzx:utf8:ustring'] = 'the XzZx other true value'
            self.browser.submit()

            # make sure the value was changed
            obj = self.portal.xz_folder['some-title-%d' % n]
            self.failUnlessEqual(getattr(obj, 'xzzx', None), 'the XzZx other true value',
                'bad/missing "xzzx" 2nd value for %s' % type_name)

            # clean up
            self.portal.xz_folder.manage_delObjects(['some-title-%d' % n])
            schema = self.portal.portal_schemas.getSchemaForMetatype(content_type['meta_type'])
            schema.manage_delObjects(['xzzx-property'])
            transaction.commit()
            n += 1

    def _fill_specific_form_fields(self, form, type_name):
        if type_name == 'NyURL':
            form['redirect:boolean'] = []
        elif type_name == 'NyGeoPoint':
            form['geo_location.lon:utf8:ustring'] = '12.587142'
            form['geo_location.lat:utf8:ustring'] = '55.681004'
        elif type_name == 'NyMediaFile':
            form.find_control('file').add_file(StringIO('the_FLV_data'),
                filename='testvid.flv', content_type='video/x-flv')

    def test_dynamic_properties(self):
        """
        Check that we can configure and set (old-style) dynamic properties
        """
        n = 1

        for content_type in content_types:
            if content_type['module'] in DYNAMIC_PROPERTIES_EXCEPTIONS:
                continue

            type_name = content_type['module']

            # create a dynamic property for this content type
            self.browser.go('http://localhost/portal/portal_dynamicproperties/'
                    '?%3Amethod=manage_addDynamicPropertiesItemForm'
                    '&submit=Add+Naaya+Dynamic+Properties+Item')

            form = self.browser.get_form(1)
            form['id'] = [ content_type['meta_type'] ]
            self.browser.clicked(form, self.browser.get_form_field(form, 'id'))
            self.browser.submit()

            self.browser.go( 'http://localhost/portal/portal_dynamicproperties/'
                '%s/manage_properties_html' % quote(content_type['meta_type']) )

            form = self.browser.get_form(1)
            form['id'] = 'yvvy'
            form['name'] = 'Yv Vy'
            form['type'] = ['string']
            self.browser.clicked(form, self.browser.get_form_field(form, 'id'))
            self.browser.submit()

            # create a new object
            self.browser.go('http://localhost/portal/xz_folder/%s' % content_type['addform'])
            form = self.browser.get_form('frmAdd')
            self.failUnless('yvvy:utf8:ustring' in (c.name for c in form.controls),
                'missing "yvvy" control for %s when adding' % type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            form['title:utf8:ustring'] = 'some title %d' % n
            form['yvvy:utf8:ustring'] = 'the yvvy value'
            self._fill_specific_form_fields(form, type_name)
            self.browser.submit()

            # make sure the value was set
            obj = self.portal.xz_folder['some-title-%d' % n]
            self.failUnlessEqual(getattr(obj, 'yvvy', None), 'the yvvy value',
                'bad/missing "yvvy" value for %s' % type_name)

            # edit the object
            self.browser.go('http://localhost/portal/xz_folder/some-title-%d/edit_html' % n)
            form = self.browser.get_form('frmEdit')
            self.failUnless('yvvy:utf8:ustring' in (c.name for c in form.controls),
                'missing "yvvy" control for %s when editing' % type_name)
            self.browser.clicked(form, form.find_control('saveProperties:method'))
            self.failUnlessEqual(form['yvvy:utf8:ustring'], 'the yvvy value',
                'bad "yvvy" value in edit form for %s' % type_name)
            form['yvvy:utf8:ustring'] = 'the yvvy other value'
            self.browser.submit()

            # make sure the value was changed
            obj = self.portal.xz_folder['some-title-%d' % n]
            self.failUnlessEqual(getattr(obj, 'yvvy', None), 'the yvvy other value',
                'bad/missing "yvvy" 2nd value for %s' % type_name)

            # delete the object, so we can create another one with the same ID later on
            self.portal.xz_folder.manage_delObjects(['some-title-%d' % n])
            transaction.commit()
            n += 1

    def test_form_remember_data(self):
        """ Make sure forms don't lose their data when they have an error """
        for content_type in content_types:
            if content_type['module'] in FORM_REMEMBER_DATA_EXCEPTIONS:
                continue

            type_name = content_type['module']

            # "create object" form
            self.browser.go('http://localhost/portal/xz_folder/%s' % content_type['addform'])
            # dont' add title, so the form generates an error
            form = self.browser.get_form('frmAdd')
            form['keywords:utf8:ustring'] = 'no save me'
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()

            html = self.browser.get_html()
            self.failUnless('frmAdd' in html)
            self.failUnless('Value required for "Title"' in html
                or 'The Title field must have a value.' in html)
            form = self.browser.get_form('frmAdd')
            self.failUnlessEqual(form['keywords:utf8:ustring'], 'no save me',
                'The "add" form did not remember our data (%s)' % type_name)

            self.failIf('test-form-title' in self.portal.xz_folder.objectIds(),
                'Object should not have been created! (%s)' % type_name)

            # create the real object so we can try editing it
            form = self.browser.get_form('frmAdd')
            form['title:utf8:ustring'] = 'test form title'
            form['keywords:utf8:ustring'] = ''
            self._fill_specific_form_fields(form, type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()

            # make sure the object was created
            ob = self.portal.xz_folder['test-form-title']
            self.failUnlessEqual(ob.meta_type, content_type['meta_type'])

            # try to edit the object, expect form errors
            self.browser.go('http://localhost/portal/xz_folder/test-form-title/edit_html')
            form = self.browser.get_form('frmEdit')
            self.failUnlessEqual(form['title:utf8:ustring'], 'test form title')
            form['title:utf8:ustring'] = ''
            form['keywords:utf8:ustring'] = 'no save me'
            self.browser.clicked(form, form.find_control('saveProperties:method'))
            self.browser.submit()

            # see if the form contains errors, and the data we just entered.
            self.failUnless('The form contains errors' in html)
            self.failUnless('Value required for "Title"' in html
                or 'The Title field must have a value.' in html)
            form = self.browser.get_form('frmEdit')
            #self.failUnlessEqual(form['keywords:utf8:ustring'], 'no save me',
            #    'The "edit" form did not remember our data (%s)' % type_name)

            self.failUnlessEqual(self.portal.xz_folder['test-form-title'].keywords, '',
                'The object\'s "keywords" value should have been empty (%s)' % type_name)

            # delete the object, so we can create another one with the same ID later on
            self.portal.xz_folder.manage_delObjects(['test-form-title'])
            transaction.commit()

    def test_translate_object(self):
        """ Make sure the translation interface works properly """
        for content_type in content_types:
            type_name = content_type['module']

            if type_name in TRANSLATE_OBJECT_EXCEPTIONS:
                continue

            # "create object" form
            self.browser.go('http://localhost/portal/xz_folder/%s' % content_type['addform'])
            form = self.browser.get_form('frmAdd')
            form['title:utf8:ustring'] = 'ze title'
            self._fill_specific_form_fields(form, type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()

            # make sure the object was created
            ob = self.portal.xz_folder['ze-title']
            self.failUnlessEqual(ob.meta_type, content_type['meta_type'])

            # try to edit the object in another language
            self.browser.go('http://localhost/portal/xz_folder/ze-title/edit_html?lang=fr')
            form = self.browser.get_form('frmEdit')
            self.failUnlessEqual(form['title:utf8:ustring'], '',
                'Unexpected value in form: "%s" (should be "") (%s)'
                    % (form['title:utf8:ustring'], type_name))
            form['title:utf8:ustring'] = 'le title'
            self.browser.clicked(form, form.find_control('saveProperties:method'))
            self.browser.submit()
            self.failIf('The form contains errors' in self.browser.get_html())

            obj = self.portal.xz_folder['ze-title']
            self.failUnlessEqual(obj.getLocalProperty('title', 'en'), 'ze title',
                'The object\'s english "title" value is wrong (%s)' % type_name)
            self.failUnlessEqual(obj.getLocalProperty('title', 'fr'), 'le title',
                'The object\'s french "title" value is wrong (%s)' % type_name)

            # do the "switch to language" operation - move content from 'en' to 'fr'
            self.browser.go('http://localhost/portal/xz_folder/ze-title/edit_html')
            form = self.browser.get_form('frmEdit')
            self.browser.clicked(form, form.find_control('switchToLanguage:method'))
            self.browser.submit()

            obj = self.portal.xz_folder['ze-title']
            self.failUnlessEqual(obj.getLocalProperty('title', 'en'), '',
                'The new english "title" value is wrong (%s)' % type_name)
            self.failUnlessEqual(obj.getLocalProperty('title', 'fr'), 'ze title',
                'The new french "title" value is wrong (%s)' % type_name)

            # delete the object, so we can create another one with the same ID later on
            self.portal.xz_folder.manage_delObjects(['ze-title'])
            transaction.commit()

    def testCatalog(self):
        """ Make sure objects get cataloged properly """
        for content_type in content_types:
            type_name = content_type['module']
            if type_name not in [ 'NyNews', 'NyStory', 'NyDocument', 'NyPointer',
                    'NyURL', 'NyEvent', 'NyFile', 'NyFolder']:
                continue
            rnd_title = 'title' + str(random())[2:8]

            self.browser.go('http://localhost/portal/xz_folder/%s' % content_type['addform'])
            form = self.browser.get_form('frmAdd')
            form['title:utf8:ustring'] = rnd_title
            self._fill_specific_form_fields(form, type_name)
            self.browser.clicked(form, form.find_control('title:utf8:ustring'))
            self.browser.submit()

            self.browser.go('http://localhost/portal/search_html?query=' + rnd_title)
            html = self.browser.get_html()
            self.failUnless('xz_folder/%s' % rnd_title in html) # we look for a hyperlink to our object

            self.portal.xz_folder.manage_delObjects([rnd_title])
            transaction.commit()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ContentTypeConformanceTestCase))
    suite.addTest(makeSuite(ConformanceFunctionalTestCase))
    return suite
