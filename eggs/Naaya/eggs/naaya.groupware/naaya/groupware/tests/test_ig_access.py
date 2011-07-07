from naaya.groupware.tests import GWFunctionalTestCase
import transaction

class IGAccessTestCase(GWFunctionalTestCase):
    def afterSetUp(self):
        self.portal.aq_parent.acl_users._doAddUser('norole', 'norole', [], '')
        self.portal.aq_parent.acl_users._doAddUser('contrib', '',
                                                    ['Contributor'], '')
        transaction.commit()

    def _get_user(self, username):
        return self.portal.aq_parent.acl_users.getUser(username)

    def test_get_user_access_restricted(self):
        """ Test when the method returns 'restricted'"""
        #No user
        self.assertEqual(self.portal.get_user_access(), 'restricted')

    def test_get_user_access_viewer(self):
        """ Should return viewer """
        self.portal.REQUEST['AUTHENTICATED_USER'] = self._get_user('norole')
        self.assertEqual(self.portal.get_user_access(), 'viewer')

    def test_get_user_access_admin(self):
        """ Test when user returns 'admin' """
        self.portal.REQUEST['AUTHENTICATED_USER'] = self._get_user('admin')
        self.assertEqual(self.portal.get_user_access(), 'admin')

    def test_get_user_access_contributor(self):
        self.portal.REQUEST['AUTHENTICATED_USER'] = self._get_user('contrib')
        self.assertEqual(self.portal.get_user_access(), 'member')

