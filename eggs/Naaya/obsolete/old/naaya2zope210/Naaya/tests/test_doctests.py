""" Doc tests
"""
import doctest
import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.Naaya.tests.NaayaTestCase import FunctionalTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
            Suite('doc/naaya.txt',
                  optionflags=OPTIONFLAGS,
                  package='Products.Naaya',
                  test_class=FunctionalTestCase) ,
              ))
