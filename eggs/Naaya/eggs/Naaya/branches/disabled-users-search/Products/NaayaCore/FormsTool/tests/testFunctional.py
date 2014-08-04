from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

class TestFormsTool(NaayaFunctionalTestCase):
    def afterSetUp(self):
        self.browser_do_login('admin', '')
        NaayaPageTemplateFile('the_template', globals(), 'tpl1')
        NaayaPageTemplateFile('the_template', globals(), 'tpl2')

    def test_overview(self):
        """ manage_overview template """
        forms_tool = self.portal.getFormsTool()
        self.browser.go(forms_tool.absolute_url() + '/manage_overview')
        self.assertTrue('tpl1' in self.browser.get_html())

    def test_customize(self):
        """ customization template """
        forms_tool = self.portal.getFormsTool()
        self.browser.go(forms_tool.absolute_url() +
                    '/manage_customize?name=tpl2')
        self.assertTrue('[physicalpath:' in self.browser.get_html())

    def test_customizeForm(self):
        """ submit customized template """
        forms_tool = self.portal.getFormsTool()
        self.browser.go(forms_tool.absolute_url() +
                 '/manage_customize?name=tpl2')
        self.browser.submit()
        #form submited test if we have a customized form
        self.assertTrue('tpl2' in forms_tool.objectIds())

    def test_diff(self):
        """ test for html_diff """

        forms_tool = self.portal.getFormsTool()
        forms_tool.manage_customizeForm('tpl1')
        forms_tool.getForm('tpl1').pt_edit(text='aaaa',
                content_type='text/html')
        import transaction; transaction.commit()
        self.browser.go(forms_tool.absolute_url() + '/show_diff?name=tpl1')
        html = self.browser.get_html()
        self.assertTrue('-[physicalpath:' in html)
        self.assertTrue('+aaaa' in html)



