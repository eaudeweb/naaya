# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
# David Batranu, Eau de Web


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
        Suite('doc/functionality.txt',
              optionflags=OPTIONFLAGS,
              package='Products.NaayaContent.NyNews',
              test_class=CustomFunctionalTestCase),
          ))
