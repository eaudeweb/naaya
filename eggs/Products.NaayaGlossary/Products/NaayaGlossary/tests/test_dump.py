# encoding: utf-8

from cStringIO import StringIO
import lxml.etree
import transaction
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaGlossary.constants import NAAYAGLOSSARY_FOLDER_METATYPE
import helpers

def read_file(name):
    from os import path
    f = open(path.join(path.dirname(__file__), name))
    data = f.read()
    f.close()
    return data

class XmlImportTest(NaayaTestCase):
    def _import_xml(self, glossary, xml_data):
        glossary.xml_dump_import(StringIO(read_file(xml_data)))

    def test_import_folders(self):
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        self._import_xml(glossary, 'dump1.xml')
        folder_ids = glossary.objectIds([NAAYAGLOSSARY_FOLDER_METATYPE])
        self.assertEqual(folder_ids, ['bucket', 'glass'])

    def _check_folder_translations(self, glossary):
        bucket = glossary['bucket']
        self.assertEqual(bucket.English, "Bucket")
        self.assertEqual(bucket.German, "Eimer")
        self.assertEqual(bucket.get_def_trans_by_language('English'),
                         u"A container that holds stuff")
        self.assertEqual(bucket.get_def_trans_by_language('German'),
                         u"Ein Container, das etwas hält")

    def test_new_folder(self):
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        self._import_xml(glossary, 'dump1.xml')
        self._check_folder_translations(glossary)

    def test_update_existing_folders(self):
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        helpers.add_folder(glossary, 'bucket', "Bucket",
                           {'English': u"Bucket 0", 'German': u"Eimer 0"})
        self._import_xml(glossary, 'dump1.xml')
        self._check_folder_translations(glossary)

    def test_delete_missing_folders(self):
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        helpers.add_folder(glossary, 'tree', "Tree")
        self._import_xml(glossary, 'dump1.xml')
        folder_ids = glossary.objectIds([NAAYAGLOSSARY_FOLDER_METATYPE])
        self.assertEqual(folder_ids, ['bucket', 'glass'])

    def test_import_elements(self):
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        self._import_xml(glossary, 'dump1.xml')
        bucket = glossary['bucket']
        self.assertEqual(bucket.objectIds(), ['water', 'ice'])

    def _check_element_translations(self, glossary):
        bucket = glossary['bucket']
        water = bucket['water']
        self.assertEqual(water.English, "Water")
        self.assertEqual(water.German, "Wasser")
        self.assertEqual(water.get_def_trans_by_language('English'),
                         u"Something to drink")
        self.assertEqual(water.get_def_trans_by_language('German'),
                         u"Etwas zum trinken")

    def test_new_element(self):
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        self._import_xml(glossary, 'dump1.xml')
        self._check_element_translations(glossary)

    def test_update_existing_elements(self):
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        bucket = helpers.add_folder(glossary, 'bucket', "Bucket")
        helpers.add_element(bucket, 'water', "Water",
                            {'English': u"Water 0", 'German': "Wasser 0"})
        self._import_xml(glossary, 'dump1.xml')
        self._check_element_translations(glossary)

    def test_delete_missing_elements(self):
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        bucket = helpers.add_folder(glossary, 'bucket', "Bucket")
        boat = helpers.add_element(bucket, 'boat', "Boat")
        self._import_xml(glossary, 'dump1.xml')
        self.assertEqual(bucket.objectIds(), ['water', 'ice'])

    def test_update_order(self):
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        self._import_xml(glossary, 'dump1.xml')
        # Test initial order
        folder_ids = glossary.objectIds([NAAYAGLOSSARY_FOLDER_METATYPE])
        elem_ids = glossary.bucket.objectIds()
        self.assertEqual(folder_ids, ['bucket', 'glass'])
        self.assertEqual(elem_ids, ['water', 'ice'])

        # Now import them shuffled, test new order
        self._import_xml(glossary, 'dump1shuffled.xml')
        folder_ids = glossary.objectIds([NAAYAGLOSSARY_FOLDER_METATYPE])
        elem_ids = glossary.bucket.objectIds()
        self.assertEqual(folder_ids, ['glass', 'bucket'])
        self.assertEqual(elem_ids, ['ice', 'water'])


