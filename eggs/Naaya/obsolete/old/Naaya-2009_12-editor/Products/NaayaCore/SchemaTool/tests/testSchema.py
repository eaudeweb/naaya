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

from DateTime import DateTime
from Testing import ZopeTestCase
from Products.Naaya.tests import NaayaTestCase, NaayaFunctionalTestCase

from Products.NaayaCore.SchemaTool.Schema import Schema

class SchemaUnitTestCase(ZopeTestCase.TestCase):
    """ Unit tests for Naaya Schema Tool """
    def afterSetUp(self):
        schema = Schema(id='my_schema', title='my_schema')
        self.schema = schema
        # patch the schema instance so we can add widgets
        schema.gl_get_selected_language = lambda: 'en'
        schema.gl_add_languages = lambda a: None
        schema.addWidget('my_str', widget_type='String')
        schema.addWidget('my_local_str', widget_type='String', localized=True)
        schema._getOb('my_str-property').required = True
        schema.addWidget('my_date', widget_type='Date', data_type='date')

    def beforeTearDown(self):
        del self.schema

    def test_form_parsing_ok(self):
        form = {'my_str': 'some value'}
        form_data, form_errors = self.schema.processForm(form)
        self.failUnlessEqual(form_data['my_str'], 'some value')
        self.failIf('my_str' in form_errors)

    def test_form_parsing_error(self):
        form = {'my_str': ''}
        form_data, form_errors = self.schema.processForm(form)
        self.failUnlessEqual(form_data['my_str'], '')
        self.failUnlessEqual(len(form_errors['my_str']), 1)

    def test_form_parsing_value_types(self):
        form = {'my_date': '13/02/2009'}
        form_data, form_errors = self.schema.processForm(form)
        self.failUnlessEqual(form_data['my_date'], DateTime(2009, 02, 13))

    def test_list_localiezd_properties(self):
        self.failUnlessEqual(self.schema.listPropNames(local=True), set(['my_local_str']))
        self.schema.getWidget('my_str').localized = True
        self.failUnlessEqual(self.schema.listPropNames(local=True), set(['my_str', 'my_local_str']))

    def test_data_type(self):
        schema = self.schema
        formats = {
            'int': {'input': '13', 'expected': 13},
            'str': {'input': 'something', 'expected': u'something'},
            'float': {'input': '3', 'expected': 3.0},
            'bool': {'input': 'non-empty-string', 'expected': True},
            'date': {'input': '13/02/2009', 'expected': DateTime(2009, 02, 13)},
        }
        for the_format, data in formats.iteritems():
            field_name = 'my_format_%s' % the_format
            schema.addWidget(field_name, widget_type='String', data_type=the_format)
            expected = data['expected']

            form = {field_name: data['input']}
            form_data, form_errors = self.schema.processForm(form)
            self.failIf(field_name in form_errors)

            output = form_data[field_name]
            self.failUnlessEqual( type(output), type(expected),
                'Bad output type for data_type=%s: expected %s, found %s'
                % (the_format, type(output), type(expected)) )
            self.failUnlessEqual(output, expected)

        # make sure we're not allowed to set an invalid data_type
        self.failUnlessRaises(ValueError, lambda: schema.addWidget(
            'my_bad_field', widget_type='String', data_type='nonesuch'))


class SchemaTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Schema Tool """

    def test_add_schema(self):
        self.portal.portal_schemas.addSchema('tst', 'Test Schema')
        tst = self.portal.portal_schemas.tst
        self.failUnlessEqual(tst.title, 'Test Schema')

    def test_populate_initial_schema(self):
        content_type_def = {
            'title': dict(widget_type='String', validator='non_empty'),
            'description': dict(widget_type='TextArea', validator=None),
            'sortorder': dict(widget_type='String', validator='positive_int'),
            'releasedate': dict(widget_type='Date', validator='datetime'),
        }
        # TODO: validator is ignored
        self.portal.portal_schemas.addSchema('schema1')
        schema1 = self.portal.portal_schemas.schema1
        schema1.populateSchema(content_type_def)

        self.failUnless('title-property' in schema1.objectIds())
        self.failUnlessEqual(schema1.getWidget('title').meta_type, 'Naaya Schema String Widget')
        self.failUnless('description-property' in schema1.objectIds())
        self.failUnlessEqual(schema1.getWidget('description').meta_type, 'Naaya Schema Text Area Widget')
        self.failUnless('sortorder-property' in schema1.objectIds())
        self.failUnlessEqual(schema1.getWidget('sortorder').meta_type, 'Naaya Schema String Widget')
        self.failUnless('releasedate-property' in schema1.objectIds())
        self.failUnlessEqual(schema1.getWidget('releasedate').meta_type, 'Naaya Schema Date Widget')

        # check if lookup of non-existent properties fails gracefully
        self.failUnlessRaises(KeyError, schema1.getWidget, 'no_such_prop')

        # populate() should not allow more than one call
        self.failUnlessRaises(ValueError, schema1.populateSchema, {})

    def test_list_widgets(self):
        schema = self.portal.portal_schemas.getSchemaForMetatype('Naaya Document')
        self.failUnlessEqual(
            [ widget.prop_name() for widget in schema.listWidgets() ],
            ['title', 'description', 'geo_location', 'geo_type', 'coverage', 'keywords',
                'sortorder', 'releasedate', 'discussion', 'body'])

    def test_list_local_properties(self):
        schema = self.portal.portal_schemas.getSchemaForMetatype('Naaya Document')
        self.failUnlessEqual(schema.listPropNames(local=True),
            set(['title', 'description', 'coverage', 'keywords', 'body']))

    def test_NyDocument_initial_schema(self):
        self.failUnless('NyDocument' in self.portal.portal_schemas.objectIds())
        schema = self.portal.portal_schemas.NyDocument

        self.failUnless('title-property' in schema.objectIds())
        pr_title = schema.getWidget('title')
        self.failUnlessEqual(pr_title.required, True)
        self.failUnlessEqual(pr_title.localized, True)
        self.failUnlessEqual(pr_title.title, 'Title')
        self.failUnlessEqual(pr_title.meta_type, 'Naaya Schema String Widget')

        self.failUnless('description-property' in schema.objectIds())
        pr_description = schema.getWidget('description')
        self.failUnlessEqual(pr_description.required, False)
        self.failUnlessEqual(pr_description.localized, True)
        self.failUnlessEqual(pr_description.meta_type, 'Naaya Schema Text Area Widget')

        self.failUnless('coverage-property' in schema.objectIds())
        pr_coverage = schema.getWidget('coverage')
        self.failUnlessEqual(pr_coverage.required, False)
        self.failUnlessEqual(pr_coverage.localized, True)
        self.failUnlessEqual(pr_coverage.title, 'Geographical coverage')
        self.failUnlessEqual(pr_coverage.meta_type, 'Naaya Schema Glossary Widget')

        self.failUnless('keywords-property' in schema.objectIds())
        pr_keywords = schema.getWidget('keywords')
        self.failUnlessEqual(pr_keywords.required, False)
        self.failUnlessEqual(pr_keywords.localized, True)
        self.failUnlessEqual(pr_keywords.title, 'Keywords')
        self.failUnlessEqual(pr_keywords.meta_type, 'Naaya Schema Glossary Widget')

        self.failUnless('sortorder-property' in schema.objectIds())
        pr_sortorder = schema.getWidget('sortorder')
        self.failUnlessEqual(pr_sortorder.required, True)
        self.failUnlessEqual(pr_sortorder.localized, False)
        self.failUnlessEqual(pr_sortorder.title, 'Sort order')
        self.failUnlessEqual(pr_sortorder.meta_type, 'Naaya Schema String Widget')

        self.failUnless('releasedate-property' in schema.objectIds())
        pr_releasedate = schema.getWidget('releasedate')
        self.failUnlessEqual(pr_releasedate.required, True)
        self.failUnlessEqual(pr_releasedate.localized, False)
        self.failUnlessEqual(pr_releasedate.title, 'Release date')
        self.failUnlessEqual(pr_releasedate.meta_type, 'Naaya Schema Date Widget')

        self.failUnless('discussion-property' in schema.objectIds())
        pr_discussion = schema.getWidget('discussion')
        self.failUnlessEqual(pr_discussion.required, False)
        self.failUnlessEqual(pr_discussion.localized, False)
        self.failUnlessEqual(pr_discussion.title, 'Open for comments')
        self.failUnlessEqual(pr_discussion.meta_type, 'Naaya Schema Checkbox Widget')

        self.failUnless('body-property' in schema.objectIds())
        pr_body = schema.getWidget('body')
        self.failUnlessEqual(pr_body.required, False)
        self.failUnlessEqual(pr_body.localized, True)
        self.failUnlessEqual(pr_body.title, 'Body (HTML)')
        self.failUnlessEqual(pr_body.meta_type, 'Naaya Schema Text Area Widget')

    def test_tinymce(self):
        self.portal.portal_schemas.addSchema('tinymce_tst', 'TinyMCE Test Schema')
        schema = self.portal.portal_schemas.tinymce_tst

        def form():
            return ''.join(widget.render_html('') for widget in schema.listWidgets())

        schema.addWidget('my_textarea', widget_type='TextArea')
        self.failUnless('TinyMCE' not in form())

        schema.addWidget('my_html_textarea', widget_type='TextArea', tinymce=True)
        self.failUnless('tinyMCE.init' in form())

    def test_prop_details(self):
        doc = self.portal.info.contact
        output = doc.prop_details('title')
        self.failUnlessEqual(output, {'label':'Title',
            'value':'Contact us', 'visible':True, 'show':True})

class SchemaFunctionalTestCase(NaayaFunctionalTestCase.NaayaFunctionalTestCase):
    """ Functional TestCase for Naaya Schema Tool """

    def afterSetUp(self):
        #self.browser.creds.add_password('Zope2', 'http://localhost/', 'admin', '')
        self.browser_do_login('admin', '')

    def beforeTearDown(self):
        self.browser_do_logout()

    def test_edit_form(self):
        self.browser.go('http://localhost/portal/info/contact/edit_html')
        form = self.browser.get_form('frmEdit')

        # check if the initial data in the form is ok
        self.failUnlessEqual(form['title:utf8:ustring'], 'Contact us')
        self.failUnless('This page should contain' in form['body:utf8:ustring'])

        # do some editing
        form['title:utf8:ustring'] = 'new title'
        form['body:utf8:ustring'] = 'new body'
        form['discussion:boolean'] = False
        form['releasedate'] = '13/02/2009'
        # generate a 'click' event so the browser knows what form we want to submit
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        self.browser.submit()

        # check if the changes were saved
        contact = self.portal.info.contact
        self.failUnlessEqual(contact.title, 'new title')
        self.failUnlessEqual(contact.body, 'new body')
        self.failUnlessEqual(contact.discussion, False)
        self.failUnlessEqual(contact.releasedate, DateTime(2009, 02, 13))

    def test_hidden_property(self):
        import transaction
        self.portal.portal_schemas.NyDocument.getWidget('discussion').visible = False
        transaction.commit()
        self.browser.go('http://localhost/portal/info/contact/edit_html')
        form = self.browser.get_form('frmEdit')
        control = form.find_control('discussion:utf8:ustring')
        self.failUnlessEqual(control.type, 'hidden')
        self.portal.portal_schemas.NyDocument.getWidget('discussion').visible = True
        transaction.commit()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(SchemaUnitTestCase))
    suite.addTest(makeSuite(SchemaTestCase))
    suite.addTest(makeSuite(SchemaFunctionalTestCase))
    return suite
