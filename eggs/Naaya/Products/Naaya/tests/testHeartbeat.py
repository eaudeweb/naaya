from unittest import TestSuite, makeSuite

from zope import component

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.Naaya.interfaces import INySite
from naaya.core.interfaces import IHeartbeat
from naaya.core.heartbeat import Heartbeat

events = 0

@component.adapter(INySite, IHeartbeat)
def mockSubscriber(site, hb):
    global events
    events += 1

class TestHeartbeat(NaayaFunctionalTestCase):
    def afterSetUp(self):
        component.provideHandler(mockSubscriber)

    def beforeTearDown(self):
        pass

    def testHeartbeat(self):
        self.assertEqual(events, 0)
        self.browser.go('http://localhost/portal/heartbeat')
        self.assertEqual(events, 1)
        self.browser.go('http://localhost/portal/heartbeat')
        self.assertEqual(events, 1)
