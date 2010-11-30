# python imports
import unittest
import os
import os.path
from datetime import datetime
import tempfile
import shutil

# program imports
from naaya.ldapdump import main

# test imports
import ldap_config
import fakeldap

realldap = main.ldap

class TestLDAPCache(unittest.TestCase):
    def setUp(self):
        users_base = ldap_config.defaults.get('users_base')
        groups_base = ldap_config.defaults.get('groups_base')

        fakeldap.clearTree()
        fakeldap.setTreeItem(users_base)
        fakeldap.setTreeItem(groups_base)

        fakeldap.setTreeItem(ldap_config.user_dn,
                             ldap_config.user)
        fakeldap.setTreeItem(ldap_config.manager_user_dn,
                             ldap_config.manager_user)
        fakeldap.setTreeItem(ldap_config.user2_dn,
                             ldap_config.user2)

        self.tmp_dir = tempfile.mkdtemp()
        shutil.copy(os.path.join(os.path.dirname(__file__), 'config.yaml'),
                self.tmp_dir)

        main.ldap = fakeldap

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

        main.ldap = realldap

    def test_ldap(self):
        fakeldap.history = []

        config_path = os.path.join(self.tmp_dir, 'config.yaml')
        config = main.get_config(config_path)

        ldap_conn = main.get_ldap_connection(config)
        self.assertEqual(len(fakeldap.history), 1)
        self.assertEqual(fakeldap.history[0]['initialize'],
                         ['ldap://localhost'])

        values = ldap_conn.get_values('ou=people,dc=naaya,dc=org')
        self.assertEqual(len(fakeldap.history), 2)
        self.assertEqual(fakeldap.history[1]['search_s'],
                         ['ou=people,dc=naaya,dc=org', fakeldap.SCOPE_SUBTREE])

        self.assertEqual(len(values), 3)
        self.assertEqual(values['uid=test,ou=people,dc=naaya,dc=org']['uid'],
                         ['test'])
        self.assertEqual(values['uid=admin,ou=people,dc=naaya,dc=org']['uid'],
                         ['admin'])
        self.assertEqual(values['uid=test2,ou=people,dc=naaya,dc=org']['uid'],
                         ['test2'])

    def test_refresh(self):
        config_path = os.path.join(self.tmp_dir, 'config.yaml')

        db_path = os.path.join(self.tmp_dir, 'naaya.test.db')
        self.assertTrue(not os.path.exists(db_path))

        before = datetime.now().isoformat()
        main.dump_ldap(config_path)
        after = datetime.now().isoformat()

        reader = main.get_reader(config_path)
        latest_timestamp = reader.latest_timestamp()
        self.assertTrue(before < latest_timestamp < after)
        values = dict(reader.get_dump())

        self.assertEqual(len(values), 3)
        self.assertEqual(values['uid=test,ou=people,dc=naaya,dc=org']['uid'],
                         u'test')
        self.assertEqual(values['uid=admin,ou=people,dc=naaya,dc=org']['uid'],
                         u'admin')
        self.assertEqual(values['uid=test2,ou=people,dc=naaya,dc=org']['uid'],
                         u'test2')

        self.assertTrue(os.path.exists(db_path))
        os.remove(db_path)

    def test_no_db(self):
        db_path = os.path.join(self.tmp_dir, 'missing.test.db')
        self.assertTrue(not os.path.exists(db_path))

        reader = main.DumpReader(db_path)
        self.assertTrue(reader.latest_timestamp() is None)


if __name__ == '__main__':
    unittest.main()
