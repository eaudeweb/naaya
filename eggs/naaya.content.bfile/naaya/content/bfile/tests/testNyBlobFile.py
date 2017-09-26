from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from StringIO import StringIO
from Testing import ZopeTestCase
from naaya.content.bfile.NyBlobFile import NyBlobFile, make_blobfile
import transaction


class MockResponse(object):
    def __init__(self, stream=False):
        self.headers = {}
        if stream:
            self._streaming = 'whatever value'

    def setHeader(self, key, value):
        self.headers[key] = value


class MockRequest(object):
    def __init__(self):
        self.headers={}

    def get_header(self, name):
        return self.headers.get(name)

    def set_header(self, name, value):
        self.headers[name] = value


class NyBlobFileTestCase(ZopeTestCase.TestCase):
    """ CRUD test for NyBlobFile """

    def test_create_update(self):
        # create plain NyBlobFile
        bf = NyBlobFile()
        self.assertEqual(bf.content_type, 'application/octet-stream')
        self.assertEqual(bf.filename, None)
        self.assertEqual(bf.open().read(), '')

        # create NyBlobFile with properties and content
        bf2 = NyBlobFile(filename='my_file.txt', content_type='text/plain')
        f = bf2.open_write()
        f.write('hello world')
        f.close()
        self.assertEqual(bf2.content_type, 'text/plain')
        self.assertEqual(bf2.filename, 'my_file.txt')
        self.assertEqual(bf2.open().read(), 'hello world')

        # change properties and content
        f = bf2.open_write()
        f.write('other content')
        f.close()
        bf2.filename = 'other_file.txt'
        bf2.content_type = 'text/html'
        self.assertEqual(bf2.content_type, 'text/html')
        self.assertEqual(bf2.filename, 'other_file.txt')
        self.assertEqual(bf2.open().read(), 'other content')

    def test_factory(self):
        data = 'some test data'
        f = StringIO(data)
        f.filename = 'my.txt'
        f.headers = {'content-type': 'text/plain'}

        bf = make_blobfile(f, somerandomkw='thevalue')

        self.assertEqual(bf.open().read(), data)
        self.assertEqual(bf.content_type, 'text/plain')
        self.assertEqual(bf.filename, 'my.txt')
        self.assertEqual(bf.somerandomkw, 'thevalue')

    def test_guess_mimetype(self):
        f = StringIO('some test image')
        f.filename = 'photo.jpg'
        bf = make_blobfile(f)
        self.assertEqual(bf.content_type, 'image/jpeg')

    def test_factory_ie6_filename(self):
        data = 'some test data'
        f = StringIO(data)
        f.filename = r'C:\\Documents and Settings\\uzer\\Desktop\\data.txt'
        f.headers = {'content-type': 'text/plain'}

        bf = make_blobfile(f, somerandomkw='thevalue')

        self.assertEqual(bf.open().read(), data)
        self.assertEqual(bf.content_type, 'text/plain')
        self.assertEqual(bf.filename, 'data.txt')
        self.assertEqual(bf.somerandomkw, 'thevalue')

    def test_send_data(self):
        data = 'some test data'
        f = StringIO(data)
        f.filename = 'my.txt'
        f.headers = {'content-type': 'text/plain'}

        bf = make_blobfile(f, somerandomkw='thevalue')

        ok_headers = {'Content-Length': 14,
                      'Content-Type': 'text/plain',
                      'Content-Disposition': ("attachment;filename*="
                                              "UTF-8''my.txt")}
        response = MockResponse()
        ret = bf.send_data(response)
        self.assertEqual(response.headers, ok_headers)
        self.assertEqual(ret, 'some test data')

        ok_headers['Content-Disposition'] = "attachment"
        ret = bf.send_data(response, set_filename=False)
        self.assertEqual(response.headers, ok_headers)
        self.assertEqual(ret, 'some test data')

        self.assertEqual(response.headers.get('X-Sendfile'), None)
        request = MockRequest()
        request.set_header('X-NaayaEnableSendfile', 'on')
        ret = bf.send_data(response, REQUEST=request)
        self.assertEqual(ret, "[body should be replaced by front-end server]")
        self.assertEqual(response.headers.get('X-Sendfile'),
                         bf._current_filename())


class NyBlobFileTransactionsTestCase(NaayaTestCase):

    def afterSetUp(self):
        self.portal.info.contact._theblob = NyBlobFile(filename='a.txt')
        f = self.portal.info.contact._theblob.open_write()
        f.write('some content')
        f.close()
        transaction.commit()

    def beforeTearDown(self):
        del self.portal.info.contact._theblob
        transaction.commit()

    def test_transaction_commit(self):
        bf = self.portal.info.contact._theblob
        bf.filename = 'b.txt'
        bf.content_type = 'text/plain'
        f = bf.open_write()
        f.write('some other content')
        f.close()

        # commit the transaction and deactivate the parent object
        # to make sure the NyBlobFile object was persisted
        transaction.commit()
        self.portal.info.contact._p_deactivate()

        bf = self.portal.info.contact._theblob
        self.assertEqual(bf.filename, 'b.txt')
        self.assertEqual(bf.content_type, 'text/plain')

    def test_transaction_abort(self):
        bf = self.portal.info.contact._theblob
        bf.filename = 'b.txt'
        bf.content_type = 'text/plain'
        f = bf.open_write()
        f.write('some other content')
        f.close()

        # abort the transaction and keep using our `bf` reference
        # to make sure the NyBlobFile object was rolled back
        transaction.abort()

        self.assertEqual(bf.filename, 'a.txt')
        self.assertEqual(bf.content_type, 'application/octet-stream')

