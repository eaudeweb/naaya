"""Tests for code paths changed in the Python 3 port."""
import os
import shutil
import tempfile
from io import BytesIO
from unittest import mock

import openpyxl

from Products.Naaya import NyFolder as NyFolderModule
from Products.Naaya.NyFolder import addNyFolder
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase


class RestrictionRolesTest(NaayaTestCase):

    def test_get_valid_roles(self):
        roles = self.portal.info.get_valid_roles()
        self.assertIn('Contributor', roles)
        for role in ('Administrator', 'Anonymous', 'Manager', 'Owner'):
            self.assertNotIn(role, roles)


class MainTopicsTest(NaayaTestCase):

    def afterSetUp(self):
        addNyFolder(self.portal, 'topic2', contributor='admin', submitted=1)
        self.portal.maintopics = ['info', 'topic2', 'missing']

    def test_get_main_topics(self):
        self.assertEqual(self.portal.getMainTopics(),
                         [self.portal.info, self.portal.topic2])

    def test_order_main_topics(self):
        self.portal.maintopics = ['info', 'topic2']
        self.portal.admin_ordermaintopics('topic2|info')
        self.assertEqual(self.portal.maintopics, ['topic2', 'info'])
        self.assertRaises(ValueError, self.portal.admin_ordermaintopics,
                          'topic2')
        self.assertEqual(self.portal.maintopics, ['topic2', 'info'])


class NetworkPortalsTest(NaayaTestCase):

    def test_delete(self):
        site = self.portal
        site.add_networkportal_item('p1', 'Portal 1', 'http://p1', ['en'])
        site.add_networkportal_item('p2', 'Portal 2', 'http://p2', ['en'])
        site.delete_networkportal_item(['p1'])
        self.assertEqual([x.id for x in site.get_networkportals_list()],
                         ['p2'])


class TagCloudTest(NaayaTestCase):

    def test_tag_cloud(self):
        scores = {'apple': 1, 'banana': 9, 'cherry': 6}
        lexicon = mock.Mock()
        lexicon.getWordsForRightTruncation.side_effect = (
            lambda c: [w for w in sorted(scores) if w.startswith(c)])
        index = mock.Mock(id='tags_en')
        index.getLexicon.return_value = lexicon
        index.getDocumentsForWord.side_effect = lambda w: list(range(scores[w]))
        catalog = self.portal.getCatalogTool()
        with mock.patch.object(type(catalog.aq_base), 'getIndexObjects',
                               return_value=[index]):
            cloud = self.portal.info.getTagCloud()
        self.assertEqual(sorted(cloud, key=lambda t: t[1]),
                         [(4, 'apple'), (1, 'banana'), (2, 'cherry')])


class BulkMailExportTest(NaayaTestCase):

    @mock.patch('Products.NaayaCore.EmailTool.EmailTool.get_bulk_emails')
    def test_export(self, get_bulk_emails):
        get_bulk_emails.return_value = [
            {'filename': 'a.eml', 'subject': 'Hello ș',
             'recipients': ['a@example.com']}]
        request = self.portal.REQUEST
        request.form.update({'headers': 'Subject,Recipients',
                             'keys': 'subject,recipients'})
        data = self.portal.admin_bulk_mail_list_export(request,
                                                       request.RESPONSE)
        response = request.RESPONSE
        self.assertEqual(response.getHeader('Content-Type'),
                         'application/vnd.openxmlformats-officedocument'
                         '.spreadsheetml.sheet')
        self.assertIn('admin_bulk_email_list.xlsx',
                      response.getHeader('Content-Disposition'))
        ws = openpyxl.load_workbook(BytesIO(data)).worksheets[0]
        self.assertEqual([[c.value for c in row] for row in ws.iter_rows()],
                         [['Subject', 'Recipients'],
                          ['Hello ș', 'a@example.com']])


class FolderWriteImportTest(NaayaTestCase):

    def afterSetUp(self):
        self.login()
        self.client_home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.client_home)

    def beforeTearDown(self):
        self.logout()

    def test_write_import(self):
        xml = ('<?xml version="1.0" encoding="iso-8859-1"?><export>'
               '<ob meta_type="Naaya URL" param="0" id="myurl" sortorder="100"'
               ' contributor="admin" approved="1" approved_by="admin"'
               ' releasedate="" discussion="0" locator="" validation_status="0"'
               ' validation_date="" validation_by="" validation_comment="">'
               '<title lang="en"><![CDATA[Caf\xe9]]></title></ob></export>')
        with open(os.path.join(self.client_home, 'data.nyexp'), 'wb') as f:
            f.write(xml.encode('iso-8859-1'))
        with mock.patch.object(NyFolderModule, 'CLIENT_HOME',
                               self.client_home):
            self.portal.info.write_import(REQUEST={'id': 'data'})
        self.assertEqual(self.portal.info.myurl.title, 'Caf\xe9')


class GrabFromUrlTest(NaayaTestCase):
    """ grabFromUrl uses urllib.request (FancyURLopener is gone in Python 3.14) """

    def afterSetUp(self):
        import threading
        from http.server import BaseHTTPRequestHandler, HTTPServer

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/file.txt':
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'grabbed data')
                else:
                    self.send_error(404)

            def log_message(self, *args):
                pass

        self.server = HTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = 'http://127.0.0.1:%d' % self.server.server_port

    def beforeTearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_grab(self):
        self.assertEqual(self.portal.grabFromUrl(self.base + '/file.txt'),
                         (b'grabbed data', 'text/plain'))

    def test_not_found(self):
        self.assertEqual(self.portal.grabFromUrl(self.base + '/missing'),
                         (None, 'text/x-unknown-content-type'))
