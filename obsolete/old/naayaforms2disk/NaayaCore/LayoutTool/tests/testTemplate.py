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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web
# Alin Voinea, Eau de Web

from unittest import TestSuite, makeSuite
from Products.Naaya.tests import NaayaTestCase
from Products.NaayaCore.LayoutTool.Template import manage_addTemplate
from Products.NaayaCore.LayoutTool.Template import Template

class TestTemplate(NaayaTestCase.NaayaTestCase):
    """ TestCase for Template object
    Sample test run from windows command prompt:
    C:\Zope-2.8.8-final>c:\Zope-2.8.8-final\bin\python.exe bin\test.py -vC D:\ZopeInstance\Zope2.8.8\etc\zope.conf --libdir D:\ZopeInstance\Zope2.8.8\Products\NaayaCore\LayoutTool 
    """

    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()


    def test_Template(self):
        tpl = Template('uid', 'title', 'text', 'text/html')
        self.assert_(hasattr(tpl, 'title'), 'Form has no attribute "title"')
        self.assert_(hasattr(tpl, 'path'), 'Form has no attribute "path"')
        self.assert_(hasattr(tpl, 'customized'), 'Form has no attribute "customized"')


    def test_manageAddTemplate(self):
        """Test that we can successfully add a template using manageAddTemplate"""
        formstool_ob = self.portal.getFormsTool()
        layouttool_ob = self.portal.getLayoutTool()
        self.assertNotEqual(formstool_ob, None)
        self.assertNotEqual(layouttool_ob, None)
        
        id = 'test_id'
        manage_addTemplate(formstool_ob, id, 'test title', 'file_dummy_content', None)
        form_ob = formstool_ob._getOb(id, None)
        self.failIfEqual(form_ob, None, 'Form was not added into FormsTool')
        self.assert_(hasattr(form_ob, 'path'), 'Form has no attribute "path"')
        self.assert_(hasattr(form_ob, 'customized'), 'Form has no attribute "customized"')


    def test_Customized(self):
        tpl = Template('uid', 'title', 'text', 'text/html')
        self.assertEqual(tpl.isCustomized(), False)
        tpl.setCustomized(True)
        self.assertEqual(tpl.isCustomized(), True)


    def test_manageAddTemplateFromFile(self):
        import os
        file_c = os.path.join(os.path.dirname(__file__), 'testform.zpt')
        formstool_ob = self.portal.getFormsTool()
        layouttool_ob = self.portal.getLayoutTool()
        self.assertNotEqual(formstool_ob, None)
        self.assertNotEqual(layouttool_ob, None)
        
        id = 'test_id'
        manage_addTemplate(formstool_ob, id, 'title', file_c, None)
        form_ob = formstool_ob._getOb(id, None)
        self.failIfEqual(form_ob, None, 'Form was not added into FormsTool')
        self.assert_(hasattr(form_ob, 'path'), 'Form has no attribute "path"')
        self.assert_(hasattr(form_ob, 'customized'), 'Form has no attribute "customized"')
        self.assertEqual(form_ob.getText(), 'insidefile')
        
        
    def test_Path(self):
        tpl = Template('uid', 'title', 'text', 'text/html')
        self.assertEqual(tpl.getPath(), None)
        tpl.setPath('testx')
        self.assertEqual(tpl.getPath(), 'testx')


    def test_Text(self):
        tpl = Template('uid', 'title', 'AMD/Cyron', 'text/html')
        self.assertEqual(tpl.getText(), 'AMD/Cyron')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplate))
    return suite
