import unittest
import cPickle
from zope.component import getGlobalSiteManager
from naaya.component import bundles
from naaya.component.testing import ITestUtil, MyClass, clean_up_bundle


class BundleRegistrationTest(unittest.TestCase):

    def setUp(self):
        self.bundle_names = []

    def tearDown(self):
        for name in self.bundle_names:
            clean_up_bundle(name)

    def test_unique_name(self):
        self.bundle_names.append('some_random_test_bundle')
        my_bundle_1 = bundles.get('some_random_test_bundle')
        my_bundle_2 = bundles.get('some_random_test_bundle')
        self.assertTrue(my_bundle_1 is my_bundle_2)

    def test_pickle(self):
        self.bundle_names.append('some_random_test_bundle')
        my_bundle = bundles.get('some_random_test_bundle')
        jar = cPickle.dumps(my_bundle)
        self.assertTrue(cPickle.loads(jar) is my_bundle)

    def test_register_utility(self):
        self.bundle_names.append('some_random_test_bundle')
        my_bundle = bundles.get('some_random_test_bundle')
        ob = MyClass()
        my_bundle.registerUtility(ob)
        self.assertTrue(my_bundle.getUtility(ITestUtil) is ob)

    def test_inheritance(self):
        self.bundle_names.extend(['test_bundle_1', 'test_bundle_2'])
        my_bundle_1 = bundles.get('test_bundle_1')
        my_bundle_2 = bundles.get('test_bundle_2')
        my_bundle_2.set_parent(my_bundle_1)

        # inherit from global registry
        gsm = getGlobalSiteManager()
        ob_0 = MyClass()
        gsm.registerUtility(ob_0)
        self.assertTrue(my_bundle_2.getUtility(ITestUtil) is ob_0)
        gsm.unregisterUtility(ob_0)

        # inherit from parent
        ob_1 = MyClass()
        my_bundle_1.registerUtility(ob_1)
        self.assertTrue(my_bundle_2.getUtility(ITestUtil) is ob_1)

        # override
        ob_2 = MyClass()
        my_bundle_2.registerUtility(ob_2)
        self.assertTrue(my_bundle_2.getUtility(ITestUtil) is ob_2)

    def test_get_parent(self):
        self.bundle_names.extend(["Foo", "Bar"])
        foo = bundles.get("Foo")
        bar = bundles.get("Bar")

        # no parent was set
        gsm = getGlobalSiteManager()
        self.assertTrue(foo.get_parent() is gsm)

        # some parent was set
        foo.set_parent(bar)
        self.assertTrue(foo.get_parent() is bar)

    def test_customize_component(self):
        from zope import interface
        from zope.app.component.site import LocalSiteManager
        from naaya.component.interfaces import ICustomize

        class MyClassCustomizer(object):
            interface.implements(ICustomize)

            def __init__(self, target):
                self.target = target

            def customize(self, site_manager, name):
                site_manager.registerUtility(MyClass(color='red'), name=name)


        self.bundle_names.append('test-bundle')
        test_bundle = bundles.get('test-bundle')
        test_bundle.registerUtility(MyClass(color='green'), name='tomato')
        test_bundle.registerAdapter(MyClassCustomizer, [ITestUtil], ICustomize)

        site_manager = LocalSiteManager(None)
        site_manager.__bases__ = (test_bundle,)

        bundles.customize_utility(site_manager, ITestUtil, 'tomato')

        util = site_manager.getUtility(ITestUtil, name='tomato')
        self.assertEqual(util.color, 'red')
