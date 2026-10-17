from unittest.mock import Mock, patch

import ldap
import transaction
from be.ldapadmin.factories import LDAPUnavailable
from naaya.groupware.member_search import LDAP_UNAVAILABLE_MSG
from naaya.groupware.tests import GWTestCase


class MemberSearchLDAPUnavailableTest(GWTestCase):
    """ Member search when the LDAP server does not answer """

    def afterSetUp(self):
        self.portal.getAuthenticationTool().manage_addUser(
            name='jdoe', password='jdoe', confirm='jdoe', firstname='John',
            lastname='Doe', email='jdoe@example.com')
        transaction.commit()
        source = Mock(id='ldap-source')
        sources_info = {'ldap-source': {'user_roles': {}, 'group_map': {},
                                        'source': source}}
        self.patches = [patch('naaya.groupware.member_search.MemberSearch.'
                              'get_sources_info',
                              Mock(return_value=sources_info))]
        for p in self.patches:
            p.start()

    def beforeTearDown(self):
        for p in self.patches:
            p.stop()

    def search(self, agent_from_uf):
        with patch('naaya.groupware.member_search.agent_from_uf',
                   agent_from_uf):
            return self.portal.member_search.search_users_html('jdoe')

    def test_not_connected(self):
        html = self.search(Mock(side_effect=LDAPUnavailable('not connected')))
        self.assertIn(LDAP_UNAVAILABLE_MSG, html)
        self.assertIn('John Doe', html)

    def test_search_error(self):
        agent = Mock()
        agent.search_user.side_effect = ldap.SERVER_DOWN({})
        html = self.search(Mock(return_value=agent))
        self.assertIn(LDAP_UNAVAILABLE_MSG, html)
        self.assertIn('John Doe', html)

    def test_no_error(self):
        agent = Mock()
        agent.search_user.return_value = []
        html = self.search(Mock(return_value=agent))
        self.assertNotIn(LDAP_UNAVAILABLE_MSG, html)
        self.assertIn('John Doe', html)
