from unittest import mock

import transaction
from OFS.SimpleItem import SimpleItem

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.NotificationTool.containers import \
    AnonymousSubscription
from Products.NaayaCore.NotificationTool.interfaces import \
    ISubscriptionContainer
from Products.NaayaCore.NotificationTool.NotificationTool import \
    NotificationTool
from Products.NaayaCore.NotificationTool.utils import walk_subscriptions
from naaya.content.document.document_item import addNyDocument

from .test_notifications_unit import BaseNotificationsTest


class Comment(SimpleItem):
    author = 'contributor'

    def __init__(self, id):
        self.id = id


class NotifyCommentTest(BaseNotificationsTest):

    def afterSetUp(self):
        super(NotifyCommentTest, self).afterSetUp()
        self.portal.getNotificationTool().config['enable_instant'] = True
        addNyDocument(self.portal.fol1, id='doc', title='Doc',
                      contributor='admin')
        self.doc = self.portal.fol1.doc
        self._fetch_test_notifications()

    def test_comment_instant(self):
        notif_tool = self.portal.getNotificationTool()
        self.add_account_subscription('user1', 'fol1', 'instant', 'en')
        comment = Comment('c1')

        self.doc.approved = False
        notif_tool.notify_comment_instant(comment, self.doc, 'contributor')
        self.assertEqual(self._fetch_test_notifications(), [])

        self.doc.approved = True
        notif_tool.notify_comment_instant(comment, self.doc, 'contributor')
        [mail] = self._fetch_test_notifications()
        self.assertEqual(mail[1], 'user1@example.com')
        self.assertEqual(mail[2], 'Instant notification - new comment on: Doc')
        self.assertIn('/fol1/doc#comment_c1', mail[3])

    def test_comment_maintainer(self):
        notif_tool = self.portal.getNotificationTool()
        self.portal.fol1.maintainer_email = 'boss@example.com'
        notif_tool.notify_comment_maintainer(Comment('c1'), self.doc)
        recipients = sorted(m[1] for m in self._fetch_test_notifications())
        self.assertEqual(recipients, ['boss@example.com',
                                      'site.admin@example.com'])

    def test_account_modification(self):
        notif_tool = self.portal.getNotificationTool()
        notif_tool.notify_account_modification(
            'user1@example.com', self.portal.fol1, username='user1',
            new_roles=['Contributor'], removed_roles=['Reviewer'])
        [mail] = self._fetch_test_notifications()
        self.assertEqual(mail[1], 'user1@example.com')
        self.assertIn('Contributor', mail[3])
        self.assertIn('Reviewer', mail[3])

    def test_remove_anonymous_subscription(self):
        notif_tool = self.portal.getNotificationTool()
        container = ISubscriptionContainer(self.portal.fol1)
        container.add(AnonymousSubscription(
            email='anon@example.com', location='fol1', notif_type='instant',
            lang='en', content_types=[]))
        self.assertRaises(ValueError, notif_tool.remove_anonymous_subscription,
                          'other@example.com', 'fol1', 'instant', 'en')
        notif_tool.remove_anonymous_subscription('anon@example.com', 'fol1',
                                                 'instant', 'en')
        self.assertEqual(list(container), [])

    def test_my_subscriptions_cached_copies(self):
        notif_tool = self.portal.getNotificationTool()
        self.add_account_subscription('contributor', 'fol1', 'instant', 'en')
        self.login('contributor')
        request = self.portal.REQUEST
        request.other.pop('_naaya_my_subscriptions', None)
        try:
            with mock.patch.object(
                    NotificationTool, 'user_subscriptions', autospec=True,
                    side_effect=NotificationTool.user_subscriptions) \
                    as user_subscriptions:
                first = notif_tool.list_my_subscriptions(request)
                first[0]['location'] = 'changed'
                second = notif_tool.list_my_subscriptions(request)
            self.assertEqual(user_subscriptions.call_count, 1)
            self.assertEqual(second, [{'location': 'fol1',
                                       'notif_type': 'instant',
                                       'content_types': [], 'lang': 'en'}])
        finally:
            request.other.pop('_naaya_my_subscriptions', None)
            self.logout()


class SubscriptionPagesTest(NaayaFunctionalTestCase):

    def subscriptions(self):
        return [(s.user_id, s.notif_type)
                for ob, n, s in walk_subscriptions(self.portal)]

    def afterSetUp(self):
        notif_tool = self.portal.getNotificationTool()
        self._config = dict(notif_tool.config)
        notif_tool.config['enable_instant'] = True
        transaction.commit()

    def beforeTearDown(self):
        notif_tool = self.portal.getNotificationTool()
        notif_tool.config.clear()
        notif_tool.config.update(self._config)
        for ob, n, s in list(walk_subscriptions(self.portal)):
            ISubscriptionContainer(ob).remove(n)
        transaction.commit()

    def test_subscribe_and_unsubscribe_me(self):
        url = 'http://localhost/portal/portal_notification/'
        self.browser.go(url + 'subscribe_me?location=info&notif_type=instant'
                        '&lang=en')
        self.assertRedirectLoginPage()
        self.assertEqual(self.subscriptions(), [])

        self.browser_do_login('contributor', 'contributor')
        self.browser.go(url + 'subscribe_me?location=info&notif_type=instant'
                        '&lang=en')
        self.assertEqual(self.subscriptions(), [('contributor', 'instant')])
        self.browser.go(url + 'unsubscribe_me?location=info'
                        '&notif_type=instant&lang=en')
        self.assertEqual(self.subscriptions(), [])
        self.browser_do_logout()

    def test_admin_add_subscription(self):
        url = ('http://localhost/portal/portal_notification/'
               'admin_add_account_subscription?user_id=user1&location=/portal/info'
               '&notif_type=instant&lang=en')
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(url)
        self.assertAccessDenied()
        self.assertEqual(self.subscriptions(), [])
        self.browser_do_logout()

        self.browser_do_login('admin', '')
        self.browser.go(url)
        self.assertEqual(self.subscriptions(), [('user1', 'instant')])
        self.browser_do_logout()
