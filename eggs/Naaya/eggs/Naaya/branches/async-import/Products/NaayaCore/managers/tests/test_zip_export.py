# encoding: utf-8
from unittest import TestSuite, makeSuite
from StringIO import StringIO
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument
from naaya.content.contact.contact_item import addNyContact
from naaya.content.event.event_item import addNyEvent
from naaya.content.news.news_item import addNyNews
from naaya.content.story.story_item import addNyStory
from zipfile import ZipFile
from Products.NaayaCore.managers.zip_import_export import IZipExportObject

def load_file(filename):
    import os
    from Globals import package_home
    filename = os.path.sep.join([package_home(globals()), filename])
    data = StringIO(open(filename, 'rb').read())
    data.filename = os.path.basename(filename)
    return data

folder_with_files = load_file('./data/folder_with_files_zip.zip')
zip_one_file = load_file('./data/one_file_zip.zip')
mac_zip = load_file('./data/mac_zip.zip')

class NyZipExport(NaayaTestCase):
    """ TestCase for Naaya CSV import """

    def afterSetUp(self):
        addNyFolder(self.portal, 'zip_export_folder',
                    contributor='contributor', submitted=1)
        self.test_folder = self.portal['zip_export_folder']
        self.test_folder.approveThis()
        self.portal.manage_install_pluggableitem('Naaya Blob File')
        self.login()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['zip_export_folder'])
        self.logout()

    def test_export_ok(self):
        self.test_folder.zip_import.do_import(data=zip_one_file)
        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        self.assertTrue(isinstance(export_value, object))

        zip = ZipFile(export_value, 'r')
        self.assertEqual(set(zip.namelist()),
                         set(['zip_export_folder/one_file.txt', 'index.txt']))
        self.assertEqual(zip.read('zip_export_folder/one_file.txt'),
                         'one_file contents\n')

    def test_export_folder(self):
        self.test_folder.zip_import.do_import(data=folder_with_files)
        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        zip = ZipFile(export_value, 'r')

        expected_namelist = [
            'index.txt',
            'zip_export_folder/one_folder/',
            'zip_export_folder/one_folder/one_file.txt',
            'zip_export_folder/one_folder/two_file.txt',
            'zip_export_folder/one_folder/three_file.txt',
        ]

        self.assertEqual(set(zip.namelist()), set(expected_namelist))

    def test_export_empty_folder(self):
        """An empty folder should also be exported"""
        addNyFolder(self.test_folder, title="Some title")
        export_value = self.test_folder.zip_export.do_export()
        zip = ZipFile(export_value, 'r')
        expected_namelist = [
            'index.txt',
            'zip_export_folder/Some title/',
        ]
        self.assertEqual(set(zip.namelist()), set(expected_namelist))

    def test_export_datetime(self):
        """The files and folders in the zipfile should have the datetime set"""
        folder_id = addNyFolder(self.test_folder, title="Some title")
        export_value = self.test_folder.zip_export.do_export()
        zip = ZipFile(export_value, 'r')

        folder_datetime = self.test_folder._getOb(folder_id).releasedate
        for zipinfo in zip.filelist:
            if folder_id in zipinfo.filename:
                self.assertEqual(folder_datetime.year(), zipinfo.date_time[0])
                self.assertEqual(folder_datetime.month(), zipinfo.date_time[1])
                self.assertEqual(folder_datetime.day(), zipinfo.date_time[2])
                self.assertEqual(folder_datetime.hour(), zipinfo.date_time[3])
                self.assertEqual(folder_datetime.minute(), zipinfo.date_time[4])

    def test_export_html_document(self):
        addNyDocument(self.test_folder, id='html_document')
        self.test_folder['html_document'].body = '<p>Html document</p>'
        self.test_folder['html_document'].approved = 1
        export_value = self.test_folder.zip_export.do_export()
        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/html_document.html']))
        self.assertTrue('<p>Html document</p>' in \
                        zip.read('zip_export_folder/html_document.html'))

    def test_export_story(self):
        addNyStory(self.test_folder, id='a_nice_story')
        self.test_folder['a_nice_story'].body = '<p>A nice story</p>'
        self.test_folder['a_nice_story'].approved = 1
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
                                 'zip_export_folder/Important contact.vcf']))
        vcard_content = zip.read('zip_export_folder/Important contact.vcf')
        self.assertTrue('BEGIN:VCARD' in vcard_content)
        self.assertTrue('Important contact' in vcard_content)
        self.assertTrue('END:VCARD' in vcard_content)

    def test_export_event(self):
        addNyEvent(self.test_folder, id='interesting_event',
                   title='Great event', start_date='10/10/2000')

        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))

        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/Great event.html']))
        exported_event_content = zip.read('zip_export_folder/Great event.html')

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
                                 'zip_export_folder/Great news.html']))
        exported_news_content = zip.read('zip_export_folder/Great news.html')

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
        self.test_folder['html_document'].approved = 1
        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))

        zip = ZipFile(export_value, 'r')

        expected_namelist = ['index.txt',
                             'zip_export_folder/Picture 1.png', # TODO
                             'zip_export_folder/Picture 2.png',
                             'zip_export_folder/html_document.html']

        self.assertEqual(sorted(zip.namelist()), sorted(expected_namelist))
        self.assertTrue('<p>Html document</p>' in \
                         zip.read('zip_export_folder/html_document.html'))

        picture1_data = IZipExportObject(self.test_folder['picture-1']).data
        picture2_data = IZipExportObject(self.test_folder['picture-2']).data

        self.assertEqual(zip.read('zip_export_folder/Picture 1.png'),
                         picture1_data)
        self.assertEqual(zip.read('zip_export_folder/Picture 2.png'),
                         picture2_data)

    def test_export_anonymous(self):
        addNyDocument(self.test_folder, id='public_access')
        self.test_folder['public_access'].body = '<p>Some html</p>'
        self.test_folder['public_access'].approved = 1
        self.logout()
        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/public_access.html']))
        self.assertTrue('<p>Some html</p>' in \
                         zip.read('zip_export_folder/public_access.html'))

    def test_export_mixed_access(self):
        addNyDocument(self.test_folder, id='public_document')
        addNyDocument(self.test_folder, id='restricted_document')
        self.test_folder['public_document'].body = '<p>Some html</p>'
        self.test_folder['public_document'].approved = 1
        self.test_folder['restricted_document'].body = '<p>Restricted html</p>'
        self.test_folder['restricted_document'].approved = 1

        #restrict access
        restricted_doc = self.test_folder['restricted_document']
        permission = getattr(restricted_doc, '_View_Permission', [])
        new_permission = [x for x in permission if x != 'Anonymous']
        if 'Contributor' not in new_permission:
            new_permission.append('Contributor')
        restricted_doc._View_Permission = tuple(new_permission)

        self.logout()

        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/public_document.html']))
        self.assertTrue('<p>Some html</p>' in \
                        zip.read('zip_export_folder/public_document.html'))

        self.login('contributor')

        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        zip = ZipFile(export_value, 'r')
        self.assertEqual(sorted(zip.namelist()),
                         sorted(['index.txt',
                                 'zip_export_folder/public_document.html',
                                 'zip_export_folder/restricted_document.html']))
        self.assertTrue('<p>Some html</p>' in \
                         zip.read('zip_export_folder/public_document.html'))
        self.assertTrue('<p>Restricted html</p>' in \
                         zip.read('zip_export_folder/restricted_document.html'))


    def test_export_index_file(self):
        f = StringIO("Hello world")
        f.filename = 'myfile.rst'
        ob_id = self.test_folder.addNyBFile(uploaded_file=f)
        self.test_folder[ob_id].approveThis()

        export_value = self.test_folder.zip_export.do_export()

        zip = ZipFile(export_value, 'r')
        index_data = ("Title\tType\tPath\n"
                      "myfile\tFile\tzip_export_folder/myfile.rst\n")
        self.assertEqual(zip.read('index.txt'), index_data)


