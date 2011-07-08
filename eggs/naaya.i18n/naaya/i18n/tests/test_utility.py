from zope.i18n.interfaces import ITranslationDomain
from zope.component import queryUtility

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

from naaya.i18n.utilities import NyI18nTranslator


class TestTranslationUtility(NaayaTestCase):


    def test_utility_requirement(self):
        self.assertTrue(self.portal.REQUEST.has_key('PARENTS'))
        traverse_objects = self.portal.REQUEST['PARENTS']
        self.assertTrue(isinstance(traverse_objects, list))
        self.assertTrue(traverse_objects[0].getSite is not None)
        self.assertEqual(traverse_objects[0].getSite(), self.portal)

    def test_utility_existence(self):
        utility = queryUtility(ITranslationDomain, 'default')
        self.assertTrue(isinstance(utility, NyI18nTranslator))

    def test_utility_translation(self):
        utility = queryUtility(ITranslationDomain, 'default')
        self.assertEqual(utility.translate('${cnt} puppies', {'cnt': 2},
                                           self.portal.REQUEST),
                         '2 puppies')
