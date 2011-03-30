from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
import os
import time
from datetime import datetime
from mock import patch

from naaya.core.zope2util import dt2DT
from App.config import getConfiguration
import pytz

class TestGetTimezone(NaayaFunctionalTestCase):
    """ TestCase for NySite.get_timezone, NySite.get_tzinfo """

    def setUp(self):
        self.winter = datetime(2011, 1, 1, 10, 0, 0, 0, pytz.timezone('UTC'))
        self.summer = datetime(2011, 6, 1, 10, 0, 0, 0, pytz.timezone('UTC'))
        self.config = getConfiguration()
        self.environ_patch = patch.dict(os.environ)
        self.environ_patch.start()
        self.config_patch = patch.dict(self.config.environment)
        self.config_patch.start()

    def tearDown(self):
        self.environ_patch.stop()
        self.config_patch.stop()

    def test_get_timezone1_zope_conf(self):
        """ 1. From buildout::zope-conf-additional """
        self.config.environment['TZ'] = 'Europe/Bucharest'
        tzinfo = self.portal.get_tzinfo()
        date_here = self.winter.astimezone(tzinfo)
        self.failUnlessEqual(date_here.date(), self.winter.date())
        self.failUnlessEqual(date_here.hour, 12)

    def test_get_timezone2_os_environ(self):
        """ 2. From os.environ """
        os.environ['TZ'] = 'Europe/Bucharest'
        tzinfo = self.portal.get_tzinfo()
        date_here = self.winter.astimezone(tzinfo)
        self.failUnlessEqual(date_here.date(), self.winter.date())
        self.failUnlessEqual(date_here.hour, 12)

    def test_get_timezone3_time_tzname(self):
        """ 3. From time.tzname """
        # We can't assume a certain timezone for the machine running this script
        expected = time.tzname
        timezone = self.portal.get_timezone()
        self.failUnlessEqual(timezone, expected[0])

    @patch.object(time, 'tzname')
    def test_get_timezone4_time_fallback(self, mock_method):
        """ 4. Hardcoded fallback """
        time.tzname = ()
        timezone = self.portal.get_timezone()
        self.failUnlessEqual(timezone, 'Europe/Copenhagen')

    def test_dst(self):
        self.config.environment['TZ'] = 'Europe/Bucharest'
        tzinfo = self.portal.get_tzinfo()
        date_nodst = self.winter.astimezone(tzinfo)
        date_dst = self.summer.astimezone(tzinfo)
        self.failUnlessEqual(date_nodst.date(), self.winter.date())
        self.failUnlessEqual(date_dst.date(), self.summer.date())
        self.failUnlessEqual(date_nodst.hour, 12 )
        self.failUnlessEqual(date_dst.hour, 12 + 1)
