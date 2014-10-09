#from unittest import TestSuite, makeSuite
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from StringIO import StringIO
from datetime import datetime
from naaya.content.bfile.bfile_item import addNyBFile


class NyBFileTestCase(NaayaTestCase):
    """ TestCase for Naaya BFile object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])

    def add_bfile(self, **kwargs):
        addNyBFile(self.portal.myfolder, submitted=1, contributor='contributor', **kwargs)

    def test_add_blank(self):
        self.add_bfile(id='mybfile', title='My bfile')
        self.assertTrue('mybfile' in self.portal.myfolder.objectIds())

        mybfile = self.portal.myfolder.mybfile
        self.assertTrue(mybfile.id, 'mybfile')
        self.assertTrue(mybfile.title, 'My bfile')
        self.assertEqual(len(mybfile._versions), 0)
        self.assertEqual(mybfile.current_version, None)

    def test_add_with_file(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.jpg'
        myfile.headers = {'content-type': 'image/jpeg'}

        tzinfo = self.portal.get_tzinfo()
        now_pre = datetime.now(tzinfo)
        self.add_bfile(id='mybfile', title='My bfile', uploaded_file=myfile)
        now_post = datetime.now(tzinfo)

        mybfile = self.portal.myfolder.mybfile
        self.assertTrue(mybfile.id, 'mybfile')
        self.assertTrue(mybfile.title, 'My bfile')
        self.assertEqual(len(mybfile._versions), 1)
        self.assertTrue(mybfile.current_version.getPhysicalPath() ==
                        mybfile._versions[0].__of__(mybfile).getPhysicalPath())

        ver = mybfile.current_version
        self.assertTrue(now_pre <= ver.timestamp <= now_post)
        self.assertEqual(ver.open().read(), 'hello data!')
        self.assertEqual(ver.filename, 'my.jpg')
        self.assertEqual(ver.size, 11)
        self.assertEqual(ver.content_type, 'image/jpeg')

    def test_add_with_file_with_fake_content_type(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.pdf'
        myfile.headers = {'content-type': 'image/jpeg'}

        self.add_bfile(id='mybfile', title='My bfile', uploaded_file=myfile)
        mybfile = self.portal.myfolder.mybfile
        ver = mybfile.current_version

        self.assertEqual(ver.content_type, 'application/pdf')

    def test_change_file(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.txt'
        self.add_bfile(id='mybfile', title='My bfile', uploaded_file=myfile)
        mybfile = self.portal.myfolder.mybfile

        myfile2 = StringIO('new data')
        myfile2.filename = 'other.txt'
        mybfile._save_file(myfile2,
                           contributor='contributor')

        self.assertEqual(len(mybfile._versions), 2)
        cv = mybfile.current_version
        self.assertEqual(cv.filename, 'other.txt')
        self.assertEqual(cv.size, 8)
        self.assertEqual(cv.open().read(), 'new data')

    def test_remove_version(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my.txt'
        self.add_bfile(id='mybfile', title='My bfile', uploaded_file=myfile)
        mybfile = self.portal.myfolder.mybfile

        myfile2 = StringIO('new data')
        myfile2.filename = 'other.txt'
        mybfile._save_file(myfile2,
                           contributor='contributor')

        mybfile.remove_version(1)
        rm_ver = mybfile._versions[1]
        self.assertEqual(rm_ver.open().read(), '')
        self.assertEqual(rm_ver.size, None)
        self.assertEqual(rm_ver.removed, True)
        self.assertTrue(mybfile.current_version.getPhysicalPath() ==
                        mybfile._versions[0].__of__(mybfile).getPhysicalPath())

        myfile3 = StringIO('even newer data')
        myfile3.filename = 'other.txt'
        mybfile._save_file(myfile3,
                           contributor='contributor')
        self.assertTrue(mybfile.current_version.getPhysicalPath() ==
                        mybfile._versions[2].__of__(mybfile).getPhysicalPath())

        mybfile.remove_version(2)
        self.assertTrue(mybfile.current_version.getPhysicalPath() ==
                        mybfile._versions[0].__of__(mybfile).getPhysicalPath())

        mybfile.remove_version(0)
        self.assertTrue(mybfile.current_version is None)

    def test_add_no_title(self):
        myfile = StringIO('hello data!')
        myfile.filename = 'my_file_for_title.txt'

        myfolder = self.portal.myfolder
        file_id = addNyBFile(myfolder, uploaded_file=myfile,
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
        file_id = addNyBFile(myfolder, uploaded_file=myfile,
                             submitted=1, contributor='contributor')
        self.assertEqual(file_id, 'assapa-c-r-_aaaa1') # as returned by unidecode

