from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from StringIO import StringIO
from datetime import datetime
from naaya.content.bfile.NyBlobFile import NyBlobFile
from naaya.content.bfile.bfile_item import LocalizedFileDownload
from naaya.content.bfile.bfile_item import NyBFile
from naaya.content.bfile.bfile_item import addNyBFile
from persistent.list import PersistentList
import pytz


class MockRequest(object):
    def __init__(self):
        self.headers={}

    def get_header(self, name):
        return self.headers.get(name)

    def set_header(self, name, value):
        self.headers[name] = value


class MockResponse(object):
    def __init__(self, stream=False):
        self.headers = {}
        if stream:
            self._streaming = 'whatever value'

    def setHeader(self, key, value):
        self.headers[key] = value


class NyBFileTestCase(NaayaTestCase):
    """ TestCase for Naaya BFile object """

    def get_storage(self, bfile):
        return bfile.versions_store.get(bfile.get_selected_language(), {})

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)

        self._old_get_selected_language = NyBFile.get_selected_language
        NyBFile.get_selected_language = lambda self: 'en'

    def beforeTearDown(self):
        NyBFile.get_selected_language = self._old_get_selected_language
        self.portal.manage_delObjects(['myfolder'])

    def add_bfile(self, **kwargs):
        addNyBFile(self.portal.myfolder, submitted=1, contributor='contributor', **kwargs)

    def test_add_blank(self):
        self.add_bfile(id='mybfile', title='My bfile')
        self.assertTrue('mybfile' in self.portal.myfolder.objectIds())

        mybfile = self.portal.myfolder.mybfile
        self.assertTrue(mybfile.id, 'mybfile')
        self.assertTrue(mybfile.title, 'My bfile')
        self.assertEqual(len(self.get_storage(mybfile)), 0)
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

        vstore = mybfile._versions_i18n[mybfile.get_selected_language()]
        self.assertEqual(len(vstore), 1)

        bf = vstore[0].__of__(mybfile)
        path1 = mybfile.current_version.getPhysicalPath()
        path2 = bf.getPhysicalPath()
        self.assertTrue(path1 == path2)

        ver = mybfile.current_version
        self.assertTrue(now_pre <= pytz.utc.localize(ver.timestamp) <= now_post)
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

        vstore = mybfile._versions_i18n[mybfile.get_selected_language()]
        self.assertEqual(len(vstore), 2)
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
        mybfile._save_file(myfile2, contributor='contributor')

        lang = mybfile.get_selected_language()
        mybfile.remove_version(1)
        rm_ver = mybfile._versions_i18n[lang][1]
        self.assertEqual(rm_ver.open().read(), '')
        self.assertEqual(rm_ver.size, None)
        self.assertEqual(rm_ver.removed, True)
        vstore = mybfile._versions_i18n[lang]
        path1 = mybfile.current_version.getPhysicalPath()
        path2 = vstore[0].__of__(mybfile).getPhysicalPath()
        self.assertTrue(path1 == path2)

        myfile3 = StringIO('even newer data')
        myfile3.filename = 'other.txt'
        mybfile._save_file(myfile3,
                           contributor='contributor')
        path1 = mybfile.current_version.getPhysicalPath()
        path2 = vstore[2].__of__(mybfile).getPhysicalPath()
        self.assertTrue(path1 == path2)

        self.assertTrue(len(list(mybfile.all_versions())) == 3)
        mybfile.remove_version(2)
        path1 = mybfile.current_version.getPhysicalPath()
        path2 = vstore[0].__of__(mybfile).getPhysicalPath()
        self.assertTrue(path1 == path2)

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

    def make_blobfile(self,
                      filename='bf.txt',
                      content='hello world',
                      content_type='text/plain'):
        bf = NyBlobFile(
            filename=filename, content_type=content_type,
            timestamp=datetime.utcnow(), contributor='tester')
        bf.removed = False
        bf.size = len(content)
        f = bf.open_write()
        f.write(content)
        f.close()
        return bf

    def test_unmigrated_version(self):
        self.add_bfile(id='mybfile', title='My bfile')
        mybfile = self.portal.myfolder.mybfile
        bf = self.make_blobfile()
        mybfile._versions = PersistentList()
        mybfile._versions.append(bf)
        assert mybfile.current_version == bf
        assert mybfile.current_version_download_url() == \
            'http://nohost/portal/myfolder/mybfile/download/en/1/bf.txt'

    def test_unmigrated_version_with_new_version(self):
        self.add_bfile(id='mybfile', title='My bfile')
        mybfile = self.portal.myfolder.mybfile
        bf = self.make_blobfile()
        mybfile._versions = PersistentList()
        mybfile._versions.append(bf)

        myfile2 = StringIO('new data')
        myfile2.filename = 'other.txt'
        mybfile._save_file(myfile2, contributor='contributor')

        assert len(list(mybfile.all_versions())) == 2
        assert mybfile.current_version.raw_data() == 'new data'

        assert mybfile.current_version_download_url() == \
            'http://nohost/portal/myfolder/mybfile/download/en/2/other.txt'

    def test_download_unmigrated_version(self):
        self.add_bfile(id='mybfile', title='My bfile')
        mybfile = self.portal.myfolder.mybfile
        bf = self.make_blobfile()
        mybfile._versions = PersistentList()
        mybfile._versions.append(bf)

        downloader = LocalizedFileDownload()
        request = MockRequest()
        request.form = {'action': 'download'}
        request.RESPONSE = MockResponse()

        assert downloader(mybfile, ['bf.txt'], request) == "hello world"
        assert downloader(mybfile, ['1', 'bf.txt'], request) ==  "hello world"
        assert downloader(mybfile, ['en', '1', 'bf.txt'], request) ==\
            'hello world'
        assert downloader(mybfile, ['fr', '1', 'bf.txt'], request) ==\
            'hello world'

