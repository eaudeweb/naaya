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
# Valentin Dumitru, Eau de Web

import re
from unittest import TestSuite, makeSuite
from copy import deepcopy
from StringIO import StringIO

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

from Products.NaayaForum.NyForum import manage_addNyForum
from Products.NaayaForum.NyForumTopic import addNyForumTopic
from Products.NaayaForum.NyForumMessage import addNyForumMessage

class NyForumFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        manage_addNyForum(
                        self.portal,
                        id='forum_id',
                        title='myforum',
                        categories=['Test category', 'Test category 2'],
                        description='Description 1',
                        file_max_size='15',
                        )
        forum = self.portal.forum_id
        myfile = StringIO('some test data')
        myfile.filename = 'the_file.txt'
        addNyForumTopic(forum,
                        id='topic_id',
                        title='topic title',
                        category='Test category',
                        description='Test Description',
                        attachment=myfile,
                        notify=True,
                        sort_reverse=True,
                        )
        topic = forum.topic_id
        addNyForumMessage(topic,
                        id='message_id',
                        title='Message title',
                        description='Message Description',
                        attachment=myfile,
                        notify=True,
                        )
        message = topic.message_id
        message.replyMessage(title='Reply to message_id',
                        description='Reply message description',
                        attachment=myfile,
                        notify=True,
                        )
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['forum_id'])
        transaction.commit()

    def test_edit_forum(self):
        #Check that an unidentified user cannot edit a topic
        self.browser.go('http://localhost/portal/forum_id/edit_html')
        self.assertAccessDenied()

        #Edit forum properties
        self.browser_do_login('admin', '')
        counter = 0
        for link in ['http://localhost/portal/forum_id/edit_html',
                     'http://localhost/portal/forum_id/manage_edit_html']:
            counter += 1
            self.browser.go(link)
            form = self.browser.get_form('frmEdit')

            expected_controls = set([
                'title:utf8:ustring',
                'description:utf8:ustring',
                'categories:utf8:ustring',
                'file_max_size:int',
            ])
            found_controls = set(c.name for c in form.controls)
            self.failUnless(expected_controls.issubset(found_controls),
                'Missing form controls: %s' % repr(expected_controls - found_controls))

            topic = self.portal.forum_id
            file_max_size = topic.file_max_size
            form['title:utf8:ustring'] = 'My forum %s' % counter
            form['categories:utf8:ustring'] = 'Test category\n\rTest category 2\n\rTest category%s' % counter
            form['description:utf8:ustring'] = 'Description %s' % counter
            form['file_max_size:int'] = '%s%s' % (file_max_size, counter)
            self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
            self.browser.submit()
            self.assertEqual(topic.title, 'My forum %s' % counter)
            self.assertEqual(topic.categories, ['Test category', 'Test category 2', 'Test category%s' % counter])
            self.assertEqual(topic.description, 'Description %s' % counter)
            self.assertEqual(topic.file_max_size, file_max_size*10+counter)

        self.browser_do_logout()

    def test_topic_add(self):

        #Check that an unidentified user cannot add a topic
        self.browser.go('http://localhost/portal/forum_id/topic_add_html')
        self.assertAccessDenied()

        #Add topic
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_add_html')
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'title:utf8:ustring',
            'description:utf8:ustring',
            'category:utf8:ustring',
            'notify',
            'attachment',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))
        form['title:utf8:ustring'] = 'Test Add subject'
        form['category:utf8:ustring'] = ['Test category 2']
        form['description:utf8:ustring'] = 'Test Add Description'
        form['notify'] = ['on']
        mytestfile = StringIO('some test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename='the_test_file.txt',
                                                content_type='text/plain; charset=utf-8'
                                                )
        self.browser.clicked(form, self.browser.get_form_field(form, 'attachment'))
        self.browser.submit()

        #Check if the field values are OK
        self.assertEqual(len(self.portal.forum_id.objectIds(['Naaya Forum Topic'])), 2)
        topic = self.portal.forum_id.objectValues(['Naaya Forum Topic'])[1]
        self.assertEqual(topic.title, 'Test Add subject')
        self.assertEqual(topic.category, 'Test category 2')
        self.assertEqual(topic.description, 'Test Add Description')
        filelink = 'http://localhost/portal/forum_id/%s/%s' % (topic.id, filename)
        self.browser.go(filelink)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.assertEqual(headers['content-type'], 'text/plain; charset=utf-8')
        self.failUnlessEqual(html, 'some test data')
        self.assertEqual(topic.notify, True)

        self.browser_do_logout()

    def test_topic_add_error(self):

        #Try to add a topic with a file larger than permitted
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_add_html')
        form = self.browser.get_form('frmAdd')
        form['title:utf8:ustring'] = 'Test subject (Large file)'
        form['category:utf8:ustring'] = ['Test category']
        form['description:utf8:ustring'] = 'Test Description (Large file)'
        form['notify'] = ['on']
        mytestfile = StringIO('some very large test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename='the_test_file.txt',
                                                content_type='text/plain; charset=utf-8'
                                                )
        self.browser.clicked(form, self.browser.get_form_field(form, 'attachment'))
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The attachment is larger than permitted' in html)
        #Check that the filled values are saved
        self.assertEqual(form['title:utf8:ustring'], 'Test subject (Large file)')
        self.assertEqual(form['category:utf8:ustring'], ['Test category'])
        self.assertEqual(form['description:utf8:ustring'], 'Test Description (Large file)')
        self.assertEqual(form['notify'], ['on'])

        self.browser_do_logout()

    def test_topic_edit(self):
        #Check that an unidentified user cannot edit a topic
        self.browser.go('http://localhost/portal/forum_id/topic_id/edit_html')
        self.assertAccessDenied()

        #Edit topic
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_id/edit_html')
        form = self.browser.get_form('frmEdit')
        expected_controls = set([
            'title:utf8:ustring',
            'description:utf8:ustring',
            'category:utf8:ustring',
            'notify',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))
        form['title:utf8:ustring'] = 'Test subject 2'
        form['category:utf8:ustring'] = ['Test category 2']
        form['description:utf8:ustring'] = 'Description'
        form['notify'] = False
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()
        topic = self.portal.forum_id.objectValues(['Naaya Forum Topic'])[0]
        self.assertEqual(topic.title, 'Test subject 2')
        self.assertEqual(topic.category, 'Test category 2')
        self.assertEqual(topic.description, 'Description')
        self.assertEqual(topic.notify, False)

        #Delete Attachment
        form = self.browser.get_form('frmDelete')
        form['ids'] = ['the_file.txt']
        self.browser.clicked(form, self.browser.get_form_field(form, 'ids'))
        self.browser.submit()
        self.assertEqual(len(self.portal.forum_id.topic_id.objectValues('File')), 0)

      #logout
        self.browser_do_logout()

    def test_topic_edit_error(self):
        #Edit topic error (attachment too large)
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_id/edit_html')

        form = self.browser.get_form('addAttachment')
        mytestfile = StringIO('some very large test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename='the_test_file.txt',
                                                content_type='text/plain; charset=utf-8'
                                                )
        self.browser.clicked(form, self.browser.get_form_field(form, 'attachment'))
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The attachment is larger than permitted' in html)

      #logout
        self.browser_do_logout()

    def test_message_add(self):
        #Add topic
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_id/message_add_html')
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'title:utf8:ustring',
            'description:utf8:ustring',
            'attachment',
            'notify',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        form['title:utf8:ustring'] = 'Message title 2'
        form['description:utf8:ustring'] = 'Message description 2'
        form['notify'] = ['on']
        mytestfile = StringIO('some test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename='the_test_file.txt',
                                                content_type='text/plain; charset=utf-8'
                                                )
        self.browser.clicked(form, self.browser.get_form_field(form, 'attachment'))
        self.browser.submit()

        #Check if the field values are OK
        self.assertEqual(len(self.portal.forum_id.topic_id.objectIds(['Naaya Forum Message'])), 3)
        message = self.portal.forum_id.topic_id.objectValues(['Naaya Forum Message'])[2]
        self.assertEqual(message.title, 'Message title 2')
        self.assertEqual(message.description, 'Message description 2')
        filelink = 'http://localhost/portal/forum_id/topic_id/%s/%s' % (message.id, filename)
        self.browser.go(filelink)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.assertEqual(headers['content-type'], 'text/plain; charset=utf-8')
        self.failUnlessEqual(html, 'some test data')
        self.assertEqual(message.notify, True)

        self.browser_do_logout()

    def test_message_add_error(self):
        #Add topic
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_id/message_add_html')
        form = self.browser.get_form('frmAdd')
        form['title:utf8:ustring'] = 'Message title 2'
        form['description:utf8:ustring'] = 'Message description 2'
        form['notify'] = ['on']
        mytestfile = StringIO('some very very big test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename='the_test_file.txt',
                                                content_type='text/plain; charset=utf-8'
                                                )
        self.browser.clicked(form, self.browser.get_form_field(form, 'attachment'))
        self.browser.submit()

        #Check if the error message is returned
        html = self.browser.get_html()
        self.failUnless('The attachment is larger than permitted' in html)

        #Check that the filled values are saved
        form = self.browser.get_form('frmAdd')
        self.assertEqual(form['title:utf8:ustring'], 'Message title 2')
        self.assertEqual(form['description:utf8:ustring'], 'Message description 2')
        self.assertEqual(form['notify'], ['on'])

        self.browser_do_logout()

    def test_message_delete(self):
        #Check that an unidentified user cannot delete a message
        self.browser.go('http://localhost/portal/forum_id/topic_id/message_id/delete_html')
        self.assertAccessDenied()

        #Delete message
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_id/message_id/delete_html')
        form = self.browser.get_form('frmConfirm')
        form['nodes'] = ['on']
        self.browser.clicked(form, self.browser.get_form_field(form, 'confirm'))
        self.browser.submit()
        self.assertEqual(len(self.portal.forum_id.topic_id.objectIds(['Naaya Forum Message'])), 0)

        self.browser_do_logout()

    def test_message_edit(self):
        #Check that an unidentified user cannot edit a message
        self.browser.go('http://localhost/portal/forum_id/topic_id/message_id/edit_html')
        self.assertAccessDenied()

        #Add topic
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_id/message_id/edit_html')
        form = self.browser.get_form('frmEdit')
        expected_controls = set([
            'title:utf8:ustring',
            'description:utf8:ustring',
            'notify',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        form['title:utf8:ustring'] = 'Message title modified'
        form['description:utf8:ustring'] = 'Message description modified'
        form['notify'] = []
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        self.browser.submit()

        #Check if the field values are OK
        message = self.portal.forum_id.topic_id.message_id
        self.assertEqual(message.title, 'Message title modified')
        self.assertEqual(message.description, 'Message description modified')
        self.assertEqual(message.notify, False)

        self.browser_do_logout()

    def test_message_edit_error(self):
        #Fail to upload a too large attachment
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_id/message_id/edit_html')
        form = self.browser.get_form('frmAddAttachment')

        mytestfile = StringIO('some very very big test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename='the_test_file.txt',
                                                content_type='text/plain; charset=utf-8'
                                                )
        self.browser.clicked(form, self.browser.get_form_field(form, 'attachment'))
        self.browser.submit()

        #Check if the error message is returned
        html = self.browser.get_html()
        self.failUnless('The attachment is larger than permitted' in html)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyForumFunctionalTestCase))
    return suite
