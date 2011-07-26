from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class TestPluginsTool(NaayaTestCase):
    """ unittests for plugins_tool """
    def test_get_plugins(self):
        """ Get a list of plugins """
        expected =         [{
            'doc': ' Plugin for User Folder ',
            'name': 'plugUserFolder',
            'object_type': 'User Folder'
        }, {
            'doc': ' Plugin for LDAPUserFolder ',
            'name': 'plugLDAPUserFolder',
            'object_type': 'LDAPUserFolder'
        }]
        self.assertEqual(self.portal.acl_users.getPluginsInfo(), expected)

    def test_get_plugin_instance(self):
        """ Return a instance of a specific plugin """
        acl_users = self.portal.acl_users
        root_acl_users = self.portal.aq_parent.acl_users
        plugin_class = acl_users.getPluginFactory(root_acl_users.meta_type)
        plugin_instance = plugin_class(1, root_acl_users, '')
        self.assertEqual(plugin_instance.object_type, root_acl_users.meta_type)

class TestFunctionalPluginsTool(NaayaFunctionalTestCase):
    """ Functional tests for plugins_tool """

    def test_add_source(self):
        """ Add a plugUserFolder source."""

        self.browser_do_login('admin', '')
        self.browser.go(self.portal.absolute_url() +
                    '/acl_users/manage_sources_html')
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, 'source_path')
        self.browser.clicked(form, field)
        form['title'] = 'Test source'
        form['source_path'] = ['acl_users']
        self.browser.submit()
        self.assertTrue('Test source' in self.browser.get_html())