class ExportTest(NaayaTestCase):
    def test_export_empty(self):
        glossary = helpers.make_glossary(self.portal)
        xliff = lxml.etree.parse(StringIO(glossary.xliff_export()))
        self.assertEqual(len(xliff.xpath('/xliff/file/body')), 1)

    def test_export_folders(self):
        glossary = helpers.make_glossary(self.portal)
        bucket = helpers.add_folder(glossary, '1', 'Bucket')
        water = helpers.add_element(bucket, '2', 'Water')

        xliff = lxml.etree.parse(StringIO(glossary.xliff_export()))
        body = xliff.xpath('/xliff/file/body')[0]

        self.assertEqual(len(body.xpath('./trans-unit')), 1)
        unit = body.xpath('./trans-unit')[0]
        self.assertEqual(unit.attrib['id'], "2")
        self.assertEqual(unit.xpath('./source')[0].text, "Water")
        self.assertEqual(unit.xpath('./context-group')[0].attrib['name'], "1")

    def test_export_translated(self):
        glossary = helpers.make_glossary(self.portal)
        helpers.add_language(glossary, 'de', "German")
        bucket = helpers.add_folder(glossary, '1', 'Bucket',
                                    {'German': "Eimer"})
        water = helpers.add_element(bucket, '2', 'Water', {'German': "Wasser"})

        xliff_src = glossary.xliff_export(language="German")
        xliff = lxml.etree.parse(StringIO(xliff_src))
        body = xliff.xpath('/xliff/file/body')[0]
        unit = body.xpath('./trans-unit')[0]

        self.assertEqual(unit.xpath('./source')[0].text, "Water")
        self.assertEqual(unit.xpath('./target')[0].text, "Wasser")
        self.assertEqual(unit.xpath('./context-group')[0].text, "Eimer")

    def test_export_unicode(self):
        glossary = helpers.make_glossary(self.portal)
        helpers.add_language(glossary, 'ru', "Russian")
        glass = helpers.add_folder(glossary, '1', 'Glass',
                                   {'Russian': u"Стекло"})
        vodka = helpers.add_element(glass, '2', "Vodka", {'Russian': u"Водка"})

        xliff_src = glossary.xliff_export(language="Russian")
        xliff = lxml.etree.parse(StringIO(xliff_src))
        unit = xliff.xpath('/xliff/file/body/trans-unit')[0]

        self.assertEqual(unit.xpath('./source')[0].text, "Vodka")
        self.assertEqual(unit.xpath('./target')[0].text, u"Водка")
        self.assertEqual(unit.xpath('./context-group')[0].text, u"Стекло")

    def test_export_blank_folders(self):
        glossary = helpers.make_glossary(self.portal)
        bucket = helpers.add_folder(glossary, '1', "Bucket")

        xliff_src = glossary.xliff_export(language="English",
                                          empty_folders=True)
        xliff = lxml.etree.parse(StringIO(xliff_src))
        body = xliff.xpath('/xliff/file/body')[0]

        self.assertEqual(len(body.xpath('./trans-unit')), 1)
        unit = body.xpath('./trans-unit')[0]
        self.assertEqual(unit.attrib['id'], "1_dummy")
        self.assertEqual(unit.xpath('./source')[0].text, None)
        self.assertEqual(unit.xpath('./target')[0].text, None)
        context_group = unit.xpath('./context-group')[0]
        self.assertEqual(context_group.attrib['name'], "1")
        self.assertEqual(context_group.text, "Bucket")

class DumpExportImportTest(NaayaTestCase):
    def _make_server_glossary(self):
        glossary = helpers.make_glossary(self.portal, 'server_glossary')
        helpers.add_language(glossary, 'de', "German")
        bucket = helpers.add_folder(glossary, '1', "Bucket",
                                    {'German': "Eimer"})
        water = helpers.add_element(bucket, '2', "Water", {'German': "Wasser"})
        ice = helpers.add_element(bucket, '3', "Ice", {'German': "Eis"})
        return glossary

    def _perform_test_import(self, glossary):
        dump_file = StringIO(self._make_server_glossary().dump_export())
        glossary.dump_import(dump_file, remove_items=True)

    def test_new_folder(self):
        glossary = helpers.make_glossary(self.portal)
        helpers.add_language(glossary, 'de', "German")

        self._perform_test_import(glossary)

        folder_ids = glossary.objectIds([NAAYAGLOSSARY_FOLDER_METATYPE])
        self.assertEqual(folder_ids, ['1'])

    def test_new_term(self):
        glossary = helpers.make_glossary(self.portal)
        helpers.add_language(glossary, 'de', "German")
        bucket = helpers.add_folder(glossary, '1', "Bucket",
                                    {'German': "Eimer"})
        water = helpers.add_element(bucket, '2', "Water", {'German': "Wasser"})

        self._perform_test_import(glossary)

        self.assertEqual(set(bucket.objectIds()), set(['2', '3']))

    def test_term_not_in_zip(self):
        glossary = helpers.make_glossary(self.portal)
        helpers.add_language(glossary, 'de', "German")
        bucket = helpers.add_folder(glossary, '1', "Bucket",
                                    {'German': "Eimer"})
        water = helpers.add_element(bucket, '5', "Fire", {'German': "Feuer"})

        self._perform_test_import(glossary)

        self.assertEqual(set(bucket.objectIds()), set(['2', '3']))

    def test_folder_not_in_zip(self):
        glossary = helpers.make_glossary(self.portal)
        helpers.add_language(glossary, 'de', "German")
        bottle = helpers.add_folder(glossary, '2', "Bottle",
                                    {'German': "Flasche"})
        water = helpers.add_element(bottle, '5', "Fire", {'German': "Feuer"})

        self._perform_test_import(glossary)

        folder_ids = glossary.objectIds([NAAYAGLOSSARY_FOLDER_METATYPE])
        self.assertEqual(folder_ids, ['1'])

    def test_term_new_translations(self):
        glossary = helpers.make_glossary(self.portal)
        helpers.add_language(glossary, 'de', "German")
        bucket = helpers.add_folder(glossary, '1', "Bucket",
                                    {'German': "Eimer 0"})
        water = helpers.add_element(bucket, '2', "Water",
                                    {'German': "Wasser 0"})
        ice = helpers.add_element(bucket, '3', "Ice", {'German': "Eis 0"})

        self._perform_test_import(glossary)

        self.assertEqual(bucket.German, "Eimer")
        self.assertEqual(water.German, "Wasser")
        self.assertEqual(ice.German, "Eis")

    def test_term_new_english_titles(self):
        glossary = helpers.make_glossary(self.portal)
        bucket = helpers.add_folder(glossary, '1', "Bucket 0")
        water = helpers.add_element(bucket, '2', "Water 0")
        ice = helpers.add_element(bucket, '3', "Ice 0")

        self._perform_test_import(glossary)

        self.assertEqual(bucket.English, "Bucket")
        self.assertEqual(water.English, "Water")
        self.assertEqual(ice.English, "Ice")

