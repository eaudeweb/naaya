from os import path
import transaction
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.LayoutTool.Template import manage_addTemplate

class CustomTemplateTest(NaayaFunctionalTestCase):
    def test_customize_function(self):
        url_schema = self.portal['portal_schemas']['NyURL']
        title_widget = url_schema['title-property']
        title_widget.custom_template = 'portal_forms/widget_tempate_for_test'
        title_widget.manage_create_custom_template()

        portal_forms = self.portal['portal_forms']
        assert 'widget_tempate_for_test' in portal_forms.objectIds()

        orig_zpt = open(path.join(path.dirname(__file__), '..', 'zpt',
                                  'property_widget_string.zpt'), 'rb')
        orig_zpt_text = orig_zpt.read()
        orig_zpt.close()

        self.assertEqual(portal_forms['widget_tempate_for_test']._text.strip(),
                         orig_zpt_text.strip())

    def _set_custom_tmpl(self):
        url_schema = self.portal['portal_schemas']['NyURL']
        title_widget = url_schema['title-property']
        title_widget.custom_template = 'portal_forms/widget_tempate_for_test'
        portal_forms = self.portal['portal_forms']
        manage_addTemplate(portal_forms, 'widget_tempate_for_test')
        tmpl = portal_forms['widget_tempate_for_test']
        custom_tmpl = ('<tal:block content="string:[[[['
                           'path ${here/getPhysicalPath},'
                           'ctxpath ${options/context/getPhysicalPath},'
                           'value ${options/value|nothing},'
                           'errors ${options/errors},'
                           'prop_id ${here/prop_name},'
                       ']]]]" />')
        tmpl.pt_edit(custom_tmpl, 'text/html')

    def test_custom_tmpl_add(self):
        self._set_custom_tmpl()
        transaction.commit()

        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/info/url_add_html')
        correct_value = (
            "[[[["
            "path ('', 'portal', 'portal_schemas', 'NyURL', 'title-property'),"
            "ctxpath ('', 'portal', 'info'),"
            "value ,"
            "errors None,"
            "prop_id title,"
            "]]]]")
        assert correct_value in self.browser.get_html()

    def test_custom_tmpl_edit(self):
        from naaya.content.url.url_item import addNyURL
        addNyURL(self.portal['info'], id='test_url', title="Teh URLz",
                 sortorder=100)
        self._set_custom_tmpl()
        transaction.commit()

        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/info/test_url/edit_html')
        correct_value = (
            "[[[["
            "path ('', 'portal', 'portal_schemas', 'NyURL', 'title-property'),"
            "ctxpath ('', 'portal', 'info', 'test_url'),"
            "value Teh URLz,"
            "errors None,"
            "prop_id title,"
            "]]]]")
        assert correct_value in self.browser.get_html(), self.browser.get_html()
