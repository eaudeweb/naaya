from unittest import TestCase, TestSuite, makeSuite

class TestOAIHarverster(TestCase):
    """ """

class TestOAINamespace(TestCase):
    """ """

class TestOAIRecord(TestCase):
    """ """

class TestOAIRepository(TestCase):
    """ """

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestOAIHarverster))
    suite.addTest(makeSuite(TestOAINamespace))
    suite.addTest(makeSuite(TestOAIRecord))
    suite.addTest(makeSuite(TestOAIRepository))
    return suite
