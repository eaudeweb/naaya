# -*- coding=utf-8 -*-

# Python imports
import unittest
from urllib import quote

# Zope imports
from Products.PageTemplates.PageTemplate import PageTemplate

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
            catalog = NaayaI18n('id', 'title',
                                [('en', 'English'), ('de', 'German')])\
                      .get_message_catalog()
            catalog.edit_message('Administration', 'de', 'Verwaltung')
            catalog.gettext('Unkown', 'en')
            wrapper = TranslationsToolWrapper(catalog)
        return wrapper

    class TranslationsToolWrapperTest(unittest.TestCase):

        def setUp(self):
            self.wrapper = _wrapper_factory()


        def test_get_msg_translations(self):
            self.assertEqual(self.wrapper.get_msg_translations('Administration', ''),
                             '')
            self.assertEqual(self.wrapper.get_msg_translations('', ''), None)
            self.assertEqual(self.wrapper.get_msg_translations('Administration', 'en'),
                             'Administration')
            self.assertEqual(self.wrapper.get_msg_translations('Administration', 'de'),
                             'Verwaltung')

        def test_msgEncodeDecode(self):
            self.assertEqual(self.wrapper.message_encode(' 1+'), 'IDEr\n')
            self.assertEqual(self.wrapper.msgEncode(' 1+'),
                             quote(self.wrapper.message_encode(' 1+')))
            self.assertEqual(self.wrapper.msgEncode(' 1+'), 'IDEr%0A')
            self.assertEqual(self.wrapper.message_decode(
                                       self.wrapper.message_encode(' 1+')), ' 1+')
            self.assertEqual(self.wrapper.message_decode('IDEr\n'), ' 1+')

        def test_languages_mapping(self):
            mapping = self.wrapper.tt_get_languages_mapping()

            self.assertEqual(len(mapping), 1)
            self.assertTrue(mapping[0].has_key('code'))
            self.assertTrue(mapping[0].has_key('name'))
            self.assertTrue(mapping[0].has_key('default'))
            self.assertEqual(mapping[0]['code'], 'de')
            self.assertEqual(mapping[0]['name'], 'German')

        def test_get_messages(self):
            messages = self.wrapper.tt_get_messages('', 'msg', True)
            messages_order_de = self.wrapper.tt_get_messages('', 'de', True)
            self.assertEqual(messages,
                             [('Unkown', False), ('Administration', True)])
            self.assertEqual(messages_order_de,
                             [('Administration', True), ('Unkown', False)])

        def test_get_not_translated_messages_count(self):
            count = self.wrapper.tt_get_not_translated_messages_count('')
            self.assertEqual(count, {'de': 1})
            count = self.wrapper.tt_get_not_translated_messages_count('nkow')
            self.assertEqual(count, {'de': 1})
            count = self.wrapper.tt_get_not_translated_messages_count('x')
            self.assertEqual(count, False)

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
            self.portal.REQUEST['EDW_SelectedLanguage'] = {('en', 'de'): 'de'}
            self.portal.REQUEST['TraversalRequestNameStack'] = ['de']

        def test_translate(self):
            # add message and translation
            self.portal.getPortalTranslations().gettext('${count} dogs', 'en')
            try:
                self.portal.getPortalTranslations().message_edit('${count} dogs', 'de', '${count} Hunde', '')
            except AttributeError:
                self.portal.getPortalTranslations().edit_message('${count} dogs', 'de', '${count} Hunde')

            # and test!
            in_de = self.portal.getPortalTranslations().trans('${count} dogs',
                                                              count='3')
            self.assertEqual(in_de, '3 Hunde')

        def test_template_translation(self):
            self.tmpl = PageTemplate(id='test_tmpl')
            self.tmpl.pt_edit('<p i18n:translate="">Home for'
                              ' <span i18n:name="hours">3</span> hours</p>',
                              'text/html')

            self.assertEqual(self.tmpl.__of__(self.portal)(),
                             '<p>Home for <span>3</span> hours</p>')
            self.portal.getLocalizer().edit_message('Home for ${hours} hours', 'en',
                                                    'Home für ${hours} Stunden')
            self.assertEqual(self.tmpl.__of__(self.portal)(),
                             '<p>Home für <span>${hours}</span> Stunden</p>')
