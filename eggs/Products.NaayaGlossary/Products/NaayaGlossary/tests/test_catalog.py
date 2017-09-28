from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.core.zope2util import ofs_path

import helpers

def search(glossary, **kwargs):
    catalog = glossary.getGlossaryCatalog()
    results = []
    for brain in catalog(**kwargs):
        results.append(brain.getObject())
    return results

class CatalogTest(NaayaTestCase):
    def test_add_folder(self):
        glossary = helpers.make_glossary(self.portal)
        glossary.manage_addGlossaryFolder('1', "Bucket")
        bucket = glossary['1']
        self.assertEqual(search(glossary, path=ofs_path(bucket)), [bucket])
        self.assertEqual(search(glossary, English="Bucket"), [bucket])

    def test_add_entry(self):
        glossary = helpers.make_glossary(self.portal)
        bucket = helpers.add_folder(glossary, '1', "Bucket")
        bucket.manage_addGlossaryElement('2', "Water")
        water = bucket['2']
        self.assertEqual(search(glossary, path=ofs_path(water)), [water])
        self.assertEqual(search(glossary, English="Water"), [water])

    def test_remove_folder(self):
        glossary = helpers.make_glossary(self.portal)
        bucket = helpers.add_folder(glossary, '1', "Bucket")
        glossary.manage_delObjects(['1'])
        self.assertEqual(search(glossary, path=ofs_path(bucket)), [])

    def test_remove_entry(self):
        glossary = helpers.make_glossary(self.portal)
        bucket = helpers.add_folder(glossary, '1', "Bucket")
        water = helpers.add_element(bucket, '2', "Water")
        bucket.manage_delObjects(['2'])
        self.assertEqual(search(glossary, path=ofs_path(water)), [])

    def test_edit_folder(self):
        glossary = helpers.make_glossary(self.portal)
        helpers.add_language(glossary, 'de', "German")
        bucket = helpers.add_folder(glossary, '1', "Bucket")

        bucket.set_translations_list('German', "Eimer")
        self.assertEqual(search(glossary, German="Eimer"), [bucket])

        bucket.set_translations_list('English', "Bucket 0")
        self.assertEqual(search(glossary, English="Bucket 0"), [bucket])

    def test_edit_entry(self):
        glossary = helpers.make_glossary(self.portal)
        helpers.add_language(glossary, 'de', "German")
        bucket = helpers.add_folder(glossary, '1', "Bucket")
        water = helpers.add_element(bucket, '2', "Water")

        water.set_translations_list('German', "Wasser")
        self.assertEqual(search(glossary, German="Wasser"), [water])

        water.set_translations_list('English', "Water 0")
        self.assertEqual(search(glossary, English="Water 0"), [water])
