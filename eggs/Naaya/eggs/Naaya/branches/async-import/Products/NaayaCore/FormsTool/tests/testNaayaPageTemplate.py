from Products.Naaya.tests import NaayaTestCase
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

from naaya.content.document import NyDocument

class NaayaTemplateTestCase(NaayaTestCase.NaayaTestCase):
    def afterSetUp(self):
        self.my_tmpl = NaayaPageTemplateFile('the_template', globals(),
                'my_tmpl')
        self.second_tmpl = NaayaPageTemplateFile('the_template', globals(),
                'second_tmpl')

        NyDocument.my_tmpl = self.my_tmpl
        NyDocument.second_tmpl = self.second_tmpl

    def beforeTearDown(self):
        del NyDocument.my_tmpl
        del NyDocument.second_tmpl

    def test_render(self):
        """ Render templates by calling the template """
        output = self.my_tmpl.__of__(self.portal)(a="26")
        self.assertTrue('[physicalpath: /portal]' in output)
        self.assertTrue('[optiona: 26]' in output)

        output = self.portal.info.contact.my_tmpl(a="13")
        self.assertTrue('[physicalpath: /portal/info/contact]' in output)
        self.assertTrue('[optiona: 13]' in output)

    def test_get_content(self):
        """ Test getContent """
        forms_tool = self.portal.portal_forms
        forms_tool.manage_customizeForm('my_tmpl')
        forms_tool.my_tmpl.pt_edit(text='<tal:block replace="a" />',
                content_type='text/html')
        output = forms_tool.getContent({'a': 26 }, 'my_tmpl')
        self.assertTrue('26' in output)

    def test_customized_templates(self):
        forms_tool = self.portal.portal_forms
        forms_tool.manage_customizeForm('my_tmpl')
        self.assertTrue('my_tmpl' in forms_tool.customized_templates())

    def test_customize(self):
        forms_tool = self.portal.portal_forms
        self.assertTrue('my_tmpl' in dict(forms_tool.get_all_templates()))
        my_tmpl_aq = forms_tool.getForm('my_tmpl')
        self.assertTrue(my_tmpl_aq.aq_self is NyDocument.my_tmpl)
        self.assertTrue(my_tmpl_aq.aq_parent is forms_tool)

        forms_tool.manage_customizeForm('my_tmpl')
        forms_tool.my_tmpl.pt_edit(text='new content', content_type='text/html')
        self.assertEqual(self.portal.info.contact.my_tmpl().strip(),
                         'new content')

    def test_template_traversal(self):
        forms_tool = self.portal.getFormsTool()

        # Customize 2nd template to include a macro def
        second_tmpl = forms_tool.getForm('second_tmpl')
        self.assertEqual(second_tmpl, forms_tool.getForm('second_tmpl'))
        forms_tool.manage_customizeForm('second_tmpl')
        text = ('<metal:block define-macro="hole">'
                'Bugs Bunny</metal:block>')
        forms_tool.second_tmpl.pt_edit(text=text, content_type='text/html')

        # Customize 1st template to include previous macro in several ways
        forms_tool.manage_customizeForm('my_tmpl')
        text = ('<tal:block metal:use-macro="'
                "python:here.getFormsTool().getForm('second_tmpl')"
                ".macros['hole']\"></tal:block>")
        forms_tool.my_tmpl.pt_edit(text=text, content_type='text/html')
        output =self.my_tmpl.__of__(self.portal)()
        self.assertTrue(output.find("Bugs Bunny")>-1)

        text = ('<tal:block metal:use-macro="'
                "python:here.getFormsTool()['second_tmpl']"
                ".macros['hole']\"></tal:block>")
        forms_tool.my_tmpl.pt_edit(text=text, content_type='text/html')
        output = self.my_tmpl.__of__(self.portal)()
        self.assertTrue(output.find("Bugs Bunny")>-1)

        text = ('<tal:block metal:use-macro="'
                "here/portal_forms/second_tmpl/"
                "macros/hole\"></tal:block>")
        forms_tool.my_tmpl.pt_edit(text=text, content_type='text/html')
        output = self.my_tmpl.__of__(self.portal)()
        self.assertTrue(output.find("Bugs Bunny")>-1)
