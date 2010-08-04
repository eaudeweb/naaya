from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase

from Products.ZOpenArchives.OAIServer import manage_addOAIServer

class TestOAIServer(ZopeTestCase.ZopeTestCase):
    def test_basic(self):
        """ """
        manage_addOAIServer(self.app, 'oai_server', title=u'OAI Server')
        self.assertTrue(hasattr(self.app, 'oai_server'))
def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOAIServer))
    return suite
