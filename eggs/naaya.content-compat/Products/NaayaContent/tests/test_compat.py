import importlib
import os
import unittest
import warnings

COMPAT_DIR = os.path.dirname(os.path.dirname(__file__))


def compat_modules():
    """ Dotted names of the old Products.NaayaContent modules kept here """
    for package in sorted(os.listdir(COMPAT_DIR)):
        path = os.path.join(COMPAT_DIR, package)
        if not package.startswith('Ny') or not os.path.isdir(path):
            continue
        yield 'Products.NaayaContent.%s' % package
        for name in sorted(os.listdir(path)):
            if name.endswith('.py') and name != '__init__.py':
                yield 'Products.NaayaContent.%s.%s' % (package, name[:-3])


class CompatImportsTest(unittest.TestCase):
    """ old module paths, needed to load old pickles, point to naaya.content """

    def test_modules_import(self):
        modules = list(compat_modules())
        self.assertGreater(len(modules), 30)
        for dotted in modules:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                module = importlib.import_module(dotted)
            aliases = [value for name, value in vars(module).items()
                       if isinstance(value, type)]
            if '.' in dotted[len('Products.NaayaContent.'):]:
                self.assertTrue(aliases, dotted)
            for value in aliases:
                self.assertTrue(value.__module__.startswith('naaya.content.'),
                                (dotted, value))

    def assertDeprecatedImport(self, dotted):
        """ Import dotted; (re)loading it warns once, whatever the test order """
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            module = importlib.import_module(dotted)
        with self.assertWarns(DeprecationWarning):
            importlib.reload(module)
        return module

    def test_class_aliases(self):
        from naaya.content.file.file_item import NyFile_extfile
        from naaya.content.contact.contact_item import NyContact as Contact
        # the packages warn, the modules in them hold the class aliases
        self.assertDeprecatedImport('Products.NaayaContent.NyFile')
        self.assertDeprecatedImport('Products.NaayaContent.NyContact')
        from Products.NaayaContent.NyFile.NyFile import NyFile
        from Products.NaayaContent.NyContact.NyContact import NyContact
        self.assertIs(NyFile, NyFile_extfile)
        self.assertIs(NyContact, Contact)

    def test_constants(self):
        from naaya.content.base import constants as base_constants
        constants = self.assertDeprecatedImport(
            'Products.NaayaContent.constants')
        self.assertEqual(constants.MUST_BE_NONEMPTY,
                         base_constants.MUST_BE_NONEMPTY)
