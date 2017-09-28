from datetime import datetime
from StringIO import StringIO

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.localizedbfile.localizedbfile_item import addNyLocalizedBFile
from mock import Mock

class NyLocalizedBFileTestCase(NaayaTestCase):
    """ TestCase for Naaya BFile object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        self.portal.gl_add_site_language('fr')
        self.lang_map = self.portal.gl_get_languages()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])

    def add_localizedbfile(self, lang, **kwargs):
        addNyLocalizedBFile(self.portal.myfolder, submitted=1, contributor='contributor', _lang=lang, **kwargs )

    def test_add_blank(self):
        self.add_localizedbfile(id='mylocalizedbfile', title='My Localized bfile', lang='en')
        self.assertTrue('mylocalizedbfile' in self.portal.myfolder.objectIds())

        mylocalizedbfile = self.portal.myfolder.mylocalizedbfile
        self.assertTrue(mylocalizedbfile.id, 'mylocalizedbfile')
        self.assertTrue(mylocalizedbfile.title, 'My Localized bfile')
        self.assertEqual(len(mylocalizedbfile._versions), 0)
        self.assertEqual(mylocalizedbfile.current_version, None)
        
    def test_add_with_file(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.jpg'
        myfile.headers = {'content-type': 'image/jpeg'}

        now_pre = datetime.utcnow()
        self.add_localizedbfile(id='mylocalizedbfile', title='My Localized bfile', uploaded_file=myfile, lang='en')
        now_post = datetime.utcnow()

        mylocalizedbfile = self.portal.myfolder.mylocalizedbfile
        language = 'en'
        self.assertTrue(mylocalizedbfile.id, 'mylocalizedbfile')
        self.assertTrue(mylocalizedbfile.title, 'My Localized bfile')
        #no french version for this file
        self.assertFalse(mylocalizedbfile._versions.has_key('fr'))
        self.assertEqual(len(mylocalizedbfile._versions), 1)
        self.assertTrue(mylocalizedbfile.current_version is mylocalizedbfile._versions[language][0])

        ver = mylocalizedbfile.current_version
        self.assertTrue(now_pre <= ver.timestamp <= now_post)
        self.assertEqual(ver.open().read(), 'hello data!')
        self.assertEqual(ver.filename, 'my.jpg')
        self.assertEqual(ver.size, 11)
        self.assertEqual(ver.content_type, 'image/jpeg')
      
        #test french version
        myfrfile = StringIO('hello data from France!')
        myfrfile.filename = 'my-fr.jpg'
        myfrfile.headers = {'content-type': 'image/jpeg'}

        mylocalizedbfile._save_file(myfrfile, 'fr',
                                 contributor='contributor')
        self.assertEqual(len(mylocalizedbfile._versions), 2)
        self.assertTrue(mylocalizedbfile._versions.has_key('fr'))
        fr_file = mylocalizedbfile._versions['fr'][0]
        self.assertEqual(fr_file.open().read(), 'hello data from France!')
        self.assertEqual(fr_file.filename, 'my-fr.jpg')
        self.assertEqual(fr_file.content_type, 'image/jpeg')

    def test_add_with_file_with_fake_content_type(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.pdf'
        myfile.headers = {'content-type': 'image/jpeg'}

        self.add_localizedbfile(id='mylocalizedbfile', title='My Localized bfile', uploaded_file=myfile, lang='en')
        mylocalizedbfile = self.portal.myfolder.mylocalizedbfile
        ver = mylocalizedbfile.current_version

        self.assertEqual(ver.content_type, 'application/pdf')

    def test_change_file(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.txt'
        self.add_localizedbfile(id='mylocalizedbfile', title='My Localized bfile', uploaded_file=myfile, lang='en')
        mylocalizedbfile = self.portal.myfolder.mylocalizedbfile
        language = 'en'

        myfile2 = StringIO('new data')
        myfile2.filename = 'other.txt'
        mylocalizedbfile._save_file(myfile2, language,
                                 contributor='contributor')
        myfrfile = StringIO('french data')
        myfrfile.filename = 'french_file.txt'
        mylocalizedbfile._save_file(myfrfile, 'fr',
                                 contributor='contributor')
        myfrfile2 = StringIO('new french data')
        myfrfile2.filename = 'french_file_2.txt'
        mylocalizedbfile._save_file(myfrfile2, 'fr',
                                 contributor='contributor')
        myfrfile2 = StringIO('newer french data')
        myfrfile2.filename = 'french_file_3.txt'
        mylocalizedbfile._save_file(myfrfile2, 'fr',
                                 contributor='contributor')

        versions_en = mylocalizedbfile._versions_for_tmpl(language)
        self.assertEqual(len(versions_en), 2)
        versions_fr = mylocalizedbfile._versions_for_tmpl('fr')
        self.assertEqual(len(versions_fr), 3)

        cv = mylocalizedbfile.current_version
        self.assertEqual(cv.filename, 'other.txt')
        self.assertEqual(cv.size, 8)
        self.assertEqual(cv.open().read(), 'new data')

        mylocalizedbfile.get_selected_language = Mock(return_value='fr')
        cv_fr = mylocalizedbfile.current_version
        self.assertEqual(cv_fr.filename, 'french_file_3.txt')
        self.assertEqual(cv_fr.open().read(), 'newer french data')

    def test_remove_version(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.txt'
        self.add_localizedbfile(id='mylocalizedbfile', title='My Localized bfile', uploaded_file=myfile, lang='en')
        mylocalizedbfile = self.portal.myfolder.mylocalizedbfile

        language = 'de'
        self.assertRaises(KeyError, mylocalizedbfile.remove_version, 1, language)

        language = 'en'

        myfile2 = StringIO('new data')
        myfile2.filename = 'other.txt'
        mylocalizedbfile._save_file(myfile2, language,
                                 contributor='contributor')

        myfrfile = StringIO('new french data')
        myfrfile.filename = 'fr_file1.txt'
        mylocalizedbfile._save_file(myfrfile, 'fr',
                                 contributor='contributor')

        myfrfile2 = StringIO('newer french data')
        myfrfile2.filename = 'fr_file2.txt'
        mylocalizedbfile._save_file(myfrfile2, 'fr',
                                 contributor='contributor')

        myfrfile3 = StringIO('latest french data')
        myfrfile3.filename = 'fr_file3.txt'
        mylocalizedbfile._save_file(myfrfile3, 'fr',
                                 contributor='contributor')

        to_remove = mylocalizedbfile._versions[language][1]
        mylocalizedbfile.remove_version(1, language)

        self.failUnless(to_remove in mylocalizedbfile._versions[language])
        self.assertEqual(to_remove.open().read(), '')
        self.assertEqual(to_remove.size, None)
        self.assertEqual(to_remove.removed, True)

        self.assertTrue(mylocalizedbfile.current_version is mylocalizedbfile._versions[language][0])

        myfile3 = StringIO('even newer data')
        myfile3.filename = 'other.txt'
        mylocalizedbfile._save_file(myfile3, language,
                                 contributor='contributor')
        self.assertTrue(mylocalizedbfile.current_version is mylocalizedbfile._versions[language][2])

        self.failUnlessEqual(myfile3.filename, mylocalizedbfile._versions[language][2].filename)
        mylocalizedbfile.remove_version(2, language)
        self.assertTrue(mylocalizedbfile.current_version is mylocalizedbfile._versions[language][0])

        mylocalizedbfile.remove_version(0, language)
        self.assertTrue(mylocalizedbfile.current_version is None)

        language = 'fr'
        rm_ver = mylocalizedbfile._versions[language][1]
        mylocalizedbfile.remove_version(1, language)
        self.failUnless(rm_ver in mylocalizedbfile._versions[language])
        self.assertEqual(rm_ver.open().read(), '')
        self.assertEqual(rm_ver.size, None)
        self.assertEqual(rm_ver.removed, True)

        mylocalizedbfile.get_selected_language = Mock(return_value=language)
        cv = mylocalizedbfile.current_version
        self.assertTrue(cv is mylocalizedbfile._versions[language][2])

        mylocalizedbfile.remove_version(2, language)
        cv = mylocalizedbfile.current_version
        self.assertTrue(cv is mylocalizedbfile._versions[language][0])

        mylocalizedbfile.remove_version(0, language)
        cv = mylocalizedbfile.current_version
        self.assertTrue(cv is None)

    def test_add_no_title(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my_file_for_title.txt'

        myfolder = self.portal.myfolder
        file_id = addNyLocalizedBFile(myfolder, uploaded_file=myfile,
                             submitted=1, contributor='contributor')

        self.assertEqual(file_id, 'my_file_for_title')
        self.assertTrue('my_file_for_title' in myfolder.objectIds())
        myfile = myfolder['my_file_for_title']
        self.assertEqual(myfile.title, 'my_file_for_title')

    def test_add_utf8_filename(self):
        name = u'A\xa7A\xb6A\xa9A\xae_\x86\x90a\x83\x91a\x86\x93a\x99\xaa1.txt'
        myfile = StringIO('hello data!')
        myfile.filename = name.encode('utf-8')

        myfolder = self.portal.myfolder
        file_id = addNyLocalizedBFile(myfolder, uploaded_file=myfile,
                             submitted=1, contributor='contributor')
        self.assertEqual(file_id, 'assapa-c-r-_aaaa1') # as returned by unidecode
