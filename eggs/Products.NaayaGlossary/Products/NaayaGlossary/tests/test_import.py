# encoding: utf-8
from io import BytesIO

import lxml.etree
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

from . import helpers


class TranslationsImportTest(NaayaTestCase):
    """ XLIFF and TMX import, SKOS export """

    def make_source(self):
        glossary = helpers.make_glossary(self.portal, 'source', langs=['de'])
        bucket = helpers.add_folder(glossary, 'B', 'Bucket',
                                    {'German': 'Eimer'})
        helpers.add_element(bucket, 'water', 'Water',
                            {'German': 'Wässer'})
        return glossary

    def test_xliff_import(self):
        xliff = self.make_source().xliff_export(language='German')
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        glossary.xliff_import(BytesIO(xliff.encode('utf-8')))
        water = glossary['B']['water']
        self.assertEqual(water.get_translation_by_language('English'),
                         'Water')
        self.assertEqual(water.get_translation_by_language('German'),
                         'Wässer')
        self.assertEqual(glossary['B'].get_translation_by_language('German'),
                         'Eimer')

    def test_terms_import_xliff_adds_no_themes(self):
        xliff = self.make_source().xliff_export(language='German')
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        themes = list(glossary.get_subjects_list())
        request = self.portal.REQUEST
        glossary.terms_import('xliff', BytesIO(xliff.encode('utf-8')),
                              REQUEST=request)
        self.assertEqual(glossary['B']['water'].subjects, [])
        self.assertEqual(list(glossary.get_subjects_list()), themes)
        self.assertEqual(request.RESPONSE.getHeader('Location'),
                         'index_impexp_html')

    def test_xliff_import_with_themes(self):
        xliff = self.make_source().xliff_export(language='German')
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        glossary.xliff_import(BytesIO(xliff.encode('utf-8')),
                              add_themes_from_folders=1)
        self.assertIn('B', [t['code'] for t in glossary.get_subjects_list()])
        self.assertEqual([s['code'] for s in glossary['B']['water'].subjects],
                         ['B'])

    def test_tmx_import(self):
        tmx = self.make_source().tmx_export()
        glossary = helpers.make_glossary(self.portal, langs=['de'])
        glossary.tmx_import(BytesIO(tmx.encode('utf-8')))
        water = glossary['W']['Water']
        self.assertEqual(water.get_translation_by_language('English'),
                         'Water')
        self.assertEqual(water.get_translation_by_language('German'),
                         'Wässer')

    def test_skos_export(self):
        glossary = self.make_source()
        glossary['B']['water'].set_def_trans_list('German', 'Etwas & mehr')
        glossary['B']['water'].approveThis()
        rdf = glossary['glossary_skos.rdf']()
        xml = lxml.etree.fromstring(rdf.encode('utf-8'))
        ns = {'skos': 'http://www.w3.org/2004/02/skos/core#',
              'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}
        [desc] = xml.findall('rdf:Description', ns)
        self.assertTrue(desc.get('{%s}about' % ns['rdf']).endswith(
            '/source/B/water'))
        labels = {e.get('{http://www.w3.org/XML/1998/namespace}lang'): e.text
                  for e in desc.findall('skos:prefLabel', ns)}
        self.assertEqual(labels, {'en': 'Water', 'de': 'Wässer'})
        definitions = {
            e.get('{http://www.w3.org/XML/1998/namespace}lang'): e.text
            for e in desc.findall('skos:definition', ns)}
        self.assertEqual(definitions['de'], 'Etwas & mehr')

    def test_style_template(self):
        glossary = helpers.make_glossary(self.portal)
        css = glossary.style_presentation_css.read()
        self.assertIsInstance(css, str)
        self.assertTrue(css.strip())
