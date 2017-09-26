import unittest

import transaction
import zope.app.component
from zope.testing import doctest
from Testing import ZopeTestCase

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

from Products.Five import zcml
import Products.Five
import edw.productsinfo

def configurationSetUp():
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('configure.zcml', Products.Five)
    zcml.load_config('configure.zcml', edw.productsinfo)

configurationSetUp()
class FunctionalTestClass(object):
    __bases__ = []
    def __init__(self, module, name):
        self.__module__ = module
        self.__name__ = name

    def setUp(self):
        self.app = ZopeTestCase.app()
        self.install()

    def tearDown(self):
        pass

    def install(self):
        self.add_root_user()
        self.login()
        self.add_portal()
        self.logout()
        transaction.commit()

    def add_root_user(self):
        atool = self.app.acl_users
        atool._doAddUser('admin', '', ['Manager'], [])

    def add_portal(self):
        try:
            from Products.Naaya.NySite import NySite
        except ImportError:
            self.portal = self.app
            return

        self.app._setObject('portal', NySite(
            'portal', 'portal', 'Naaya Test Site', 'en'))
        self.portal = getattr(self.app, 'portal')

    def login(self):
        '''Logs in.'''
        aclu = self.app.acl_users
        user = aclu.getUserById('admin').__of__(aclu)
        self.app.REQUEST.AUTHENTICATED_USER = user
        newSecurityManager(None, user)

    def logout(self):
        noSecurityManager()

class FunctionalTestCase(ZopeTestCase.PortalTestCase):
    """ Base """
    layer = FunctionalTestClass(__name__, 'FunctionalTestLayer')
    _configure_portal = 0

def test_suite():
    flags = (doctest.ELLIPSIS |
             doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    return unittest.TestSuite((
        ZopeTestCase.FunctionalDocFileSuite('README.txt',
              optionflags=flags,
              package='edw.productsinfo',
              test_class=FunctionalTestCase),
    ))
