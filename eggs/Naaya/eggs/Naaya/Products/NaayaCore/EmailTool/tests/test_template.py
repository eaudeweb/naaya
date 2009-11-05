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

from OFS.SimpleItem import Item
from Testing.ZopeTestCase import TestCase
from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplate

class EmailPageTemplateUnitTest(TestCase):
    """ unit test for notifications """

    def afterSetUp(self):
        pass

    def beforeTearDown(self):
        pass

    def test_render(self):
        test_template = (
            '<tal:block>\n'
            '<subject>Hello testing #<tal:block content="options/number" />\n'
            '</subject>\n'
            '<body_text>Test message to\n'
            ' check <tal:block content="options/item" /> rendering\n'
            '</body_text>\n'
            '<ignoreme></ignoreme>\n'
            '</tal:block>\n'
        )
        templ = EmailPageTemplate(id='templ', text=test_template)

        # make sure the page template is Persistent
        self.failUnless(issubclass(EmailPageTemplate, Item))

        render1 = templ.render_email(number=13, item=u"THING")
        self.assertEqual(render1, {
            'subject': 'Hello testing #13',
            'body_text': 'Test message to\n check THING rendering',
        })

    def test_render_bad_template(self):
        templ = EmailPageTemplate(id='templ', text='<subject>asdf</subject>')
        try:
            templ.render_email()
            self.fail('Should have raised ValueError')
        except ValueError, e:
            self.assertTrue('Section "body_text" not found' in str(e))

    def test_i18n(self):
        text = ('<subject i18n:translate="">qwer</subject>\n'
                '<body_text>lala</body_text>\n')
        templ = EmailPageTemplate(id='templ', text=text)
        render = templ.render_email

        i18n_data = {
            ('qwer', 'fr'): 'azer',
        }
        def translate(message, lang):
            return i18n_data.get((message, lang), message)

        def render_subject(l=None, t=None):
            return templ.render_email(_lang=l, _translate=t)['subject']

        # no translation service specified
        s = render()['subject']
        self.assertEqual(render_subject(), 'qwer')

        s = render(_lang='fr')['subject']
        self.assertEqual(render_subject('fr'), 'qwer')

        # language not specified
        s = render(_translate=translate)['subject']
        self.assertEqual(render_subject(t=translate), 'qwer')

        # language specified
        s = render(_lang='fr', _translate=translate)['subject']
        self.assertEqual(render_subject('fr', translate), 'azer')

    def test_i18n_with_mapping(self):
        text = ('<subject>qwer</subject>\n'
                '<body_text i18n:translate="">the '
                    '<tal:block i18n:name="x">Y</tal:block>'
                ' value</body_text>\n')
        templ = EmailPageTemplate(id='templ', text=text)
        render = templ.render_email

        i18n_data = {
            ('the ${x} value', 'fr'): 'la valeur ${x}',
        }
        def translate(message, lang):
            return i18n_data.get((message, lang), message)

        def render_body(l=None, t=None):
            return templ.render_email(_lang=l, _translate=t)['body_text']

        self.assertEqual(render_body(t=translate), 'the Y value')
        self.assertEqual(render_body('fr', translate), 'la valeur Y')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(EmailPageTemplateUnitTest))
    return suite