def _create_file(filename, data):
    f = StringIO(data)
    f.filename = filename
    return f

def _upload_file(parent, filename, data):
    ob_id = parent.addNyBFile(uploaded_file=_create_file(filename, data))
    parent[ob_id].approveThis()
    return parent[ob_id]

def _create_folder(parent, folder_id, title=None):
    folder_id = addNyFolder(parent, folder_id, title=title,
                            contributor='contributor', submitted=1)
    parent[folder_id].approveThis()
    return parent[folder_id]

def _zip_export_filenames(ctx):
    export_value = ctx.zip_export.do_export()
    assert not isinstance(export_value, list), 'Errors: %r' % export_value
    zip_file = ZipFile(export_value, 'r')
    return sorted(zip_file.namelist())

class ZipExportFilenames(NaayaTestCase):

    def setUp(self):
        self.portal.manage_install_pluggableitem('Naaya Blob File')
        self.my_folder = _create_folder(self.portal, 'my_folder')

    def test_export_filenames(self):
        test_file = _upload_file(self.my_folder, 'test_file.txt', "FILEDATA")
        test_file._setLocalPropValue('title', 'en', "New name")

        self.assertEqual(_zip_export_filenames(self.my_folder),
                         ['index.txt', 'my_folder/New name.txt'])

    def test_export_foldernames(self):
        _create_folder(self.portal.my_folder, 'box', "Ze Box")
        _upload_file(self.my_folder.box, 'test_file.txt', "FILEDATA")

        self.assertEqual(_zip_export_filenames(self.my_folder),
                         ['index.txt', 'my_folder/Ze Box/',
                          'my_folder/Ze Box/test_file.txt'])

    def test_filesystem_name_restrictions(self):
        test_file = _upload_file(self.my_folder, 'test_file.txt', "FILEDATA")
        test_file._setLocalPropValue('title', 'en', u"in/the 香港 Ar\\Ea")

        utf8_fs_name = 'in_the \xe9\xa6\x99\xe6\xb8\xaf Ar_Ea.txt'
        self.assertEqual(_zip_export_filenames(self.my_folder),
                         ['index.txt', 'my_folder/' + utf8_fs_name])

    def test_duplicate_file_names(self):
        from nose import SkipTest; raise SkipTest # TODO
        for c in range(3):
            test_file = _upload_file(self.my_folder, 'test_file.txt', "DATA")
            test_file._setLocalPropValue('title', 'en', "HI")

        expected_names = ['index.txt', 'my_folder/HI.txt']
        for c in range(1, 3):
            expected_names.append('my_folder/HI (%d).txt' % c)

        self.assertEqual(_zip_export_filenames(self.my_folder), expected_names)

    def test_duplicate_folder_names(self):
        from nose import SkipTest; raise SkipTest # TODO
        for c in range(3):
            folder_id = 'box_%d' % c
            folder =_create_folder(self.portal.my_folder, folder_id, "Ze Box")
            _upload_file(folder, 'test_file.txt', "DATA")

        expected_names = ['index.txt', 'Ze Box/test_file.txt']
        for c in range(1, 3):
            expected_names.append('Ze Box (%d)/test_file.txt' % c)

        self.assertEqual(_zip_export_filenames(self.my_folder), expected_names)
