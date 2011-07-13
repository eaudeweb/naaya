# -*- coding=utf-8 -*-

# Python imports
import unittest
from urllib import quote
from mock import Mock

# Zope imports
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

# Naaya imports
from naaya.i18n import NaayaI18n
from naaya.i18n.TranslationsToolWrapper import TranslationsToolWrapper
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
try:
    from Products.NaayaCore.TranslationsTool.TranslationsTool import TranslationsTool
except ImportError:
    pass
else:
    class _PatchedTranslationsTool(TranslationsTool):
        """ Since this is not a NaayaTestCase, acquisition is missing """
        def utToUtf8(self, p_string):
            if isinstance(p_string, unicode): return p_string.encode('utf-8')
            else: return str(p_string)

    def _wrapper_factory():
        """ You can use this to create wrapper or the actual translations tool """
        # you can use this bool as a manual switch
        actual_tool = False

        if actual_tool:
            wrapper = _PatchedTranslationsTool('id', 'title')
            wrapper.add_language('de')
            wrapper.gettext('Administration', 'de')
            wrapper.message_edit('Administration', 'de', 'Verwaltung', '')
            wrapper.gettext('Unkown', 'en')
        else:
            portal_i18n = NaayaI18n('id', 'title',
                                    [('en', 'English'), ('de', 'German')])
            catalog = portal_i18n.get_message_catalog()
            catalog.edit_message('Administration', 'de', 'Verwaltung')
            catalog.gettext('Unkown', 'en')
            site_mock = Mock()
            getPortalI18n = site_mock.getPortalI18n
            getPortalI18n.return_value = portal_i18n

            wrapper = TranslationsToolWrapper(portal_i18n)
            wrapper.getSite = lambda: site_mock

        return wrapper


    class TranslationsToolWrapperNaayaTest(NaayaTestCase):

        def setUp(self):
            # step 1: fix request patch, for Localizer
            try:
                # needed for some Localizer Patching:
                from thread import get_ident
                from Products.Localizer.patches import _requests
                _requests[get_ident()] = self.portal.REQUEST
            except:
                pass

            # step 2: add language in site and catalog
            self.portal.gl_add_site_language('de')
            try:
                # for old code, we also need to add language in trans. catalog
                self.portal.getPortalTranslations().add_language('de')
            except:
                pass

            # step 3: force negotiation to de, regardless of negotiator
            portal_i18n = self.portal.getPortalI18n()
            self.portal.REQUEST['EDW_SelectedLanguage'] = {('en', 'de'): 'de'}
            self.portal.REQUEST.cookies[portal_i18n.get_negotiator().cookie_id] = 'de'

        def test_translate(self):
            # add message and translation
            self.portal.getPortalTranslations().gettext('${count} dogs', 'en')
            try:
                self.portal.getPortalTranslations().message_edit('${count} dogs', 'de', '${count} Hunde', '')
            except AttributeError:
                self.portal.getPortalI18n().get_message_catalog().edit_message('${count} dogs', 'de', '${count} Hunde')

            # and test!
            in_de = self.portal.getPortalTranslations().trans('${count} dogs',
                                                              count='3')
            self.assertEqual(in_de, '3 Hunde')

        def test_template_translation(self):
            tmpl = ZopePageTemplate(id='test_tmpl')
            tmpl.pt_edit('<p i18n:translate="">Home for'
                              ' <span i18n:name="hours">3</span> hours</p>',
                              'text/html')

            self.assertEqual(tmpl.__of__(self.portal)(),
                             u'<p>Home for <span>3</span> hours</p>\n')
