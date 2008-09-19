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

import time
import transaction
from Testing import ZopeTestCase
from Testing.ZopeTestCase import base
from Products.Naaya.NySite import manage_addNySite
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager

portal_name = 'portal'
from Testing.ZopeTestCase import user_name
from Testing.ZopeTestCase import user_password

ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG2')
ZopeTestCase.installProduct('NaayaCore')
ZopeTestCase.installProduct('NaayaContent')
ZopeTestCase.installProduct('NaayaBase')
ZopeTestCase.installProduct('naayaHotfix')
ZopeTestCase.installProduct('Naaya')
ZopeTestCase.installProduct('iHotfix')
ZopeTestCase.installProduct('PythonScripts')

#-------------------------------------------------------------------------------
# The folowing are patches needed because Localizer doesn't work
# well within ZTC
# This one is needed by ProxyTool.
def get_selected_language(self):
    """ """
    return 'en'

from Products.Localizer.Localizer import LanguageManager
LanguageManager.get_selected_language = get_selected_language

# Dummy portal_catalog.
from OFS.SimpleItem import SimpleItem
class DummyTranslationService(SimpleItem):
    meta_type = 'Translation Service'
    id = 'translation_service'
    def translate(self, domain, msgid, *args, **kw):
        return msgid

    def getDomainInfo(self):
        return [(None, 'Localizer/default')]

    def manage_addDomainInfo(self, domain, path, REQUEST=None, **kw):
        pass

# Dummy MessageCatalog
class DummyMessageCatalog:
    def __call__(self, message, *args, **kw):
        return message

    def get_selected_language(self):
        "xxx"
        return 'en'

    def get_languages(self):
        return ['en', 'fr']

    def manage_import(self, *args, **kw):
        pass

    def wl_isLocked(self):
        return None # = False

#-------------------------------------------------------------------------------
class NaayaInstaller:
    def __init__(self, app, quiet=0):
        if not quiet: 
            ZopeTestCase._print('Adding Naaya Site ... ')
        self.app = app
        self._start = time.time()
        self._quiet = quiet

    def install(self, portal_id):
        self.addUser()
        self.login()
        self.addPortal(portal_id)
        self.addPortalManager(portal_id)
        self.fixupTranslationServices(portal_id)
        self.logout()

    def addUser(self):
        atool = self.app.acl_users
        atool._doAddUser('admin', '', ['Owner'], [])

    def login(self):
        atool = self.app.acl_users
        user = atool.getUserById('admin').__of__(atool)
        self.app.REQUEST.AUTHENTICATED_USER = user
        newSecurityManager(None, user)

    def addPortal(self, portal_id):
        manage_addNySite(self.app, portal_id)

    def addPortalManager(self, portal_id, user=user_name, password=user_password):
        portal = getattr(self.app, portal_id)
        atool = getattr(portal, 'acl_users')
        atool._doAddUser(user_name, password, ['Manager'], '', '', '', '')

    # Change translation_service to DummyTranslationService
    def fixupTranslationServices(self, portal_id):
        portal = getattr(self.app, portal_id)
        portal.translation_service = DummyTranslationService()
        localizer = portal.Localizer
        for domain in localizer.objectIds():
            setattr(localizer, domain, DummyMessageCatalog())

    def logout(self):
        noSecurityManager()
        transaction.get().commit()
        if not self._quiet: 
            ZopeTestCase._print('done (%.3fs)\n' 
                % (time.time() - self._start,))

def setupPortal(PortalInstaller=NaayaInstaller):
    app = ZopeTestCase.app()
    if not hasattr(app, portal_name):
        PortalInstaller(app).install(portal_name)
    ZopeTestCase.close(app)
setupPortal()
#
# Naaya Test Care
#
class NaayaTestCase(base.TestCase):
    '''Base test case for testing Naaya portals'''

    _configure_portal = 1

    def setUp(self):
        '''Sets up the fixture. Do not override,
           use the hooks instead.
        '''
        try:
            self.beforeSetUp()
            self.app = self._app()
            self.portal = self._portal()
            self._setup()
            self.afterSetUp()
        except:
            self._clear()
            raise

    def _portal(self):
        '''Returns the portal object for a test.'''
        return self.getPortal()

    def _setup(self):
        '''Configures the portal. Framework authors may
           override.
        '''
        pass

    def getPortal(self, portal_name=portal_name):
        '''Returns the portal object to the setup code.
           Will typically be overridden by subclasses
           to return the object serving as the "portal".

           Note: This method should not be called by tests!
        '''
        return getattr(self.app, portal_name)

    def login(self, name=user_name):
        '''Logs in.'''
        uf = self.portal.acl_users
        user = uf.getUserById(name)
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        self.portal.REQUEST.AUTHENTICATED_USER = user
        newSecurityManager(None, user)
        
    def logout(self):
        '''Logs out.'''
        noSecurityManager()
