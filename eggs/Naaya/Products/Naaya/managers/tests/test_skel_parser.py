# Python imports
from unittest import TestSuite, makeSuite
from os.path import join, dirname

# Zope imports
import Globals

# Naaya imports
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.managers.skel_parser import skel_parser, TAG_MAPPING

class SkelTestCase(NaayaTestCase):

    def test_parser(self):
        TAG_MAPPING['testnode'] = {'type': 'list'}
        skel_content = open(join(dirname(__file__), 'skel.xml'), 'r').read()
        sk, error = skel_parser().parse('Garbage content')
        self.assertNotEqual(error, '')
        self.assertEqual(sk, None)
        sk, error = skel_parser().parse(skel_content)
        self.assertEqual(error, '')
        self.assertNotEqual(sk.root, None)
        self.assertEqual(len(sk.root.testnode), 4)
        self.assertFalse(isinstance(sk.root.forms, list))
        self.assertTrue(isinstance(sk.root.forms.forms, list))
        self.assertTrue(len(sk.root.forms.forms) > 1)
        self.assertNotEqual(sk.root.forms.forms[1].id, None)
        self.assertEqual(sk.root.layout.skins[0].styles, [])
        self.assertEqual(sk.root.syndication.remotechannels, [])
        self.assertFalse(isinstance(sk.root.others.images, list))
        self.assertNotEqual(sk.root.security, None)
        for role in sk.root.security.roles:
            self.assertNotEqual(role.name, None)
            self.assertNotEqual(role.name, '')
            for permission in role.permissions:
                self.assertNotEqual(permission.name, None)
                self.assertNotEqual(permission.name, '')
            if role == 'Authenticated':
                expected = ["Naaya - Add comments for content",
                            "Naaya - Bulk download", "Naaya - Skip Captcha"]
                self.assertEqual(set(map(role.permissions, lambda x: x.name)),
                                 set(expected))
