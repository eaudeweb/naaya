from Products.Naaya.tests import NaayaTestCase

class NaayaTests(NaayaTestCase.NaayaTestCase):

    def afterSetUp(self):
        self.login()

    def beforeTearDown(self):
        self.logout()

    def testChangeSiteTitle(self):
        lang = self._portal().gl_get_selected_language()
        self._portal()._setLocalPropValue('title', lang, 'portal_title')
        self._portal()._setLocalPropValue('site_title', lang, 'site_title')
        self._portal()._setLocalPropValue('title', 'fr', 'portal_title_fr')
        self._portal()._setLocalPropValue('site_title', 'fr', 'site_title_fr')
        self._portal()._p_changed = 1
        self.assertEqual(self._portal().getLocalProperty('title', lang), 'portal_title')
        self.assertEqual(self._portal().getLocalProperty('title', 'fr'), 'portal_title_fr')

    def testChangeEmailServer(self):
        new_server = 'newMailServer'
        self._portal().getEmailTool().manageSettings(mail_server_name=new_server)
        self.assertEqual(self._portal().mail_server_name, new_server)
