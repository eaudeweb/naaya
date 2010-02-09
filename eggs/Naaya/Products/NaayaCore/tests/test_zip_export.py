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
# David Batranu, Eau de Web

from unittest import TestSuite, makeSuite
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaTestCase import load_test_file
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument
from naaya.content.contact.contact_item import addNyContact
from naaya.content.event.event_item import addNyEvent
from naaya.content.news.news_item import addNyNews
from naaya.content.story.story_item import addNyStory
from zipfile import ZipFile
from Products.NaayaCore.managers.zip_import_export import IZipExportObject


folder_with_files = load_test_file('./data/folder_with_files_zip.zip', globals())
zip_one_file = load_test_file('./data/one_file_zip.zip', globals())
mac_zip = load_test_file('./data/mac_zip.zip', globals())

class NyZipExport(NaayaTestCase):
    """ TestCase for Naaya CSV import """

    def afterSetUp(self):
        addNyFolder(self.portal, 'zip_export_folder',
                    contributor='contributor', submitted=1)
        self.test_folder = self.portal['zip_export_folder']

    def beforeTearDown(self):
        self.portal.manage_delObjects(['zip_export_folder'])

    def test_export_ok(self):
        self.test_folder.zip_import.do_import(data=zip_one_file)
        export_value = self.test_folder['one_file_zip'].zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        self.assertTrue(isinstance(export_value, object))

        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['one_file_zip/one_file.txt',
                                 'index.txt']))
        self.assertEqual(zip.read('one_file_zip/one_file.txt'),
                         'one_file contents\n')

    def test_export_folder(self):
        self.test_folder.zip_import.do_import(data=folder_with_files)
        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        zip = ZipFile(export_value, 'r')

        expected_namelist = \
        ['index.txt',
         'zip_export_folder/folder_with_files_zip/',
         'zip_export_folder/folder_with_files_zip/one_folder/',
         'zip_export_folder/folder_with_files_zip/one_folder/one_file.txt',
         'zip_export_folder/folder_with_files_zip/one_folder/two_file.txt',
         'zip_export_folder/folder_with_files_zip/one_folder/three_file.txt']

        self.assertEqual(sorted(zip.namelist()), sorted(expected_namelist))

    def test_export_html_document(self):
        addNyDocument(self.test_folder, id='html_document')
        self.test_folder['html_document'].body = '<p>Html document</p>'
        export_value = self.test_folder.zip_export.do_export()
        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/html_document.html']))
        self.assertEqual(zip.read('zip_export_folder/html_document.html'),
                                  '<p>Html document</p>')

    def test_export_story(self):
        addNyStory(self.test_folder, id='a_nice_story')
        self.test_folder['a_nice_story'].body = '<p>A nice story</p>'
        export_value = self.test_folder.zip_export.do_export()
        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/a_nice_story.html']))
        self.assertEqual(zip.read('zip_export_folder/a_nice_story.html'),
                                  '<p>A nice story</p>')

    def test_export_contact(self):
        addNyContact(self.test_folder, id="important_contact",
                     title='Important contact')
        export_value = self.test_folder.zip_export.do_export()
        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/important_contact.vcf']))
        exported_vcard_content = \
            zip.read('zip_export_folder/important_contact.vcf')
        self.assertTrue('BEGIN:VCARD' in exported_vcard_content)
        self.assertTrue('Important contact' in exported_vcard_content)
        self.assertTrue('END:VCARD' in exported_vcard_content)

    def test_export_event(self):
        addNyEvent(self.test_folder, id='interesting_event',
                   title='Great event')

        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))

        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/interesting_event.html']))
        exported_event_content = \
            zip.read('zip_export_folder/interesting_event.html')

        obj = self.test_folder['interesting_event']
        schema = self.portal.getSchemaTool().getSchemaForMetatype('Naaya Event')
        obj_data = []
        obj_data.append('<html><body>')
        obj_data.append('<h1>%s</h1>' % obj.title_or_id())

        for widget in schema.listWidgets():
            if widget.prop_name() in ['sortorder', 'topitem', 'title']:
                continue
            if not widget.visible:
                continue
            obj_widget_value = getattr(obj, widget.prop_name(), '')
            widget_data = widget._convert_to_form_string(obj_widget_value)

            if not widget_data:
                continue

            obj_data.append('<h2>%s</h2><p><div>%s</div></p>' % (widget.title,
                                                                 widget_data))

        obj_data.append('</body></html>')
        self.assertEqual('\n'.join(obj_data), exported_event_content)

    def test_export_news(self):
        addNyNews(self.test_folder, id='interesting_news',
                   title='Great news')

        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))

        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/interesting_news.html']))
        exported_news_content = \
            zip.read('zip_export_folder/interesting_news.html')

        obj = self.test_folder['interesting_news']
        schema = self.portal.getSchemaTool().getSchemaForMetatype('Naaya News')
        obj_data = []
        obj_data.append('<html><body>')
        obj_data.append('<h1>%s</h1>' % obj.title_or_id())

        for widget in schema.listWidgets():
            if widget.prop_name() in ['sortorder', 'topitem', 'title']:
                continue
            if not widget.visible:
                continue
            obj_widget_value = getattr(obj, widget.prop_name(), '')
            widget_data = widget._convert_to_form_string(obj_widget_value)

            if not widget_data:
                continue

            obj_data.append('<h2>%s</h2><p><div>%s</div></p>' % (widget.title,
                                                                 widget_data))

        obj_data.append('</body></html>')
        self.assertEqual('\n'.join(obj_data), exported_news_content)

    def test_export_mixed_encodings(self):
        self.test_folder.zip_import.do_import(data=mac_zip)
        addNyDocument(self.test_folder, id='html_document')
        self.test_folder['html_document'].body = u'<p>Html document</p>'
        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))

        zip = ZipFile(export_value, 'r')

        expected_namelist = ['index.txt',
                             'zip_export_folder/mac_zip/',
                             'zip_export_folder/mac_zip/Picture_1.png',
                             'zip_export_folder/mac_zip/Picture_2.png',
                             'zip_export_folder/html_document.html']

        self.assertEqual(sorted(zip.namelist()), sorted(expected_namelist))
        self.assertEqual(zip.read('zip_export_folder/html_document.html'),
                                  '<p>Html document</p>')

        imported_folder = self.test_folder['mac_zip']

        picture1_data = IZipExportObject(imported_folder['Picture_1.png'])()[0]
        picture2_data = IZipExportObject(imported_folder['Picture_2.png'])()[0]

        self.assertEqual(zip.read('zip_export_folder/mac_zip/Picture_1.png'),
                         picture1_data)
        self.assertEqual(zip.read('zip_export_folder/mac_zip/Picture_2.png'),
                         picture2_data)

    def test_export_anonymous(self):
        addNyDocument(self.test_folder, id='public_access')
        self.test_folder['public_access'].body = '<p>Some html</p>'
        self.logout()
        self.portalLogout()
        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/public_access.html']))
        self.assertEqual(zip.read('zip_export_folder/public_access.html'),
                         '<p>Some html</p>')

    def test_export_mixed_access(self):
        addNyDocument(self.test_folder, id='public_document')
        addNyDocument(self.test_folder, id='restricted_document')
        self.test_folder['public_document'].body = '<p>Some html</p>'
        self.test_folder['restricted_document'].body = '<p>Restricted html</p>'

        #restrict access
        restricted_doc = self.test_folder['restricted_document']
        permission = getattr(restricted_doc, '_View_Permission', [])
        new_permission = [x for x in permission if x != 'Anonymous']
        if 'Contributor' not in new_permission:
            new_permission.append('Contributor')
        restricted_doc._View_Permission = tuple(new_permission)

        self.logout()
        self.portalLogout()

        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/public_document.html']))
        self.assertEqual(zip.read('zip_export_folder/public_document.html'),
                         '<p>Some html</p>')

        self.login('contributor')
        self.portalLogin('contributor')

        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/public_document.html',
                                 'zip_export_folder/restricted_document.html']))
        self.assertEqual(zip.read('zip_export_folder/public_document.html'),
                                  '<p>Some html</p>')
        self.assertEqual(zip.read('zip_export_folder/restricted_document.html'),
                                  '<p>Restricted html</p>')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyZipExport))
    return suite


