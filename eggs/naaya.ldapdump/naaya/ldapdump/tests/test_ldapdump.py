# python imports
from __future__ import absolute_import
import os
import os.path
import shutil
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from . import fakeldap
# test imports
from . import ldap_config
# program imports
from naaya.ldapdump import main

realldap = main.ldap
JPEG_SYNTAX = '1.3.6.1.4.1.1466.115.121.1.28'

class TestLDAPCache(unittest.TestCase):
    def setUp(self):
        users_base = ldap_config.defaults.get('users_base')
        groups_base = ldap_config.defaults.get('groups_base')

        fakeldap.clearTree()
        fakeldap.setTreeItem(users_base)
        fakeldap.setTreeItem(groups_base)

        # copies, since the tests change the entries
        fakeldap.setTreeItem(ldap_config.user_dn,
                             dict(ldap_config.user))
        fakeldap.setTreeItem(ldap_config.manager_user_dn,
                             dict(ldap_config.manager_user))
        fakeldap.setTreeItem(ldap_config.user2_dn,
                             dict(ldap_config.user2))

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
                         ['ldaps://localhost'])

        values = ldap_conn.get_values('ou=people,dc=naaya,dc=org')
        self.assertEqual(len(fakeldap.history), 2)
        self.assertEqual(fakeldap.history[1]['search_s'],
                         ['ou=people,dc=naaya,dc=org', fakeldap.SCOPE_SUBTREE])

        self.assertEqual(len(values), 3)
        self.assertEqual(values['uid=test,ou=people,dc=naaya,dc=org']['uid'],
                         {'type': 'text', 'values': ['test']})
        self.assertEqual(values['uid=admin,ou=people,dc=naaya,dc=org']['uid'],
                         {'type': 'text', 'values': ['admin']})
        self.assertEqual(values['uid=test2,ou=people,dc=naaya,dc=org']['uid'],
                         {'type': 'text', 'values': ['test2']})

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

    def test_binary_values(self):
        photo = b'\xff\xd8\xff\xe0 jpeg'
        fakeldap.getSubtree(ldap_config.user_dn)['jpegPhoto'] = [photo]
        schema = Mock()
        schema.get_syntax.side_effect = lambda attr: (
            JPEG_SYNTAX if attr == 'jpegPhoto' else None)
        config_path = os.path.join(self.tmp_dir, 'config.yaml')
        with patch.object(main.LDAPConnection, 'get_schema',
                          return_value=schema):
            main.dump_ldap(config_path)

        values = dict(main.get_reader(config_path).get_dump())
        record = values[ldap_config.user_dn]
        self.assertEqual(record['jpegPhoto'], photo)
        self.assertEqual(record['givenName'], u'G\xc3\xbcnther')

    def write_config(self, encoding='utf-8', extra=''):
        config_path = os.path.join(self.tmp_dir, 'config.yaml')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('# Configuration for the démo dump\n'
                    'ldap:\n'
                    '    host: localhost\n'
                    '    encoding: %s\n'
                    '    root_DNs:\n'
                    '        - ou=people,dc=naaya,dc=org\n'
                    'sqlite:\n'
                    '    path: ./naaya.test.db\n%s' % (encoding, extra))
        return config_path

    def test_utf8_config_and_values(self):
        # only fails with a non UTF-8 locale (e.g. LANG=C) if the config is
        # read without encoding='utf-8'
        config_path = self.write_config(extra='# Grüße\n')
        self.assertEqual(main.get_config(config_path)['ldap']['encoding'],
                         'utf-8')
        main.dump_ldap(config_path)
        values = dict(main.get_reader(config_path).get_dump())
        self.assertEqual(values[ldap_config.user_dn]['givenName'],
                         'Günther')

    def test_multivalued_cn(self):
        fakeldap.getSubtree(ldap_config.user_dn)['cn'] = [b'Test', b'User']
        config_path = self.write_config()
        values = main.get_ldap_connection(main.get_config(config_path))\
            .get_values('ou=people,dc=naaya,dc=org')
        self.assertEqual(values[ldap_config.user_dn]['cn'],
                         {'type': 'text', 'values': ['Test User']})

    def test_multivalued_attribute(self):
        fakeldap.getSubtree(ldap_config.user_dn)['mail'] = [b'a@x.org',
                                                            b'b@x.org']
        config_path = self.write_config()
        main.dump_ldap(config_path)
        values = dict(main.get_reader(config_path).get_dump())
        self.assertEqual(values[ldap_config.user_dn]['mail'],
                         ['a@x.org', 'b@x.org'])
        self.assertEqual(values[ldap_config.user_dn]['dn'],
                         ldap_config.user_dn)

    def test_undecodable_value(self):
        # values that do not decode are left out, the other attributes stay
        fakeldap.getSubtree(ldap_config.user_dn)['sn'] = [b'\xff\xfe']
        config_path = self.write_config()
        values = main.get_ldap_connection(main.get_config(config_path))\
            .get_values('ou=people,dc=naaya,dc=org')
        record = values[ldap_config.user_dn]
        self.assertNotIn('sn', record)
        self.assertEqual(record['uid'], {'type': 'text', 'values': ['test']})

    def test_missing_config(self):
        config = main.get_config(os.path.join(self.tmp_dir, 'missing.yaml'))
        self.assertEqual(config['sqlite'], {'path': ''})

    def test_no_db(self):
        db_path = os.path.join(self.tmp_dir, 'missing.test.db')
        self.assertTrue(not os.path.exists(db_path))

        reader = main.DumpReader(db_path)
        self.assertTrue(reader.latest_timestamp() is None)


if __name__ == '__main__':
    unittest.main()
