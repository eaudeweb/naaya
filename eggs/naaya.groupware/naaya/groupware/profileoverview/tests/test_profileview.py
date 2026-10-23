''' profile overview pages with a mocked LDAP agent '''
import json
from unittest.mock import MagicMock as Mock, patch

from lxml.html.soupparser import fromstring

from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.Naaya.NyFolder import addNyFolder
from naaya.groupware.interfaces import IGroupwareApplication
from naaya.groupware.tests import GWTestCase
from naaya.groupware.profileoverview.profile import (
    ProfileClient, ProfileView, show_local_roles, get_plugldap)

LDAP_ROLES = [
    ('places-bank', {'description': [b'B\xc3\xa4nk']}),
    ('places', {'description': [b'Places']}),
    ('places-bank-vault', {}),
    ('places-atm', {'description': [b'ATM']}),
    ('shops-bank', {'description': [b'Orphan']}),
]


class ProfileTestBase(GWTestCase):

    def afterSetUp(self):
        addNyFolder(self.portal, 'docs', title='Documents', submitted=1)
        self.folder = self.portal['docs']
        self.app.acl_users._doAddUser('anne', 'anne', [], '')
        self.user = self.app.acl_users.getUser('anne')
        self.agent = Mock()
        self.agent.member_roles_info.side_effect = \
            lambda *args: iter(LDAP_ROLES)
        self.agent.role_info.side_effect = lambda role_id: {
            'description': 'Description of %s' % role_id}
        self.patch = patch(
            'naaya.groupware.profileoverview.profile.agent_from_uf',
            Mock(return_value=self.agent))
        self.patch.start()

    def beforeTearDown(self):
        self.patch.stop()

    def client(self):
        return ProfileClient(self.app, self.user)


class ProfileClientTest(ProfileTestBase):

    def test_roles_list_in_ldap(self):
        roles = self.client().roles_list_in_ldap()
        self.assertEqual(
            [(r['id'], r['level'], r['parent'], r['description'])
             for r in roles],
            [('places', 0, 'top', 'Places'),
             ('places-atm', 1, 'places', 'ATM'),
             ('places-bank', 1, 'places', 'B\xe4nk'),
             ('places-bank-vault', 2, 'places-bank', '')])
        self.agent.member_roles_info.assert_called_once_with(
            'user', 'anne', ('description',))

    def test_access_in_igs(self):
        self.portal.manage_setLocalRoles('anne', ['Administrator'])
        access = self.client().access_in_igs()
        self.assertEqual(access, {'admin': [self.portal]})
        self.assertEqual(self.client().access_in_ig(self.portal), 'admin')

    def test_local_access_in_ig(self):
        self.folder.manage_setLocalRoles('anne', ['Contributor'])
        self.folder.recatalogNyObject(self.folder)
        result = self.client().local_access_in_ig(self.portal)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['location'].getPhysicalPath(),
                         self.folder.getPhysicalPath())
        self.assertEqual(result[0]['access'], ['Contributor'])
        self.assertEqual(result[0]['group'], '')

    def test_local_roles_by_groups(self):
        self.assertIsNone(get_plugldap(self.portal))
        self.assertEqual(self.client().local_roles_by_groups(self.portal), [])
        plugldap = Mock()
        plugldap.get_local_roles_by_groups.return_value = {
            'places-bank': [('Contributor', {'ob': self.folder})]}
        with patch('naaya.groupware.profileoverview.profile.get_plugldap',
                   Mock(return_value=plugldap)):
            result = self.client().local_roles_by_groups(self.portal)
        self.assertEqual(result, [{'location': self.folder,
                                   'access': ('Contributor', ),
                                   'group': 'places-bank'}])

    def test_notification_lists(self):
        notif_tool = self.portal.getNotificationTool()
        notif_tool.config['enable_weekly'] = True
        notif_tool.add_account_subscription('anne', 'docs', 'weekly', 'en')
        notif_tool.add_account_subscription('admin', '', 'weekly', 'en')
        notifications = self.client().notification_lists([self.portal], 5)
        subscriptions, = notifications.values()
        self.assertEqual([(s['object'].getId(), s['notif_type'])
                          for s in subscriptions], [('docs', 'weekly')])


