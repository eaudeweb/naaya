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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Andrei Laza, Eau de Web


#Python imports
from unittest import TestCase, TestSuite, makeSuite
import os.path
import os
import email
import shutil
import random
import tempfile

#Naaya Imports
from Products.NaayaCore.EmailTool.EmailSender import EmailSenderThread, EmailSender, build_email, save_email

class EmailSenderSub(EmailSender):
    def __init__(self, *args):
        EmailSender.__init__(self, *args)

        self.sent_content = []
        self.error_content = []

    def _open_smtp(self):
        pass

    def _close_smtp(self):
        pass

    def _send_email(self, content):
        if random.randint(0, 1) == 0:
            self.sent_content.append(content)
        else:
            self.error_content.append(content)
            raise Exception()

class EmailSenderTestCase(TestCase):
    TMP_FOLDER = None
    SEND_ERROR_FOLDER = None
    SEND_FOLDER = None

    def setUp(self):
        self.TMP_FOLDER = tempfile.mkdtemp()
        self.SEND_ERROR_FOLDER = tempfile.mkdtemp()
        self.SEND_FOLDER = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.TMP_FOLDER)
        shutil.rmtree(self.SEND_ERROR_FOLDER)
        shutil.rmtree(self.SEND_FOLDER)

    def testFolderPath(self):
        self.assertTrue(os.path.isdir(self.TMP_FOLDER))
        self.assertTrue(os.path.isdir(self.SEND_ERROR_FOLDER))
        self.assertTrue(os.path.isdir(self.SEND_FOLDER))

        self.msg1_content = build_email('me@email.com',
                'you@email.com', 'subject', 'text')
        self.msg2_content = build_email('me@email.com',
                ['youtoo@email.com', 'you@email.com'], 'subject', 'text', 'html')

        save_email(self.TMP_FOLDER, self.SEND_FOLDER, self.msg1_content)
        save_email(self.TMP_FOLDER, self.SEND_FOLDER, self.msg2_content)

        #esender = EmailSender(self.SEND_ERROR_FOLDER, self.SEND_FOLDER, self.TMP_FOLDER, '127.0.0.1')
        esender = EmailSenderSub(self.SEND_ERROR_FOLDER, self.SEND_FOLDER, self.TMP_FOLDER, '127.0.0.1')

        esender_thread = EmailSenderThread(1, esender)
        esender_thread.start()
        esender_thread.join()

        self.assertTrue((self.msg1_content in esender.sent_content) or
                (self.msg1_content in esender.error_content))
        self.assertFalse((self.msg1_content in esender.sent_content) and
                (self.msg1_content in esender.error_content))
        self.assertTrue((self.msg2_content in esender.sent_content) or
                (self.msg2_content in esender.error_content))
        self.assertFalse((self.msg2_content in esender.sent_content) and
                (self.msg2_content in esender.error_content))

        self.assertEqual(esender._get_from_and_to_addrs(self.msg1_content),
                ('me@email.com', 'you@email.com'))
        self.assertEqual(esender._get_from_and_to_addrs(self.msg2_content),
                ('me@email.com', 'youtoo@email.com, you@email.com'))

        self.assertEqual(len(os.listdir(self.TMP_FOLDER)), 0)
        self.assertEqual(len(os.listdir(self.SEND_ERROR_FOLDER)), len(esender.error_content))
        self.assertEqual(len(os.listdir(self.SEND_FOLDER)), 0)

    def testManyEmails(self):
        self.assertTrue(os.path.isdir(self.TMP_FOLDER))
        self.assertTrue(os.path.isdir(self.SEND_ERROR_FOLDER))
        self.assertTrue(os.path.isdir(self.SEND_FOLDER))

        self.msg_contents = []
        for i in range(30):
            msg = build_email(str(random.randint(1, 1000)), str(random.randint(1, 1000)),
                    str(random.randint(1, 1000)), str(random.randint(1, 1000)))
            save_email(self.TMP_FOLDER, self.SEND_FOLDER, msg)
            self.msg_contents.append(msg)

        esender = EmailSenderSub(self.SEND_ERROR_FOLDER, self.SEND_FOLDER, self.TMP_FOLDER, '127.0.0.1')

        esender_threads = []
        for i in range(10):
            esender_threads.append(EmailSenderThread(1, esender))
            esender_threads[i].start()
        for i in range(10):
            esender_threads[i].join()

        for i in range(len(self.msg_contents)):
                self.assertTrue((self.msg_contents[i] in esender.sent_content) or
                        (self.msg_contents[i] in esender.error_content))
                self.assertFalse((self.msg_contents[i] in esender.sent_content) and
                        (self.msg_contents[i] in esender.error_content))

        self.assertEqual(len(os.listdir(self.TMP_FOLDER)), 0)
        self.assertEqual(len(os.listdir(self.SEND_ERROR_FOLDER)), len(esender.error_content))
        self.assertEqual(len(os.listdir(self.SEND_FOLDER)), 0)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(EmailSenderTestCase))
    return suite
