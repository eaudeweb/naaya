from unittest import TestSuite, TestLoader
import transaction
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
        self.assertEqual(form_data['my_str'], 'some value')
        self.assertFalse('my_str' in form_errors)

    def test_form_parsing_error(self):
        form = {'my_str': ''}
        form_data, form_errors = self.schema.processForm(form)
        self.assertEqual(form_data['my_str'], '')
        self.assertEqual(len(form_errors['my_str']), 1)

    def test_form_parsing_value_types(self):
        form = {'my_date': '13/02/2009'}
        form_data, form_errors = self.schema.processForm(form)
        self.assertEqual(form_data['my_date'], DateTime(2009, 2, 13))

    def test_list_localiezd_properties(self):
        self.assertEqual(self.schema.listPropNames(local=True), set(['my_local_str']))
        self.schema.getWidget('my_str').localized = True
        self.assertEqual(self.schema.listPropNames(local=True), set(['my_str', 'my_local_str']))

    def test_data_type(self):
        schema = self.schema
        formats = {
            'int': {'input': '13', 'expected': 13},
            'str': {'input': 'something', 'expected': u'something'},
            'float': {'input': '3', 'expected': 3.0},
            'bool': {'input': 'non-empty-string', 'expected': True},
            'date': {'input': '13/02/2009', 'expected': DateTime(2009, 2, 13)},
        }
        for the_format, data in formats.items():
            field_name = 'my_format_%s' % the_format
            schema.addWidget(field_name, widget_type='String', data_type=the_format)
            expected = data['expected']

            form = {field_name: data['input']}
            form_data, form_errors = self.schema.processForm(form)
            self.assertFalse(field_name in form_errors)

            output = form_data[field_name]
            self.assertEqual( type(output), type(expected),
                'Bad output type for data_type=%s: expected %s, found %s'
                % (the_format, type(output), type(expected)) )
            self.assertEqual(output, expected)

        # make sure we're not allowed to set an invalid data_type
        self.assertRaises(ValueError, lambda: schema.addWidget(
            'my_bad_field', widget_type='String', data_type='nonesuch'))


class SchemaTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Schema Tool """

    def test_add_schema(self):
        self.portal.portal_schemas.addSchema('tst', 'Test Schema')
        tst = self.portal.portal_schemas.tst
        self.assertEqual(tst.title, 'Test Schema')

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

        self.assertTrue('title-property' in schema1.objectIds())
        self.assertEqual(schema1.getWidget('title').meta_type, 'Naaya Schema String Widget')
        self.assertTrue('description-property' in schema1.objectIds())
        self.assertEqual(schema1.getWidget('description').meta_type, 'Naaya Schema Text Area Widget')
        self.assertTrue('sortorder-property' in schema1.objectIds())
        self.assertEqual(schema1.getWidget('sortorder').meta_type, 'Naaya Schema String Widget')
        self.assertTrue('releasedate-property' in schema1.objectIds())
        self.assertEqual(schema1.getWidget('releasedate').meta_type, 'Naaya Schema Date Widget')

        # check if lookup of non-existent properties fails gracefully
        self.assertRaises(KeyError, schema1.getWidget, 'no_such_prop')

        # populate() should not allow more than one call
        self.assertRaises(ValueError, schema1.populateSchema, {})

    def test_list_widgets(self):
        schema = self.portal.portal_schemas.getSchemaForMetatype('Naaya Document')
        self.assertEqual(
            [ widget.prop_name() for widget in schema.listWidgets() ],
            ['title', 'description', 'geo_location', 'geo_type', 'coverage',
                'keywords', 'sortorder', 'releasedate', 'discussion', 'body'])

    def test_list_local_properties(self):
        schema = self.portal.portal_schemas.getSchemaForMetatype('Naaya Document')
        self.assertEqual(schema.listPropNames(local=True),
            set(['title', 'description', 'coverage', 'keywords', 'body']))

    def test_NyDocument_initial_schema(self):
        self.assertTrue('NyDocument' in self.portal.portal_schemas.objectIds())
        schema = self.portal.portal_schemas.NyDocument

        self.assertTrue('title-property' in schema.objectIds())
        pr_title = schema.getWidget('title')
        self.assertEqual(pr_title.required, True)
        self.assertEqual(pr_title.localized, True)
        self.assertEqual(pr_title.title, 'Title')
        self.assertEqual(pr_title.meta_type, 'Naaya Schema String Widget')

        self.assertTrue('description-property' in schema.objectIds())
        pr_description = schema.getWidget('description')
        self.assertEqual(pr_description.required, False)
        self.assertEqual(pr_description.localized, True)
        self.assertEqual(pr_description.meta_type, 'Naaya Schema Text Area Widget')

        self.assertTrue('coverage-property' in schema.objectIds())
        pr_coverage = schema.getWidget('coverage')
        self.assertEqual(pr_coverage.required, False)
        self.assertEqual(pr_coverage.localized, True)
        self.assertEqual(pr_coverage.title, 'Geographical coverage')
        self.assertEqual(pr_coverage.meta_type, 'Naaya Schema Glossary Widget')

        self.assertTrue('keywords-property' in schema.objectIds())
        pr_keywords = schema.getWidget('keywords')
        self.assertEqual(pr_keywords.required, False)
        self.assertEqual(pr_keywords.localized, True)
        self.assertEqual(pr_keywords.title, 'Keywords')
        self.assertEqual(pr_keywords.meta_type, 'Naaya Schema Glossary Widget')

        self.assertTrue('sortorder-property' in schema.objectIds())
        pr_sortorder = schema.getWidget('sortorder')
        self.assertEqual(pr_sortorder.required, True)
        self.assertEqual(pr_sortorder.localized, False)
        self.assertEqual(pr_sortorder.title, 'Sort order')
        self.assertEqual(pr_sortorder.meta_type, 'Naaya Schema String Widget')

        self.assertTrue('releasedate-property' in schema.objectIds())
        pr_releasedate = schema.getWidget('releasedate')
        self.assertEqual(pr_releasedate.required, True)
        self.assertEqual(pr_releasedate.localized, False)
        self.assertEqual(pr_releasedate.title, 'Release date')
        self.assertEqual(pr_releasedate.meta_type, 'Naaya Schema Date Widget')

        self.assertTrue('discussion-property' in schema.objectIds())
        pr_discussion = schema.getWidget('discussion')
        self.assertEqual(pr_discussion.required, False)
        self.assertEqual(pr_discussion.localized, False)
        self.assertEqual(pr_discussion.title, 'Open for comments')
        self.assertEqual(pr_discussion.meta_type, 'Naaya Schema Checkbox Widget')

        self.assertTrue('body-property' in schema.objectIds())
        pr_body = schema.getWidget('body')
        self.assertEqual(pr_body.required, False)
        self.assertEqual(pr_body.localized, True)
        self.assertEqual(pr_body.title, 'Body (HTML)')
        self.assertEqual(pr_body.meta_type, 'Naaya Schema Text Area Widget')

    def test_tinymce(self):
        self.portal.portal_schemas.addSchema('tinymce_tst', 'TinyMCE Test Schema')
        schema = self.portal.portal_schemas.tinymce_tst

        def form():
            return ''.join(widget.render_html('') for widget in schema.listWidgets())

        schema.addWidget('my_textarea', widget_type='TextArea')
        self.assertTrue('TinyMCE' not in form())

        schema.addWidget('my_html_textarea', widget_type='TextArea', tinymce=True)
        self.assertTrue('tinymce(' in form())

    def test_prop_details(self):
        doc = self.portal.info.contact
        output = doc.prop_details('title')
        self.assertEqual(output, {'label':'Title',
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
        self.assertEqual(form['title:utf8:string'], 'Contact us')
        self.assertTrue('This page should contain' in form['body:utf8:string'])

        # do some editing
        form['title:utf8:string'] = 'new title'
        form['body:utf8:string'] = 'new body'
        form['discussion:boolean'] = False
        form['releasedate'] = '13/02/2009'
        # generate a 'click' event so the browser knows what form we want to submit
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        self.browser.submit()

        # check if the changes were saved
        contact = self.portal.info.contact
        self.assertEqual(contact.title, 'new title')
        self.assertEqual(contact.body, 'new body')
        self.assertEqual(contact.discussion, False)
        self.assertEqual(contact.releasedate, DateTime(2009, 2, 13))

    def test_multipleselect_widget(self):
        #https://svn.eionet.europa.eu/projects/Naaya/ticket/400
        from Products.NaayaCore.PortletsTool.RefTree import manage_addRefTree
        from Products.NaayaCore.PortletsTool.RefTreeNode import manage_addRefTreeNode
        from Products.Naaya.NyFolder import addNyFolder

        #add reftree
        portlets_tool = self.portal.getPortletsTool()
        manage_addRefTree(portlets_tool, 'theme', 'Theme', 'Theme description', 'en')
        manage_addRefTreeNode(portlets_tool.theme, 'node1', 'Node 1', lang="en")
        manage_addRefTreeNode(portlets_tool.theme, 'node2', 'Node 2', lang='en')

        #add new widget
        schema = self.portal.portal_schemas.NyEvent
        schema.addWidget('theme', widget_type='SelectMultiple', data_type='list', visible = True, list_id = 'theme')

        #add folder
        addNyFolder(self.portal, 'myfolder', contributor='admin', submitted=1)
        transaction.commit()

        #go to event add page
        self.browser.go('http://localhost/portal/myfolder/event_add_html')
        form = self.browser.get_form('frmAdd')

        #check widget values
        field = self.browser.get_form_field(form, 'theme:utf8:string:list')
        self.assertEqual(field.items[0].name, 'node1')
        self.assertEqual(len(field.items), 2)   #we have 2 nodes in theme reftree

        #add event metadata but omit to fill in values for our widget
        form['title:utf8:string'] = 'test_event'
        form['description:utf8:string'] = 'test_event_description'
        form['coverage:utf8:string'] = 'test_event_coverage'
        form['keywords:utf8:string'] = 'keyw1, keyw2'
        form['details:utf8:string'] = 'test_event_details'
        form['start_date'] = '10/10/2000'
        # generate a 'click' event so the browser knows what form we want to submit
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        self.browser.submit()

        # check if the changes were saved correctly
        event = self.portal.myfolder.test_event
        self.assertEqual(event.title, 'test_event')
        self.assertEqual(event.theme, [])

    def test_hidden_property(self):
        self.portal.portal_schemas.NyDocument.getWidget('discussion').visible = False
        self.portal.info.contact.discussion = 1
        transaction.commit()
        self.browser.go('http://localhost/portal/info/contact/edit_html')
        form = self.browser.get_form('frmEdit')
        control = form.find_control('discussion:boolean')
        self.assertEqual(control.type, 'hidden')
        self.portal.portal_schemas.NyDocument.getWidget('discussion').visible = True
        self.portal.info.contact.discussion = 0
        transaction.commit()
