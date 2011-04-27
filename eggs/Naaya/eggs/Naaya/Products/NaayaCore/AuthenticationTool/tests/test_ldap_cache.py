from time import time
from datetime import datetime, timedelta
from copy import deepcopy

from nose.plugins.skip import SkipTest

from zope.component import getGlobalSiteManager, queryUtility
from zope.interface import alsoProvides
import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.NaayaCore.AuthenticationTool.plugins import ldap_cache

try:
    from naaya.ldapdump.interfaces import IDumpReader
except ImportError:
    ldapdump_is_available = False
else:
    ldapdump_is_available = True

import mock_ldap

gsm = getGlobalSiteManager()

mock_data = {
    'uid=userone,ou=Users,o=EIONET,l=Europe': {
        'cn': 'One User',
        'sn': 'User',
        'givenName': 'One',
        'mail': 'user-one@example.com',
        'uid': 'userone',
    },
    'uid=usertwo,ou=Users,o=EIONET,l=Europe': {
        'cn': 'rik leemans',
        'sn': 'User',
        'givenName': 'Two',
        'mail': 'user-two@example.com',
        'uid': 'usertwo',
    },
    'uid=userthree,ou=Users,o=EIONET,l=Europe': {
        'cn': 'Eamonn Lacey',
        'sn': 'User',
        'givenName': 'Three',
        'mail': 'user-three@example.com',
        'uid': 'userthree',
    },
}

def _remove_existing_cache():
    orig_reader = queryUtility(IDumpReader, default=None)
    if orig_reader is not None:
        gsm.unregisterUtility(orig_reader)
        return lambda: gsm.registerUtility(orig_reader)
    else:
        return lambda: None

def _register_mock_cache(mock_reader):
    alsoProvides(mock_reader, IDumpReader)
    gsm.registerUtility(mock_reader)
    return lambda: gsm.unregisterUtility(mock_reader)


class MockCacheReader(object):
    def __init__(self, age=timedelta(minutes=2), data=mock_data):
        self.set_timestamp(age)
        self._data = mock_data
        self._called = []

    def set_timestamp(self, age):
        self._timestamp = (datetime.now() - age).isoformat()

    def latest_timestamp(self):
        self._called.append('timestamp')
        return self._timestamp

    def get_dump(self):
        self._called.append('dump')
        return self._data.iteritems()

class LDAPCacheTest(NaayaTestCase):
    def setUp(self):
        if not ldapdump_is_available:
            raise SkipTest("naaya.ldapdump not available")

        self._restore_cache = _remove_existing_cache()
        self._mock_reader = MockCacheReader()
        self._remove_mock_cache = _register_mock_cache(self._mock_reader)

    def tearDown(self):
        self._remove_mock_cache()
        self._restore_cache()

    def test_update_cache(self):
        cache = ldap_cache.Cache()
        assert len(cache.users) == 0
        assert self._mock_reader._called == []

        cache.update()
        assert self._mock_reader._called == ['timestamp', 'dump']
        self._mock_reader._called[:] = []
        assert len(cache.users) == 3

        cache.update()
        assert self._mock_reader._called == []

        cache._last_update = time() - (60*20)
        cache.update()
        assert self._mock_reader._called == ['timestamp']
        self._mock_reader._called[:] = []

        self._mock_reader.set_timestamp(timedelta(minutes=1))
        self._mock_reader._data.popitem() # remove an entry at random
        cache._last_update = time() - (60*20)
        cache.update()
        assert self._mock_reader._called == ['timestamp', 'dump']
        self._mock_reader._called[:] = []
        assert len(cache.users) == 2

    def test_get_from_cache(self):
        cache = ldap_cache.Cache()
        cache.update()
        userone_dn = 'uid=userone,ou=Users,o=EIONET,l=Europe'

        assert cache.get(userone_dn)['cn'] == "One User"
        self.assertRaises(KeyError, cache.get, 'nosuchuser')
        assert cache.get('nosuchuser', 'placeholder') is 'placeholder'

class LDAPPluginTest(NaayaTestCase):
    def setUp(self):
        if not (mock_ldap.is_available and ldapdump_is_available):
            raise SkipTest

        mock_ldap.quick_setup(self.app, self.portal, False)
        mock_ldap.add_user(self.app, {
            'uid': "gigel",
            'cn': "Gigel's Full Name",
            'sn': "Test",
            'givenName': "Gigel",
            'mail': "mygigel@example.com",
            'user_pw': "mypass", 'confirm_pw': "mypass",
        })
        transaction.commit()
        self._cache = ldap_cache.Cache()
        self._cache.timestamp = datetime.now().isoformat()
        self._orig_get = ldap_cache.get
        ldap_cache.get = self._cache.get

    def tearDown(self):
        ldap_cache.get = self._orig_get

    def test_without_cache(self):
        ldap_plugin = self.portal.acl_users.getSources()[0]
        gigel_info = ldap_plugin.get_source_user_info('gigel')
        assert gigel_info.first_name == "Gigel"
        assert gigel_info.last_name == "Test"
        assert gigel_info.full_name == "Gigel's Full Name"
        assert gigel_info.email == "mygigel@example.com"
        assert gigel_info.user_id == 'gigel'
        assert isinstance(gigel_info.user_id, str)
        user_ob = gigel_info.zope_user is ldap_plugin._get_zope_user('gigel')

    def test_with_cache(self):
        # cached values have " C" appended so we can recognise them
        self._cache._store_dump([
            ('uid=gigel,ou=people,dc=dataflake,dc=org', {
                'uid': u"gigel C",
                'cn': u"Gigel's Full Name C",
                'sn': u"Test C",
                'givenName': u"Gigel C",
                'mail': u"mygigel@example.com C",
            }),
        ])
        ldap_plugin = self.portal.acl_users.getSources()[0]
        gigel_info = ldap_plugin.get_source_user_info('gigel')
        assert gigel_info.first_name == "Gigel C"
        assert gigel_info.last_name == "Test C"
        assert gigel_info.full_name == "Gigel's Full Name C"
        assert gigel_info.email == "mygigel@example.com C"
        assert gigel_info.user_id == 'gigel'
        assert isinstance(gigel_info.user_id, str)
        user_ob = gigel_info.zope_user is ldap_plugin._get_zope_user('gigel')
