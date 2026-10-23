import json
import re

from Products.NaayaCore.PortletsTool.RefList import manage_addRefList
from Products.NaayaCore.PortletsTool.RefTree import manage_addRefTree
from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre
from zope.publisher.browser import setDefaultSkin

from destinet.testing.DestinetTestCase import DestinetTestCase

PAYLOAD = '</script><script>alert(1)</script>'


class ListingTemplatesTest(DestinetTestCase):

    def setUp(self):
        super(ListingTemplatesTest, self).setUp()
        self.add_manager()
        manage_addGlossaryCentre(self.portal, 'countries_glossary')
        manage_addGlossaryCentre(self.portal, 'keywords_glossary')
        # the templates sort countries on a 'name' index added on destinet.eu
        self.portal.countries_glossary.getGlossaryCatalog().addIndex(
            'name', 'FieldIndex')
        ptool = self.portal.getPortletsTool()
        for reflist in ('target-groups', 'administrative_level',
                        'certificate_sustainability', 'certificate_services',
                        'credibility', 'gstc_criteria', 'gstc_industry',
                        'landscape_type', 'topics'):
            manage_addRefList(ptool, reflist, reflist)
        manage_addRefTree(ptool, 'user-groups', 'User groups')
        self.request = self.portal.REQUEST
        self.request.SESSION = {}
        setDefaultSkin(self.request)

    def render(self, form_id, **form):
        self.request.form.update(form)
        for key, value in form.items():
            self.request.set(key, value)
        return self.portal.getFormsTool().getContent(
            {'here': self.portal.resources}, form_id)

    def script_values(self, html):
        return dict(re.findall(r'<script>var (\w+) ?= ?(.*?);</script>',
                               html))

    def check_escaped(self, html, names):
        self.assertNotIn(PAYLOAD, html)
        values = self.script_values(html)
        for name in names:
            self.assertEqual(json.loads(values[name]), PAYLOAD)

    def test_quickfinder(self):
        html = self.render('destinet_quickfinder_listing', address=PAYLOAD,
                           geo_query=PAYLOAD, category=[PAYLOAD])
        self.check_escaped(html, ['address', 'geo_query'])
        values = self.script_values(html)
        self.assertEqual(json.loads(values['category']), [PAYLOAD])
        self.assertEqual(json.loads(values['administrative_level']), [])

    def test_certified_tourism_quickfinder(self):
        html = self.render('destinet_certified_tourism_quickfinder',
                           address=PAYLOAD, geo_query=PAYLOAD)
        self.check_escaped(html, ['address', 'geo_query'])

    def test_green_travel_maps(self):
        html = self.render('destinet_green_travel_maps_listing',
                           address=PAYLOAD, geo_query=PAYLOAD)
        self.check_escaped(html, ['address', 'geo_query'])

    def test_good_practice_browser(self):
        html = self.render('destinet_good_practice_browser_listing',
                           category=PAYLOAD, landscape_type=PAYLOAD)
        self.check_escaped(html, ['category', 'landscape_type'])
