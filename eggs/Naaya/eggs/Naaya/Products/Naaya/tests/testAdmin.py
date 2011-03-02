from unittest import TestSuite, makeSuite

import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyAdminTestCase(NaayaTestCase):
    def beforeTearDown(self):
        restore_default_glossary_ids(self.portal)
        transaction.commit()

    def test_set_glossaries(self):
        def glossary_id(content_name, property_name):
            portal_schemas = self.portal['portal_schemas']
            schema = portal_schemas[content_name]
            return schema[property_name + '-property'].glossary_id

        self.assertNotEqual(glossary_id('NyDocument', 'keywords'), 'new_kwds')
        self.assertNotEqual(glossary_id('NyDocument', 'coverage'), 'new_cogv')
        self.assertNotEqual(glossary_id('NyFolder', 'keywords'), 'new_kwds')
        self.assertNotEqual(glossary_id('NyFolder', 'coverage'), 'new_cogv')

        self.portal.admin_set_glossary_ids(keywords='new_kwds',
                                           coverage='new_cogv')

        self.assertEqual(glossary_id('NyDocument', 'keywords'), 'new_kwds')
        self.assertEqual(glossary_id('NyDocument', 'coverage'), 'new_cogv')
        self.assertEqual(glossary_id('NyFolder', 'keywords'), 'new_kwds')
        self.assertEqual(glossary_id('NyFolder', 'coverage'), 'new_cogv')

def test_glossaries():
    """ mock glossaries listing """
    return [{'id': name, 'title_or_id': name}
            for name in ['new_kwds', 'new_cogv']]

class NyAdminBrowserTestCase(NaayaFunctionalTestCase):
    def afterSetUp(self):
        restore_default_glossary_ids(self.portal)
        self.portal.list_glossaries = test_glossaries
        transaction.commit()

    def beforeTearDown(self):
        del self.portal.list_glossaries
        transaction.commit()

    def test_admin_page(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/admin_glossaries_html')
        form = self.browser.get_form('glossaries')
        form['keywords'] = ['new_kwds']
        form['coverage'] = ['new_cogv']
        self.browser.clicked(form, self.browser.get_form_field(form, 'keywords'))
        self.browser.submit()

        self.assertTrue(self.browser.get_url().endswith('admin_glossaries_html'))
        form = self.browser.get_form('glossaries')
        self.assertEqual(form['keywords'], ['new_kwds'])
        self.assertEqual(form['coverage'], ['new_cogv'])

        self.browser_do_logout()

        portal_schemas = self.portal['portal_schemas']
        schema = portal_schemas['NyDocument']
        self.assertEqual(schema['keywords-property'].glossary_id, 'new_kwds')
        self.assertEqual(schema['coverage-property'].glossary_id, 'new_cogv')

def restore_default_glossary_ids(portal):
    """ restore glossary IDs to their default value """
    for schema in portal['portal_schemas'].objectValues():
        schema['keywords-property'].glossary_id = 'keywords'
        schema['coverage-property'].glossary_id = 'coverage'

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyAdminTestCase))
    suite.addTest(makeSuite(NyAdminBrowserTestCase))
    return suite
