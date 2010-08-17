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

from Testing import ZopeTestCase
from Products.Naaya.tests import NaayaTestCase

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.FormsTool import FormsTool

from naaya.content.document import NyDocument

class NaayaTemplateTestCase(NaayaTestCase.NaayaTestCase):
    def afterSetUp(self):
        self.my_tmpl = NaayaPageTemplateFile('the_template', globals(),
                                             'my_tmpl')
        NyDocument.my_tmpl = self.my_tmpl
        self.second_tmpl = NaayaPageTemplateFile('the_template', globals(),
                                                 'second_tmpl')
        NyDocument.second_tmpl = self.second_tmpl


    def beforeTearDown(self):
        del NyDocument.my_tmpl
        del NyDocument.second_tmpl
        del FormsTool.naaya_templates['my_tmpl']
        del FormsTool.naaya_templates['second_tmpl']

    def test_default(self):
        output = self.my_tmpl.__of__(self.portal)(a="26")
        self.assertTrue('[physical path: /portal]' in output)
        self.assertTrue('[option a: 26]' in output)

        output = self.portal.info.contact.my_tmpl(a="13")
        self.assertTrue('[physical path: /portal/info/contact]' in output)
        self.assertTrue('[option a: 13]' in output)

    def test_customize(self):
        forms_tool = self.portal.portal_forms
        ids = [f['id'] for f in forms_tool.listDefaultForms()]
        self.assertTrue('my_tmpl' in ids)
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
        second_tmpl = forms_tool['second_tmpl']
        my_tmpl = forms_tool['my_tmpl']
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

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaTemplateTestCase))
    return suite
