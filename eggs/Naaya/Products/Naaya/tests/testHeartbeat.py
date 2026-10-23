from zope import component

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.interfaces import INySite
from naaya.core.interfaces import IHeartbeat
from naaya.core.utils import _cooldown_map


class TestHeartbeat(NaayaFunctionalTestCase):
    def afterSetUp(self):
        _cooldown_map.pop("site heartbeat '/portal'", None)
        self.events = []

        @component.adapter(INySite, IHeartbeat)
        def subscriber(site, hb):
            self.events.append(site)

        self.subscriber = subscriber
        component.provideHandler(subscriber)

    def beforeTearDown(self):
        component.getGlobalSiteManager().unregisterHandler(self.subscriber)

    def testHeartbeat(self):
        self.browser.go('http://localhost/portal/heartbeat')
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0].getId(), 'portal')
        # a second call within the cooldown interval does not notify again
        self.browser.go('http://localhost/portal/heartbeat')
        self.assertEqual(len(self.events), 1)
