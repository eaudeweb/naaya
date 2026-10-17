import os

from naaya.groupware.tests import GWTestCase


class GWMacroInViewTest(GWTestCase):
    """ gw_macro used by a Five browser view (zope.tales engine) """

    def test_applications_view(self):
        import naaya.gwapplications
        from Products.Five import BrowserView
        from Products.Five.browser.pagetemplatefile import (
            ViewPageTemplateFile)
        from naaya.gwapplications.applications import GWApplications

        class View(BrowserView):
            index = ViewPageTemplateFile(
                'zpt/applications_index.zpt',
                os.path.dirname(naaya.gwapplications.__file__))

        from Products.PythonScripts.PythonScript import (
            manage_addPythonScript)
        app = self.portal.aq_parent
        # registered as a view in the deployed site
        manage_addPythonScript(app, 'gw_meta_info')
        app.gw_meta_info.write("return {'root_site_title': 'GW'}")
        app._setObject('applications', GWApplications(
            'applications', 'Applications', 'admin@example.com',
            'admin@example.com'))
        html = View(app.applications, self.portal.REQUEST).index()
        self.assertIn('breadcrumbitem', html)
