from unittest import TestSuite, makeSuite

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.url.url_item import addNyURL

class TestTree(NaayaTestCase):
    def afterSetUp(self):
        addNyFolder(self.portal, id='myfol', title='myfol')
        addNyFolder(self.portal.myfol, id='f1', title='f1')
        addNyFolder(self.portal.myfol.f1, id='f1a', title='f1a')
        addNyFolder(self.portal.myfol.f1, id='f1b', title='f1b')
        addNyFolder(self.portal.myfol, id='f2', title='f2')
        addNyURL(self.portal.myfol.f1, id='u1c', title='u1c')
        addNyURL(self.portal.myfol.f1.f1b, id='u1bx', title='u1bx')

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfol'])

    def test_empty(self):
        myfol = self.portal.myfol
        myfol.manage_delObjects(['f1', 'f2'])
        output = self.portal.getSiteMapTree(myfol, True, [])
        self.assertEqual(output, {'ob': myfol, 'has_children':False})

    def test_full(self):
        myfol = self.portal.myfol
        output = self.portal.getSiteMapTree(myfol, True, ['myfol', 'myfol/f1', 'myfol/f1/f1b'])
        self.assertEqual(output,
            {'ob': myfol, 'has_children':True, 'children': [
                {'ob': myfol.f1, 'has_children': True, 'children': [
                    {'ob': myfol.f1.f1a, 'has_children': False},
                    {'ob': myfol.f1.f1b, 'has_children': True, 'children': [
                        {'ob': myfol.f1.f1b.u1bx, 'has_children': False},
                    ]},
                    {'ob': myfol.f1.u1c, 'has_children': False},
                ]},
                {'ob': myfol.f2, 'has_children': False},
            ]})

    def test_no_showitems(self):
        myfol = self.portal.myfol
        output = self.portal.getSiteMapTree(myfol, False, ['myfol', 'myfol/f1', 'myfol/f1/f1b'])
        self.assertEqual(output,
            {'ob': myfol, 'has_children':True, 'children': [
                {'ob': myfol.f1, 'has_children': True, 'children': [
                    {'ob': myfol.f1.f1a, 'has_children': False},
                    {'ob': myfol.f1.f1b, 'has_children': False},
                ]},
                {'ob': myfol.f2, 'has_children': False},
            ]})

    def test_expand(self):
        myfol = self.portal.myfol

        output = self.portal.getSiteMapTree(myfol, True, ['myfol'])
        self.assertEqual(output,
            {'ob': myfol, 'has_children':True, 'children': [
                {'ob': myfol.f1, 'has_children': True},
                {'ob': myfol.f2, 'has_children': False},
            ]})

        output = self.portal.getSiteMapTree(myfol, True, ['myfol', 'myfol/f1'])
        self.assertEqual(output,
            {'ob': myfol, 'has_children':True, 'children': [
                {'ob': myfol.f1, 'has_children': True, 'children': [
                    {'ob': myfol.f1.f1a, 'has_children': False},
                    {'ob': myfol.f1.f1b, 'has_children': True},
                    {'ob': myfol.f1.u1c, 'has_children': False},
                ]},
                {'ob': myfol.f2, 'has_children': False},
            ]})
