from naaya.groupware.tests import GWTestCase
from naaya.gwhelp import manage_addGWHelp

PAGES = ['index_html', 'main_features', 'content', 'content_folder',
         'content_forum', 'content_file', 'content_survey',
         'content_consultation', 'content_meeting', 'ig_admin',
         'user_management']


class GWHelpTest(GWTestCase):
    """ the help pages render inside the groupware gw_macro """

    def test_pages(self):
        from Products.PythonScripts.PythonScript import manage_addPythonScript
        # registered as a view in the deployed site
        manage_addPythonScript(self.app, 'gw_meta_info')
        self.app.gw_meta_info.write("return {'root_site_title': 'GW'}")
        manage_addGWHelp(self.app, 'help', 'Help')
        help_folder = self.app['help']
        for name in PAGES:
            html = getattr(help_folder, name)()
            self.assertIn('id="workarea"', html, name)
            self.assertIn('breadcrumbitem', html, name)
