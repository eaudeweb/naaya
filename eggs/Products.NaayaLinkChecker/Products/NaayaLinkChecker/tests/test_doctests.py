""" Doc tests
"""
import doctest
import unittest
from Globals import package_home
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.Naaya.tests.NaayaTestCase import FunctionalTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

class CustomFunctionalTestCase(FunctionalTestCase):
    home = package_home(globals())

def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
        Suite('Utils.py',
              optionflags=OPTIONFLAGS,
              package='Products.NaayaLinkChecker',
              test_class=CustomFunctionalTestCase),
        Suite('doc/functionality.txt',
              optionflags=OPTIONFLAGS,
              package='Products.NaayaLinkChecker',
              test_class=CustomFunctionalTestCase),
          ))