class ProfileViewTest(ProfileTestBase):

    def afterSetUp(self):
        super().afterSetUp()
        # the groupware Zope root provides it through zcml in production
        alsoProvides(self.app.aq_base, IGroupwareApplication)
        alsoProvides(self.app.REQUEST, IDefaultBrowserLayer)

    def request(self, form, user='anne'):
        request = self.app.REQUEST
        request.form.clear()
        request.form.update(form)
        request['AUTHENTICATED_USER'] = self.app.acl_users.getUser(user)
        return request

    def test_overview_page(self):
        request = self.request({})
        page = fromstring(ProfileView(self.app, request))
        rows = page.xpath('//table[contains(@class, "sub-roles")]/tbody/tr')
        cells = [[' '.join(td.text_content().split()) for td in tr.xpath('td')]
                 for tr in rows]
        self.assertEqual(cells, [['places-atm', 'ATM'],
                                 ['places-bank-vault', '']])
        self.assertEqual([tr.get('class') for tr in rows],
                         ['even places', 'odd places-bank'])
        self.assertEqual(page.xpath('//input[@id="user"]')[0].get('value'),
                         'anne')

    def test_manager_sees_other_profile(self):
        request = self.request({'user': 'anne'}, user='admin')
        page = fromstring(ProfileView(self.app, request))
        self.assertEqual(page.xpath('//input[@id="user"]')[0].get('value'),
                         'anne')
        request = self.request({'user': 'admin'})
        page = fromstring(ProfileView(self.app, request))
        self.assertEqual(page.xpath('//input[@id="user"]')[0].get('value'),
                         'anne')

    def test_ajax_igs(self):
        request = self.request({'ajax': 'igs'})
        self.assertEqual(json.loads(ProfileView(self.app, request)),
                         [self.portal.getId()])
        self.portal.toggle_portal_restricted(True)
        self.assertEqual(json.loads(ProfileView(self.app, request)), [])

    def test_ajax_memberships(self):
        self.folder.manage_setLocalRoles('anne', ['Contributor'])
        self.folder.recatalogNyObject(self.folder)
        plugldap = Mock()
        plugldap.get_local_roles_by_groups.return_value = {
            'places-bank': [('Reviewer', {'ob': self.folder})]}
        request = self.request({'ajax': 'memberships',
                                'ig_id': self.portal.getId()})
        with patch('naaya.groupware.profileoverview.profile.get_plugldap',
                   Mock(return_value=plugldap)):
            page = fromstring(ProfileView(self.app, request))
        items = [' '.join(li.text_content().split())
                 for li in page.xpath('//li')]
        self.assertEqual(items, [
            'Contributor in Documents - local role',
            'Reviewer in Documents - as a member of '
            'Description of places-bank (places-bank)'])
        self.assertEqual(page.xpath('//dt//a')[0].text.strip(),
                         self.portal.title_or_id())

    def test_ajax_memberships_admin(self):
        self.portal.manage_setLocalRoles('anne', ['Administrator'])
        request = self.request({'ajax': 'memberships',
                                'ig_id': self.portal.getId()})
        page = fromstring(ProfileView(self.app, request))
        self.assertIn('Admin access', page.text_content())

    def test_ajax_memberships_admin_compared_by_value(self):
        # a string built at runtime is equal to 'admin' but not identical
        admin = ''.join(['ad', 'min'])
        request = self.request({'ajax': 'memberships',
                                'ig_id': self.portal.getId()})
        with patch.object(ProfileClient, 'access_in_ig',
                          Mock(return_value=admin)):
            page = fromstring(ProfileView(self.app, request))
        self.assertIn('Admin access', page.text_content())

    def test_ajax_memberships_viewer(self):
        request = self.request({'ajax': 'memberships',
                                'ig_id': self.portal.getId()})
        self.assertEqual(self.client().access_in_ig(self.portal), 'viewer')
        self.assertEqual(ProfileView(self.app, request).strip(), '')
        # the same viewer with a local role gets the membership list
        self.folder.manage_setLocalRoles('anne', ['Contributor'])
        self.folder.recatalogNyObject(self.folder)
        page = fromstring(ProfileView(self.app, request))
        self.assertEqual([' '.join(li.text_content().split())
                          for li in page.xpath('//li')],
                         ['Contributor in Documents - local role'])

    def test_ajax_subscriptions(self):
        notif_tool = self.portal.getNotificationTool()
        notif_tool.config['enable_weekly'] = True
        notif_tool.add_account_subscription('anne', 'docs', 'weekly', 'en')
        request = self.request({'ajax': 'subscriptions',
                                'ig_id': self.portal.getId()})
        page = fromstring(ProfileView(self.app, request))
        link = page.xpath('//li/a')[0]
        self.assertEqual(link.text.strip(), 'Documents')
        self.assertEqual(link.get('href'), self.folder.absolute_url())
        self.assertEqual(page.xpath('//li/div')[0].text, 'weekly')

    def test_ajax_anonymous(self):
        request = self.request({'ajax': 'igs'})
        request['AUTHENTICATED_USER'] = self.app.acl_users._nobody
        self.assertEqual(ProfileView(self.app, request), '')

    def test_show_local_roles(self):
        self.folder.manage_setLocalRoles('anne', ['Contributor'])
        self.folder.recatalogNyObject(self.folder)
        request = self.request({'userid': 'anne'})
        result = json.loads(show_local_roles(self.app, request))
        self.assertEqual(result, {'anne': [{
            'roles': ['Contributor'],
            'ob_url': self.folder.absolute_url(),
            'ob_title': '%s > Documents' % self.portal.title_or_id(),
            'extra': {'ig': self.portal.getId()}}]})
