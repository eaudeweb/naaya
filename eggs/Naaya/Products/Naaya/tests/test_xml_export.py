"""Naaya XML (.nyexp) export and import of binary content."""
import base64
import re

from OFS.Image import manage_addImage

from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.document.document_item import addNyDocument
from naaya.content.file.file_item import addNyFile
from naaya.content.story.story_item import addNyStory

DATA = 'café ș\n'.encode('utf-8') + bytes(range(256))
GIF = (b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!'
       b'\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00'
       b'\x00\x02\x02D\x01\x00;')
GIF2 = GIF[:-1] + b'\x00;'


def decoded_attr(xml, name):
    """ Decode the base64 value of the first `name` attribute in `xml` """
    return base64.decodebytes(re.search(r'%s="([^"]*)"' % name,
                                        xml).group(1).encode('ascii'))


def img_ids(xml):
    return re.findall(r'<img param="0" id="([^"]*)"', xml)


class XMLExportTest(NaayaTestCase):

    def afterSetUp(self):
        self.login()
        addNyFolder(self.portal.info, 'src', contributor='admin', submitted=1)
        self.src = self.portal.info.src

    def beforeTearDown(self):
        self.logout()

    def _add_document(self):
        addNyDocument(self.src, id='mydoc', title='Document ș',
                      body='<p>Body ș</p>', contributor='admin', submitted=1)
        manage_addImage(self.src.mydoc, 'doc.gif', GIF2)
        return self.src.mydoc

    def _add_story(self):
        addNyStory(self.src, id='mystory', title='Story ș',
                   body='<p>Story body</p>', contributor='admin', submitted=1)
        manage_addImage(self.src.mystory, 'story.gif', GIF2)
        return self.src.mystory

    def _import(self, content):
        xml = ('<?xml version="1.0" encoding="utf-8"?><export>%s</export>'
               % content)
        addNyFolder(self.portal.info, 'dst', contributor='admin', submitted=1)
        dst = self.portal.info.dst
        dst.manage_import(source='file', file=xml.encode('utf-8'))
        return dst

    def test_file_data(self):
        addNyFile(self.src, id='myfile', title='My file', contributor='admin',
                  submitted=1)
        self.src.myfile.update_data(DATA, 'application/octet-stream')
        tag = self.src.myfile.export_this_tag_custom()
        self.assertEqual(decoded_attr(tag, 'file'), DATA)

    def test_folder_images(self):
        manage_addImage(self.src, 'pic.gif', GIF)
        body = self.src.export_this_body_custom()
        self.assertEqual(decoded_attr(body, 'content'), GIF)

    def test_document_images(self):
        manage_addImage(self.src, 'pic.gif', GIF)
        body = self._add_document().export_this_body_custom()
        self.assertEqual(img_ids(body), ['doc.gif'])
        self.assertEqual(decoded_attr(body, 'content'), GIF2)

    def test_story_images(self):
        manage_addImage(self.src, 'pic.gif', GIF)
        body = self._add_story().export_this_body_custom()
        self.assertEqual(img_ids(body), ['story.gif'])
        self.assertEqual(decoded_attr(body, 'content'), GIF2)

    def test_import_file(self):
        addNyFile(self.src, id='myfile', title='My file ș', contributor='admin',
                  submitted=1)
        self.src.myfile.update_data(DATA, 'application/octet-stream')
        copy = self._import(self.src.myfile.export_this()).myfile
        self.assertEqual(copy.title, 'My file ș')
        self.assertEqual(bytes(copy.get_data()), DATA)
        self.assertEqual(copy.getContentType(), 'application/octet-stream')

    def test_import_document(self):
        dst = self._import(self._add_document().export_this())
        self.assertEqual(dst.mydoc.title, 'Document ș')
        self.assertEqual(dst.mydoc.body, '<p>Body ș</p>')
        self.assertEqual(dst.mydoc.objectIds(['Image']), ['doc.gif'])
        self.assertEqual(bytes(dst.mydoc['doc.gif'].data), GIF2)

    def test_import_story(self):
        dst = self._import(self._add_story().export_this())
        self.assertEqual(dst.mystory.title, 'Story ș')
        self.assertEqual(dst.mystory.objectIds(['Image']), ['story.gif'])
        self.assertEqual(bytes(dst.mystory['story.gif'].data), GIF2)

    def test_import_folder(self):
        self.src.custom_index = 'site:info'
        manage_addImage(self.src, 'pic.gif', GIF)
        addNyFile(self.src, id='myfile', title='My file', contributor='admin',
                  submitted=1)
        self.src.myfile.update_data(DATA, 'application/octet-stream')
        self._add_document()
        copy = self._import(self.src.export_this()).src
        self.assertEqual(copy.meta_type, 'Naaya Folder')
        self.assertEqual(copy.custom_index, 'site:info')
        self.assertEqual(sorted(copy.objectIds(['Image'])), ['pic.gif'])
        self.assertEqual(bytes(copy.myfile.get_data()), DATA)
        self.assertEqual(copy.mydoc.objectIds(['Image']), ['doc.gif'])

    def test_import_folder_old_publicinterface(self):
        xml = ('<ob meta_type="Naaya Folder" param="0" id="old" sortorder="100"'
               ' contributor="admin" approved="1" approved_by="admin"'
               ' releasedate="" discussion="0" publicinterface="1"'
               ' maintainer_email="" folder_meta_types="">'
               '<title lang="en"><![CDATA[Old]]></title></ob>')
        copy = self._import(xml).old
        self.assertEqual(copy.custom_index, 'local:index')
        self.assertIsNotNone(copy._getOb('index', None))
