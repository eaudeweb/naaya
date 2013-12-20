from mock import Mock
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

def prepare_glossary_with_data(portal):
    try:
        from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre
    except ImportError:
        from nose import SkipTest
        raise SkipTest

    manage_addGlossaryCentre(portal, 'my_glossary')
    glossary = portal['my_glossary']
    glossary.parent_anchors = True

    glossary.manage_addGlossaryFolder('1', "Bucket")
    bucket = glossary['1']
    bucket.set_translations_list('German', "Eimer")

    bucket.manage_addGlossaryElement('2', "Water")
    bucket['2'].set_translations_list('German', "Wasser")

    bucket.manage_addGlossaryElement('3', "Ice")
    bucket['3'].set_translations_list('German', "Eis")

    bucket.manage_addGlossaryElement('4', "Train station")
    bucket['4'].set_translations_list('German', "Bahnhof")

    return glossary

def prepare_mock_glossary(portal):
    glossary = Mock()
    glossary.getId.return_value = 'my_glossary'
    glossary.meta_type = "Naaya Glossary"
    portal.my_glossary = glossary
    portal._objects += ({'id': 'my_glossary', 'meta_type': "Naaya Glossary"},)

    glossary_data = [{'English': "Water", 'German': "Wasser"},
                     {'English': "Ice", 'German': "Eis"},
                     {'English': "Bucket", 'German': "Eimer"},
                     {'English': "Train station", 'German': "Bahnhof"}]

    def search_result(data):
        result = Mock()
        result.get_translation_by_language = data.get
        return result

    def search_glossary(query, language, definition):
        results = []
        for item in glossary_data:
            if item[language] == query.strip():
                results.append(search_result(item))
        return (None, None, results)

    glossary.searchGlossary.side_effect = search_glossary

    return glossary


class PropertyUpdaterTest(NaayaTestCase):
    _prop_name = 'keywords'

    _set_up_glossary = staticmethod(prepare_glossary_with_data)

    def setUp(self):
        from naaya.content.url.url_item import addNyURL
        self.portal.gl_add_site_language('de')
        glossary = self._set_up_glossary(self.portal)
        self.portal.keywords_glossary = glossary.getId()
        widget = self.portal['portal_schemas']['NyURL']['keywords-property']
        widget.glossary_id = glossary.getId()
        url_id = addNyURL(self.portal['info'], title="My URL")
        self.url = self.portal['info'][url_id]

    def inject_property(self, value, language):
        """
        Helper function: set a property value without triggering any update.
        """
        self.url._setLocalPropValue(self._prop_name, language, value)

    def set_property(self, value, language):
        """
        Helper function: set a property normally, like a user would.
        """
        self.url._change_schema_properties(_lang=language,
                                           **{self._prop_name: value})

    def get_property(self, language):
        """
        Helper function: read the property.
        """
        return self.url.getLocalProperty(self._prop_name, language)

    def test_add_in_glossary_en(self):
        self.set_property("Water, Ice", 'en')
        self.assertEqual(self.get_property('de'), "Wasser, Eis")

    def test_add_in_glossary_de(self):
        self.set_property("Wasser, Eis", 'de')
        self.assertEqual(self.get_property('en'), "Water, Ice")

    def test_add_not_in_glossary_en(self):
        self.set_property("Fire, Ice", 'en')
        self.assertEqual(self.get_property('de'), "Eis")

    def test_add_not_in_glossary_de(self):
        self.set_property("Feuer, Eis", 'de')
        self.assertEqual(self.get_property('en'), "Ice")

    def test_remove_in_glossary_en(self):
        self.inject_property("Water, Ice", 'en')
        self.inject_property("Wasser, Eis", 'de')
        self.set_property("Ice", 'en')
        self.assertEqual(self.get_property('de'), "Eis")

    def test_remove_in_glossary_de(self):
        self.inject_property("Water, Ice", 'en')
        self.inject_property("Wasser, Eis", 'de')
        self.set_property("Eis", 'de')
        self.assertEqual(self.get_property('en'), "Ice")

    def test_remove_not_in_glossary_en(self):
        self.inject_property("Fire, Ice", 'en')
        self.inject_property("Feuer, Eis", 'de')
        self.set_property("Ice", 'en')
        self.assertEqual(self.get_property('de'), "Feuer, Eis")

    def test_remove_not_in_glossary_de(self):
        self.inject_property("Fire, Ice", 'en')
        self.inject_property("Feuer, Eis", 'de')
        self.set_property("Eis", 'de')
        self.assertEqual(self.get_property('en'), "Fire, Ice")

    def test_add_folder_term(self):
        self.set_property("Bucket", 'en')
        self.assertEqual(self.get_property('de'), "Eimer")

    def test_add_multiword_value(self):
        self.set_property("Train station", 'en')
        self.assertEqual(self.get_property('de'), "Bahnhof")

class MockedPropertyUpdaterTest(PropertyUpdaterTest):
    """ The same set of tests, with a mock glossary """

    _set_up_glossary = staticmethod(prepare_mock_glossary)
