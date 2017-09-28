
from zope.i18n.interfaces import INegotiator, ILanguageAvailability
from zope.component import providedBy

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.constants import DEFAULT_PORTAL_LANGUAGE_CODE
from nose.plugins.skip import SkipTest

from naaya.i18n.constants import (ID_NAAYAI18N, TITLE_NAAYAI18N,
                                  METATYPE_NAAYAI18N)
from naaya.i18n.interfaces import INyTranslationCatalog

class TestPortalTool(NaayaTestCase):

    def setUp(self):
        self.tool = getattr(self.portal, ID_NAAYAI18N, None)

    def test_existance(self):
        self.assertTrue(self.tool is not None)
        self.assertEqual(self.tool, self.portal.getPortalI18n())
        self.assertEqual(self.tool.title, TITLE_NAAYAI18N)
        self.assertEqual(self.tool.meta_type, METATYPE_NAAYAI18N)

    def test_components_availability(self):
        self.assertTrue(ILanguageAvailability.providedBy(
                                                  self.tool.get_lang_manager()))
        self.assertTrue(INegotiator.providedBy(self.tool.get_negotiator()))
        self.assertTrue(INyTranslationCatalog.providedBy(
                                               self.tool.get_message_catalog()))

class TestNySiteApi(NaayaTestCase):

    def setUp(self):
        self.portal.gl_add_site_language('de')
        # needed for some Localizer Patching:
        try:
            from thread import get_ident
            from Products.Localizer.patches import _requests
            _requests[get_ident()] = self.portal.REQUEST
        except:
            pass

    def test_get_all_languages(self):
        known_langs = self.portal.gl_get_all_languages()
        self.assertTrue(isinstance(known_langs, list))
        self.assertTrue(len(known_langs) > 20) # length of languages.txt
        self.assertTrue(isinstance(known_langs[0], dict))
        self.assertTrue(known_langs[0].has_key('code'))
        self.assertTrue(known_langs[0].has_key('name'))
        # test sorted by code
        for i in range(len(known_langs)-1):
            self.assertTrue(known_langs[i]['code'] <= known_langs[i+1]['code'])

    def test_get_languages(self):
        self.assertEqual(self.portal.gl_get_languages(),
                         (DEFAULT_PORTAL_LANGUAGE_CODE, 'de'))

    def test_get_languages_mapping(self):
        self.portal.gl_change_site_defaultlang(DEFAULT_PORTAL_LANGUAGE_CODE)
        mapping = self.portal.gl_get_languages_mapping()
        self.assertEqual(len(mapping), 2)
        self.assertTrue('de' in [x['code'] for x in mapping])
        self.assertTrue(DEFAULT_PORTAL_LANGUAGE_CODE in [x['code'] for x in mapping])
        self.assertEqual([DEFAULT_PORTAL_LANGUAGE_CODE],
                         [x['code'] for x in mapping if x['default']])

    def test_default_language(self):
        self.assertEqual(self.portal.gl_get_default_language(),
                         DEFAULT_PORTAL_LANGUAGE_CODE)
        self.portal.gl_change_site_defaultlang('de')
        self.assertEqual(self.portal.gl_get_default_language(), 'de')
        self.assertEqual(self.portal.getPortalI18n().get_message_catalog()\
                         ._default_language, 'en')

    def test_get_selected_language(self):
        i18n = self.portal.getPortalI18n()
        self.portal.REQUEST[i18n.get_negotiator().cookie_id] = 'de'
        self.assertEqual(self.portal.gl_get_selected_language(), 'de')

    def test_get_languages_map(self):
        i18n = self.portal.getPortalI18n()
        self.portal.REQUEST[i18n.get_negotiator().cookie_id] = 'de'
        l_map = self.portal.gl_get_languages_map()
        self.assertEqual(len(l_map), 2)
        self.assertTrue('de' in [x['id'] for x in l_map])
        self.assertTrue(DEFAULT_PORTAL_LANGUAGE_CODE in [x['id'] for x in l_map])
        self.assertEqual(['de'], [x['id'] for x in l_map if x['selected']])

    def test_get_language_name(self):
        self.assertEqual(self.portal.gl_get_language_name('en-US'),
                         'English/United States')
        self.assertEqual(self.portal.gl_get_language_name('un-known'), '???')

    def test_changeLanguage(self):
        i18n = self.portal.getPortalI18n()
        cookie_id = i18n.get_negotiator().cookie_id
        self.assertEqual(self.portal.gl_get_selected_language(),
                         DEFAULT_PORTAL_LANGUAGE_CODE)
        self.portal.gl_changeLanguage('de')
        self.assertTrue(self.portal.REQUEST.RESPONSE.cookies.has_key(cookie_id))
        cookie = self.portal.REQUEST.RESPONSE.cookies[cookie_id]
        self.assertEqual(cookie['path'], '/portal')
        self.assertEqual(cookie['value'], 'de')

    def test_add_site_language(self):
        self.portal.gl_add_site_language('fr')
        self.portal.gl_add_site_language('ar')
        self.assertEqual(self.portal.gl_get_languages(),
                         (DEFAULT_PORTAL_LANGUAGE_CODE, 'de', 'fr', 'ar'))

    def test_del_site_languages(self):
        self.portal.gl_add_site_language('fr')
        self.portal.gl_del_site_languages(('de', 'fr'))
        self.assertEqual(self.portal.gl_get_languages(),
                         (DEFAULT_PORTAL_LANGUAGE_CODE, ))


class NySiteFunctionalTestCase(NaayaFunctionalTestCase):

    def test_changeLanguage_redirect(self):
        # Test redirect, no referrer
        self.portal.gl_add_site_language('fr')
        import transaction; transaction.commit()
        self.browser.go('http://localhost/portal/info/contact/gl_changeLanguage?old_lang=fr')
        self.assertEqual(self.browser.get_url(),
                         'http://localhost/portal/info/contact')
