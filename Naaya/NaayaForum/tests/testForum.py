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
# Andrei Laza, Eau de Web

from unittest import TestSuite, makeSuite
from StringIO import StringIO

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaBase.NyRoleManager import NyRoleManager

from Products.NaayaForum.NyForum import NyForum, manage_addNyForum
from Products.NaayaForum.NyForumTopic import NyForumTopic, addNyForumTopic
from Products.NaayaForum.NyForumMessage import addNyForumMessage

class ForumBasicTestCase(NaayaFunctionalTestCase):
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

    def test_NyRoleManager_wrappers(self):
        self.assertTrue(NyRoleManager.manage_addLocalRoles == NyForum.manage_addLocalRoles)
        self.assertTrue(NyRoleManager.manage_setLocalRoles == NyForum.manage_setLocalRoles)
        self.assertTrue(NyRoleManager.manage_delLocalRoles == NyForum.manage_delLocalRoles)

        self.assertTrue(NyRoleManager.manage_addLocalRoles == NyForumTopic.manage_addLocalRoles)
        self.assertTrue(NyRoleManager.manage_setLocalRoles == NyForumTopic.manage_setLocalRoles)
        self.assertTrue(NyRoleManager.manage_delLocalRoles == NyForumTopic.manage_delLocalRoles)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(ForumBasicTestCase))
    return suite


