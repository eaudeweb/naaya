from zope.component import getGlobalSiteManager
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase, capture_events
from Products.Naaya.interfaces import INyPluggableItemInstalled

URL_META_TYPE = 'Naaya URL'

class PluggableInstallTest(NaayaTestCase):
    def setUp(self):
        self.portal.manage_uninstall_pluggableitem(URL_META_TYPE)

    @capture_events(INyPluggableItemInstalled)
    def test_install_event(self, events):
        self.portal.manage_install_pluggableitem(URL_META_TYPE)

        self.assertEqual(len(events), 1)
        e = events[0]
        self.assertEqual(e.meta_type, URL_META_TYPE)
        self.assertTrue(e.context is self.portal)
