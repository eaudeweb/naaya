from unittest import TestSuite, makeSuite
from Products.Naaya.tests import NaayaTestCase, NaayaFunctionalTestCase


class WidgetTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for Naaya Content Property Definition """

    def afterSetUp(self):
        self.portal.portal_schemas.addSchema('sch', 'Test Schema')
        self.schema = self.portal.portal_schemas.sch

    def beforeTearDown(self):
        self.portal.portal_schemas.manage_delObjects(['sch'])

    def test_add_propdef(self):
        self.schema.addWidget('mypr', label='mypr', widget_type='String')
        self.failUnless('mypr-property' in self.schema.objectIds())
        self.failUnless(self.schema.getWidget('mypr').id == 'mypr-property')
        self.failUnlessEqual(self.schema.getWidget('mypr').meta_type, 'Naaya Schema String Widget')

        for widget_name in ['String', 'Text Area', 'Date', 'Checkbox']:
            widget_id = widget_name.replace(' ', '')
            prop_name ='mypr_%s' % widget_id
            self.schema.addWidget(prop_name, label=prop_name, widget_type=widget_id)
            self.failUnlessEqual(self.schema.getWidget(prop_name).meta_type,
                'Naaya Schema %s Widget' % widget_name)

    def test_change_properties(self):
        self.schema.addWidget('mypr', label='mypr', widget_type='String')
        mypr = self.schema.getWidget('mypr')

        properties = dict( (p['id'], p) for p in mypr._properties )
        self.failUnless('localized' in properties)
        self.failUnlessEqual(properties['localized']['type'], 'boolean')
        self.failUnlessEqual(properties['data_type']['type'], 'string')
        self.failUnlessEqual(properties['visible']['type'], 'boolean')

        self.failUnlessEqual(mypr.required, False)
        self.failUnlessEqual(mypr.localized, False)
        self.failUnlessEqual(type(mypr.localized), bool)

        # TODO: test change label
        mypr.manage_changeProperties(required='True', localized='True')

        self.failUnlessEqual(mypr.required, True)
        self.failUnlessEqual(mypr.localized, True)

class WidgetDefaultDefinitionTestCase(NaayaTestCase.NaayaTestCase):
    """ testing code that queries the default definition of a property """

    def afterSetUp(self):
        self.doc_schema = self.portal.portal_schemas.NyDocument
        self.doc_schema.addWidget('newpr', label='newpr', widget_type='String')

    def beforeTearDown(self):
        self.doc_schema.manage_delObjects(['newpr-property'])

    def test_get_default_definition(self):
        sortorder = self.doc_schema.getWidget('sortorder')
        keywords = self.doc_schema.getWidget('keywords')
        newpr = self.doc_schema.getWidget('newpr')
        from Products.NaayaBase.NyContentType import NY_CONTENT_BASE_SCHEMA
        self.failUnless(sortorder.get_default_definition() is NY_CONTENT_BASE_SCHEMA['sortorder'])
        self.failUnless(keywords.get_default_definition() is NY_CONTENT_BASE_SCHEMA['keywords'])
        self.failUnless(newpr.get_default_definition() is None)

    def test_mandatory_property(self):
        sortorder = self.doc_schema.getWidget('sortorder')
        keywords = self.doc_schema.getWidget('keywords')
        newpr = self.doc_schema.getWidget('newpr')

        def set_required(widget, required):
            widget.saveProperties(title=widget.title, visible=widget.visible,
                sortorder=widget.sortorder, required=required)

        self.failUnlessRaises(ValueError, set_required, sortorder, False)
        try: set_required(keywords, False)
        except: self.fail('making "keywords" non-mandatory should be possible')
        try: set_required(newpr, False)
        except: self.fail('making "newpr" non-mandatory should be possible')


class WidgetFunctionalTestCase(NaayaFunctionalTestCase.NaayaFunctionalTestCase):
    """ Functional TestCase for Naaya Content Property Definition """

    def afterSetUp(self):
        self.browser.creds.add_password('Zope2', 'http://localhost/', 'admin', '')
