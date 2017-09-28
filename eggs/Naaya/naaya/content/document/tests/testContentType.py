import re;
from unittest import TestSuite, makeSuite

from DateTime.DateTime import DateTime

import transaction

from naaya.content.document.document_item import addNyDocument
from Products.Naaya.tests import NaayaTestCase
from Products.Naaya.tests import NaayaFunctionalTestCase

class NaayaContentTestCase(NaayaFunctionalTestCase.NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()
        
    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Documents """
        addNyDocument(self._portal().info, id='doc1', title='doc1', lang='en', submitted=1)
        addNyDocument(self._portal().info, id='doc1_fr', title='doc1_fr', lang='fr', submitted=1)
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Document'])
        
        #Get added NyDocument
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'doc1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'doc1_fr':
                meta_fr = x
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'doc1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'doc1_fr')
        
        #Change NyDocument title
        meta.process_submitted_form({'title': 'doc1_edited'}, _lang='en', _all_values=False)
        meta_fr.process_submitted_form({'title': 'doc1_fr_edited'}, _lang='fr', _all_values=False)
        
        self.assertEqual(meta.getLocalProperty('title', 'en'), 'doc1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'doc1_fr_edited')
        
        #delete NyDocument
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])
        
        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Document'])
        for x in meta:
            if x.id == 'doc1':
                meta = x
            else:
                meta = []
            
            if x.id == 'doc1_fr':
                meta_fr = x
            else:
                meta_fr = []
            
        self.assertEqual(meta, [])
        self.assertEqual(meta_fr, [])

    def do_make_document(self, kwargs=None):
        if kwargs is None:
            kwargs = {
                'title': 'my new document',
                'description': 'a nice document',
                'body': 'lots of text',
                'sortorder': '13',
                'coverage': 'nation-wide',
                'keywords': 'key1, key2',
                'releasedate': '15/03/2008',
                '_lang': 'en',
            }
        container = self._portal().info
        doc_id = container.addNyDocument(**kwargs)
        return container[doc_id]

    def test_create_edit_document(self):
        doc = self.do_make_document()
        self.failUnlessEqual(doc.title, 'my new document')
        self.failUnlessEqual(doc.description, 'a nice document')
        self.failUnlessEqual(doc.body, 'lots of text')
        self.failUnlessEqual(doc.sortorder, 13)
        self.failUnlessEqual(doc.coverage, 'nation-wide')
        self.failUnlessEqual(doc.keywords, 'key1, key2')
        self.failUnlessEqual(doc.releasedate, DateTime('15/03/2008'))

    def test_edit_document(self):
        doc = self.do_make_document()
        doc.process_submitted_form({
            'title': 'my old document',
            'description': 'an old document',
            'body': 'old text',
            'sortorder': '15',
            'coverage': 'local',
            'keywords': 'key3',
            'releasedate': '15/06/2008',
        }, _all_values=False)
        self.failUnlessEqual(doc.title, 'my old document')
        self.failUnlessEqual(doc.description, 'an old document')
        self.failUnlessEqual(doc.body, 'old text')
        self.failUnlessEqual(doc.sortorder, 15)
        self.failUnlessEqual(doc.coverage, 'local')
        self.failUnlessEqual(doc.keywords, 'key3')
        #TODO: FIX IT
        #self.failUnlessEqual(doc.releasedate, DateTime('15/06/2008'))

    def test_document_multilingual(self):
        doc = self.do_make_document()
        doc.process_submitted_form({
            'title': u'le nouveau document \u03bb',
            'description': u'ancien document \u03bb',
            'body': u'beaucoup de text \u00f8',
            'sortorder': '13',
            'coverage': u'nationel \u00f8',
            'keywords': u'k\u00e9y3',
            'releasedate': '15/06/2008',
        }, _lang='fr', _all_values=False)

        # localized properties
        self.failUnlessEqual(doc.title, 'my new document')
        self.failUnlessEqual(doc.getLocalProperty('title', 'fr'), u'le nouveau document \u03bb')
        self.failUnlessEqual(doc.description, 'a nice document')
        self.failUnlessEqual(doc.getLocalProperty('description', 'fr'), u'ancien document \u03bb')
        self.failUnlessEqual(doc.body, 'lots of text')
        self.failUnlessEqual(doc.getLocalProperty('body', 'fr'), u'beaucoup de text \u00f8')
        self.failUnlessEqual(doc.coverage, 'nation-wide')
        self.failUnlessEqual(doc.getLocalProperty('coverage', 'fr'), u'nationel \u00f8')
        self.failUnlessEqual(doc.keywords, 'key1, key2')
        self.failUnlessEqual(doc.getLocalProperty('keywords', 'fr'), u'k\u00e9y3')

        # non-localized properties
        self.failUnlessEqual(doc.sortorder, 13)
        #TODO: FIX IT
        #self.failUnlessEqual(doc.releasedate, DateTime('15/06/2008'))

    def test_index_html(self):
        doc = self.do_make_document()
        transaction.commit()

        self.browser.go('http://localhost/portal/info/' + doc.id)
        page = self.browser.get_html()

        self.failUnless(doc.title in page)
        self.failUnless(doc.description in page)
        self.failUnless(doc.body in page)
        self.failUnless(doc.coverage in page)
        self.failUnless(doc.keywords in page)
        self.failUnless(doc.releasedate.strftime('%d/%m/%Y') in page)

        doc.aq_parent.manage_delObjects([doc.id])
        transaction.commit()

    def test_edit_html(self):
        doc = self.do_make_document()
        transaction.commit()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/' + doc.id + '/edit_html')
        page = self.browser.get_html()
        self.browser_do_logout()

        tag = re.search(r'<input[^>]*name="title:utf8:ustring"[^>]*value="([^"]*)[^>]*/>', page)
        self.failUnless(tag, 'Missing <input.../> tag for "title"')
        self.failUnlessEqual(tag.group(1), doc.title)

        tag = re.search(r'<textarea[^>]*name="description:utf8:ustring"[^>]*>([^<]*)<', page)
        self.failUnless(tag, 'Missing <textarea.../> tag for "description"')
        self.failUnlessEqual(tag.group(1), doc.description)

        tag = re.search(r'<textarea[^>]*name="body:utf8:ustring"[^>]*>([^<]*)<', page)
        self.failUnless(tag, 'Missing <textarea.../> tag for "body"')
        self.failUnlessEqual(tag.group(1), doc.body)

        tag = re.search(r'<input[^>]*name="coverage:utf8:ustring"[^>]*value="([^"]*)[^>]*/>', page)
        self.failUnless(tag, 'Missing <input.../> tag for "coverage"')
        self.failUnlessEqual(tag.group(1), doc.coverage)

        tag = re.search(r'<input[^>]*name="keywords:utf8:ustring"[^>]*value="([^"]*)[^>]*/>', page)
        self.failUnless(tag, 'Missing <input.../> tag for "keywords"')
        self.failUnlessEqual(tag.group(1), doc.keywords)

        tag = re.search(r'<input[^>]*name="releasedate"[^>]*value="([^"]*)[^>]*/>', page)
        self.failUnless(tag, 'Missing <input.../> tag for "releasedate"')
        self.failUnlessEqual(tag.group(1), doc.releasedate.strftime('%d/%m/%Y'))

        doc.aq_parent.manage_delObjects([doc.id])
        transaction.commit()
