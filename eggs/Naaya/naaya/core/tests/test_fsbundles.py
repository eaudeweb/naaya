import os.path
import unittest
import tempfile
import shutil
from zope.component import getGlobalSiteManager
from naaya.component import bundles
from naaya.component.testing import ITestUtil, MyClass, clean_up_bundle
from Products.NaayaCore.FormsTool.interfaces import ITemplate


class FilesystemBundlesTest(unittest.TestCase):

    def setUp(self):
        self.bundle_names = []
        self.tmp = tempfile.mkdtemp()
        self.bundle_path = os.path.join(self.tmp, 'foo.bundle')
        os.makedirs(os.path.join(self.bundle_path, 'templates'))

    def tearDown(self):
        shutil.rmtree(self.tmp)
        for name in self.bundle_names:
            clean_up_bundle(name)

    def _write_template(self, name, data):
        tmpl_path = os.path.join(self.bundle_path, 'templates', name + '.zpt')
        f = open(tmpl_path, 'wb')
        f.write(data)
        f.close()

    def test_load_templates(self):
        self.bundle_names.append("CHM-Foo")
        self._write_template('bar', "Hello Bar")

        from naaya.core import fsbundles
        fsbundles.load_filesystem_bundle(self.bundle_path, "CHM-Foo")
        foo = bundles.get("CHM-Foo")
        bar = foo.queryUtility(ITemplate, name='bar')

        self.assertTrue(bar is not None, "Template `bar` not found")
        bar._cook_check()
        self.assertEqual(bar._text, "Hello Bar")

    def test_parent_bundle(self):
        self.bundle_names.append("CHM-Foo")

        from naaya.core import fsbundles
        fsbundles.load_filesystem_bundle(self.bundle_path, "CHM-Foo", "CHM")
        foo = bundles.get("CHM-Foo")
        self.assertTrue(foo.get_parent() is bundles.get("CHM"), "Wrong parent")

    def test_parent_bundle_from_cfg_file(self):
        self.bundle_names.append("CHM-Foo")
        self.bundle_names.append("Bar")
        f = open(os.path.join(self.bundle_path, 'bundle.cfg'), 'wb')
        f.write("[bundle]\nparent-bundle = Bar\n")
        f.close()

        from naaya.core import fsbundles
        fsbundles.load_filesystem_bundle(self.bundle_path, "CHM-Foo")
        foo = bundles.get("CHM-Foo")
        self.assertTrue(foo.get_parent() is bundles.get("Bar"), "Wrong parent")

    def test_reloading(self):
        self.bundle_names.append("CHM-Foo")
        self._write_template('bar', "Hello Bar")
        gsm = getGlobalSiteManager()

        def tmpl_text(name):
            foo = bundles.get("CHM-Foo")
            tmpl = foo.queryUtility(ITemplate, name=name)
            if tmpl is None:
                return None
            else:
                tmpl._cook_check()
                return tmpl._text

        from naaya.core import fsbundles
        from naaya.component.interfaces import IBundleReloader
        fsbundles.load_filesystem_bundle(self.bundle_path, "CHM-Foo", "CHM")

        self.assertEqual(tmpl_text('bar'), "Hello Bar")
        self.assertEqual(tmpl_text('baz'), None)

        reloader = gsm.queryUtility(IBundleReloader, name="CHM-Foo")
        self.assertTrue(reloader is not None, "Reloader not found")

        self._write_template('bar', "Hello Bar 2")
        self._write_template('baz', "Hello Baz")
        reloader.reload_bundle()

        self.assertEqual(tmpl_text('bar'), "Hello Bar 2")
        self.assertEqual(tmpl_text('baz'), "Hello Baz")


    def test_reloading_removed_templates(self):
        from nose import SkipTest
        raise SkipTest("Reloading does not detect removed templates yet.")


class BundleFactoryTest(unittest.TestCase):

    def setUp(self):
        from Products.Naaya.interfaces import INySite
        from Products.Naaya.NySite import NySite
        from naaya.core.interfaces import IFilesystemBundleFactory
        from naaya.core.fsbundles import register_bundle_factory
        self.bundle_names = []
        self.tmp = tempfile.mkdtemp()
        register_bundle_factory(self.tmp, 'FooSites-', 'Foo')
        self.site = NySite('bar')
        self.site.set_bundle(bundles.get('Foo'))

    def tearDown(self):
        from Products.Naaya.interfaces import INySite
        from naaya.core.interfaces import IFilesystemBundleFactory
        shutil.rmtree(self.tmp)
        for name in self.bundle_names:
            clean_up_bundle(name)
        gsm = getGlobalSiteManager()
        assert gsm.unregisterAdapter(required=(INySite,),
                                     provided=IFilesystemBundleFactory,
                                     name='Foo')

    def test_create_bundle(self):
        from naaya.core.fsbundles import get_filesystem_bundle_factory
        factory = get_filesystem_bundle_factory(self.site)
        bundle = factory()
        self.assertEqual(bundle.__name__, 'FooSites-bar')
        self.assertEqual(os.listdir(self.tmp), ['FooSites-bar.bundle'])
        self.assertEqual(self.site.get_bundle(), bundle)

    def test_bundle_cfg(self):
        from naaya.core.fsbundles import get_filesystem_bundle_factory
        factory = get_filesystem_bundle_factory(self.site)
        bundle = factory()
        cfg_path = os.path.join(self.tmp, 'FooSites-bar.bundle', 'bundle.cfg')
        f = open(cfg_path, 'rb')
        data = list(f)
        f.close()
        self.assertTrue('parent-bundle = Foo\n') in data

    def test_create_preexisting_bundle(self):
        from naaya.core.fsbundles import get_filesystem_bundle_factory
        factory = get_filesystem_bundle_factory(self.site)
        bundle = factory()
        self.assertRaises(ValueError, factory)

    def test_wrong_site_bundle(self):
        from naaya.core.fsbundles import get_filesystem_bundle_factory
        self.site.set_bundle(bundles.get('Baz'))
        factory = get_filesystem_bundle_factory(self.site)
        self.assertTrue(factory is None)