#        self.assertEqual(bucket.title, "Bucket")
#        self.assertEqual(water.title, "Water")
#        self.assertEqual(ice.title, "Ice")

    def test_new_language(self):
        glossary = helpers.make_glossary(self.portal)
        bucket = helpers.add_folder(glossary, '1', "Bucket 0")
        water = helpers.add_element(bucket, '2', "Water 0")
        ice = helpers.add_element(bucket, '3', "Ice 0")

        self._perform_test_import(glossary)

        self.assertEqual(bucket.German, "Eimer")
        self.assertEqual(water.German, "Wasser")
        self.assertEqual(ice.German, "Eis")

    def _export_for_unicode_test(self):
        glossary = helpers.make_glossary(self.portal, 'server_glossary')
        helpers.add_language(glossary, 'ru', "Russian")
        glass = helpers.add_folder(glossary, '1', "Glass",
                                   {'Russian': u"Стекло"})
        vodka = helpers.add_element(glass, '2', "Vodka", {'Russian': u"Водка"})
        ice = helpers.add_element(glass, '3', "Ice", {'Russian': u"Лёд"})
        return glossary.dump_export()

    def test_unicode(self):
        dump_file = self._export_for_unicode_test()
        glossary = helpers.make_glossary(self.portal)

        glossary.dump_import(StringIO(dump_file), remove_items=True)

        self.assertEqual(glossary['1'].Russian, u"Стекло")
        self.assertEqual(glossary['1']['2'].Russian, u"Водка")
        self.assertEqual(glossary['1']['3'].Russian, u"Лёд")

    def test_no_change(self):
        dump_file = self._make_server_glossary().dump_export()
        glossary = helpers.make_glossary(self.portal)
        glossary.dump_import(StringIO(dump_file), remove_items=True)
        transaction.commit()

        glossary.dump_import(StringIO(dump_file), remove_items=True)

        connection = glossary._p_jar
        # assert no commit to DB since no change was required by second import
        self.assertEqual(connection._registered_objects, [])

    def test_empty_folders(self):
        src_glossary = helpers.make_glossary(self.portal, 'server_glossary')
        glass = helpers.add_folder(src_glossary, '1', "Bucket")
        dump_file = src_glossary.dump_export()

        glossary = helpers.make_glossary(self.portal)
        glossary.dump_import(StringIO(dump_file), remove_items=True)

        self.assertEqual(glossary.objectIds([NAAYAGLOSSARY_FOLDER_METATYPE]),
                         ['1'])
        self.assertEqual(glossary['1'].title, "Bucket")
        self.assertEqual(glossary['1'].English, "Bucket")

    def test_configuration(self):
        server_glossary = self._make_server_glossary()
        server_glossary.parent_anchors = True
        glossary = helpers.make_glossary(self.portal)
        self.assertFalse(glossary.parent_anchors)

        glossary.dump_import(StringIO(server_glossary.dump_export()))

        self.assertTrue(glossary.parent_anchors)

    def test_update_titles(self):
        server_glossary = self._make_server_glossary()
        glossary = helpers.make_glossary(self.portal)
        glossary.dump_import(StringIO(server_glossary.dump_export()))
        server_glossary['1'].title = "New bucket"
        server_glossary['1']['2'].title = "New water"

        glossary.dump_import(StringIO(server_glossary.dump_export()))
        self.assertEqual(glossary['1'].title, "New bucket")
        self.assertEqual(glossary['1']['2'].title, "New water")

    def test_update_description(self):
        server_glossary = self._make_server_glossary()
        server_glossary.set_description(u"Hello world!")
        server_glossary.set_description(u"Hallo Welt!", lang='de')
        glossary = helpers.make_glossary(self.portal)

        glossary.dump_import(StringIO(server_glossary.dump_export()))

        self.assertEqual(glossary.get_description(), u"Hello world!")
        self.assertEqual(glossary.get_description(lang='de'), u"Hallo Welt!")
