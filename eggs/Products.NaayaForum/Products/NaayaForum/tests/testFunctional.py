from unittest import TestSuite, TestLoader
from io import BytesIO

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

from Products.NaayaForum.NyForum import addNyForum
from Products.NaayaForum.NyForumTopic import addNyForumTopic
from Products.NaayaForum.NyForumMessage import addNyForumMessage
from naaya import sql

class NyForumFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        addNyForum(
                        self.portal,
                        id='forum_id',
                        title='myforum',
                        categories=['Test category', 'Test category 2'],
                        description='Description 1',
                        file_max_size='15',
                        )
        forum = self.portal.forum_id
        myfile = BytesIO(b'some test data')
        myfile.filename = 'the_file.txt'
        addNyForumTopic(forum,
                        id='topic_id',
                        title='topic title',
                        category='Test category',
                        description='Test Description',
                        attachment=myfile,
                        sort_reverse=True,
                        )
        topic = forum.topic_id
        addNyForumMessage(topic,
                        id='message_id',
                        title='Message title',
                        description='Message Description',
                        attachment=myfile,
                        )
        message = topic.message_id
        message.replyMessage(title='Reply to message_id',
                        description='Reply message description',
                        attachment=myfile,
                        )
        transaction.commit()

    def beforeTearDown(self):
        # get sqlite db (if any) or create one
        cursor = self.portal.forum_id._getStatisticsContainerCursor()
        self.portal.forum_id._removeStatisticsContainer()
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
                'title:utf8:string',
                'description:utf8:string',
                'categories:utf8:string',
                'file_max_size:int',
            ])
            found_controls = set(c.name for c in form.controls)
            self.assertTrue(expected_controls.issubset(found_controls),
                'Missing form controls: %s' % repr(expected_controls - found_controls))

            topic = self.portal.forum_id
            file_max_size = topic.file_max_size
            form['title:utf8:string'] = 'My forum %s' % counter
            form['categories:utf8:string'] = 'Test category\n\rTest category 2\n\rTest category%s' % counter
            form['description:utf8:string'] = 'Description %s' % counter
            form['file_max_size:int'] = '%s%s' % (file_max_size, counter)
            self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
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
            'title:utf8:string',
            'description:utf8:string',
            'category:utf8:string',
            'attachment',
        ])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))
        form['title:utf8:string'] = 'Test Add subject'
        form['category:utf8:string'] = ['Test category 2']
        form['description:utf8:string'] = 'Test Add Description'
        mytestfile = BytesIO(b'some test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename=filename,
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
        self.assertEqual(html, 'some test data')

        # Check hit counter
        topiclink = 'http://localhost/portal/forum_id/%s' % topic.id
        gethits = lambda: self.portal.forum_id.getTopicHits(topic.id)
        self.assertEqual(gethits(), 0)
        for i in range(13):
            self.browser.go(topiclink)
        self.assertEqual(gethits(), 13)

        self.browser_do_logout()

    def test_topic_add_error(self):

        #Try to add a topic with a file larger than permitted
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_add_html')
        form = self.browser.get_form('frmAdd')
        form['title:utf8:string'] = 'Test subject (Large file)'
        form['category:utf8:string'] = ['Test category']
        form['description:utf8:string'] = 'Test Description (Large file)'
        mytestfile = BytesIO(b'some very large test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename=filename,
                                                content_type='text/plain; charset=utf-8'
                                                )
        self.browser.clicked(form, self.browser.get_form_field(form, 'attachment'))
        self.browser.submit()
        html = self.browser.get_html()
        self.assertTrue('The attachment is larger than permitted' in html)
        #Check that the filled values are saved
        self.assertEqual(form['title:utf8:string'], 'Test subject (Large file)')
        self.assertEqual(form['category:utf8:string'], 'Test category')
        self.assertEqual(form['description:utf8:string'], 'Test Description (Large file)')

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
            'title:utf8:string',
            'description:utf8:string',
            'category:utf8:string',
        ])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))
        form['title:utf8:string'] = 'Test subject 2'
        form['category:utf8:string'] = ['Test category 2']
        form['description:utf8:string'] = 'Description'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:string'))
        self.browser.submit()
        topic = self.portal.forum_id.objectValues(['Naaya Forum Topic'])[0]
        self.assertEqual(topic.title, 'Test subject 2')
        self.assertEqual(topic.category, 'Test category 2')
        self.assertEqual(topic.description, 'Description')

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
        mytestfile = BytesIO(b'some very large test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename=filename,
                                                content_type='text/plain; charset=utf-8'
                                                )
        self.browser.clicked(form, self.browser.get_form_field(form, 'attachment'))
        self.browser.submit()
        html = self.browser.get_html()
        self.assertTrue('The attachment is larger than permitted' in html)

      #logout
        self.browser_do_logout()

    def test_message_add(self):
        #Add topic
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_id/message_add_html')
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'title:utf8:string',
            'description:utf8:string',
            'attachment',
        ])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        form['title:utf8:string'] = 'Message title 2'
        form['description:utf8:string'] = 'Message description 2'
        mytestfile = BytesIO(b'some test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename=filename,
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
        self.assertEqual(html, 'some test data')

        self.browser_do_logout()

    def test_message_add_error(self):
        #Add topic
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_id/message_add_html')
        form = self.browser.get_form('frmAdd')
        form['title:utf8:string'] = 'Message title 2'
        form['description:utf8:string'] = 'Message description 2'
        mytestfile = BytesIO(b'some very very big test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename=filename,
                                                content_type='text/plain; charset=utf-8'
                                                )
        self.browser.clicked(form, self.browser.get_form_field(form, 'attachment'))
        self.browser.submit()

        #Check if the error message is returned
        html = self.browser.get_html()
        self.assertTrue('The attachment is larger than permitted' in html)

        #Check that the filled values are saved
        form = self.browser.get_form('frmAdd')
        self.assertEqual(form['title:utf8:string'], 'Message title 2')
        self.assertEqual(form['description:utf8:string'].strip(),
                         'Message description 2')

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
            'title:utf8:string',
            'description:utf8:string',
        ])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        form['title:utf8:string'] = 'Message title modified'
        form['description:utf8:string'] = 'Message description modified'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        self.browser.submit()

        #Check if the field values are OK
        message = self.portal.forum_id.topic_id.message_id
        self.assertEqual(message.title, 'Message title modified')
        self.assertEqual(message.description, 'Message description modified')

        self.browser_do_logout()

    def test_message_edit_error(self):
        #Fail to upload a too large attachment
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/forum_id/topic_id/message_id/edit_html')
        form = self.browser.get_form('frmAddAttachment')

        mytestfile = BytesIO(b'some very very big test data')
        filename='the_test_file.txt'
        form.find_control('attachment').add_file(
                                                mytestfile,
                                                filename=filename,
                                                content_type='text/plain; charset=utf-8'
                                                )
        self.browser.clicked(form, self.browser.get_form_field(form, 'attachment'))
        self.browser.submit()

        #Check if the error message is returned
        html = self.browser.get_html()
        self.assertTrue('The attachment is larger than permitted' in html)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(TestLoader().loadTestsFromTestCase(NyForumFunctionalTestCase))
    return suite
