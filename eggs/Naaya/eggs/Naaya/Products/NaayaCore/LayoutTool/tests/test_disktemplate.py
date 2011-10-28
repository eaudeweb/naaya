from os import path
from unittest import TestSuite

from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.LayoutTool.DiskTemplate import manage_addDiskTemplate

from Products import Naaya as Naaya_module
naaya_module_path = path.dirname(Naaya_module.__file__)
logo_data = open(naaya_module_path + '/skel/layout/left_logo.gif').read()

use_macro_zpt = """\
<metal:block use-macro="here/portal_layout/skin/test_template/macros/portlet">
    <metal:block fill-slot="portlet_title">new title</metal:block>
</metal:block>
"""

class DiskFileTest(NaayaTestCase):
    def setUp(self):
        skin = self.portal.portal_layout.getCurrentSkin()
        manage_addDiskTemplate(skin, 'test_template',
                'Products.Naaya:skel/layout/skin/portlet_left_macro.zpt')
        self.tmpl = skin['test_template']

    def test_call(self):
        self.assertEqual(self.tmpl(),
            '\n<div class="left_portlet">\n'
            '\t<div class="left_portlet_title">PORTLET TITLE</div>\n'
            '\t<div class="left_portlet_content">PORTLET CONTENT</div>\n'
            '</div>\n\n')

    def test_use_as_macro(self):
        use_macro = ZopePageTemplate(id='use_macro').__of__(self.portal)
        use_macro.pt_edit(use_macro_zpt, 'text/html')
        self.assertEqual(use_macro(),
            '\n<div class="left_portlet">\n'
            '\t<div class="left_portlet_title">new title</div>\n'
            '\t<div class="left_portlet_content">PORTLET CONTENT</div>\n'
            '</div>\n')
