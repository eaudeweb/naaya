# -*- coding: utf-8 -*-
from Products.NaayaCore.SchemaTool.widgets.GlossaryWidget import (
        GlossaryWidget)

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

class GlossaryWidgetTestCase(NaayaTestCase):
    def afterSetUp(self):
        widget = GlossaryWidget('glossary-property', title='Glossary',
                lang='en')
        widget.default = "Default value"
        self.widget = widget.__of__(self.portal.portal_schemas.NyDocument)

    def test_render_html(self):
        html = self.widget.render_html('glossary')
        self.assertTrue('value="glossary"' in html)

    def test_default_value(self):
        """ """
        html = self.widget.render_html('')
        self.assertTrue('value="%s"' % self.widget.default in html)

    def test_translate_default_value(self):
        """If there are multiple languages translate the default value into
        different langs."""
        #This should put the message in the translation catalog
        html = self.widget.render_html(self.widget.default)
        self.assertTrue('value="%s"' % self.widget.default in html)
        #Add a site language
        portal_i18n = self.portal.getPortalI18n()
        portal_i18n.add_language('fr')

        translated_message = u"La valeur par défaut"
        #Translate the default value
        translation_tool = portal_i18n.get_message_catalog()
        translation_tool.edit_message(self.widget.default, 'fr',
                translated_message)

        #render and check if the default value has been translated.
        self.portal.gl_change_site_defaultlang('fr')
        html = self.widget.render_html('')
        self.assertTrue(u'value="%s"' % translated_message in html)
