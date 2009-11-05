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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
# Alex Morega, Eau de Web

import os
from zope.configuration.xmlconfig import xmlconfig
from StringIO import StringIO
from copy import deepcopy
import transaction
from Testing import ZopeTestCase
from Testing.ZopeTestCase import user_name, user_password
from Testing.ZopeTestCase import Functional
from AccessControl.User import nobody
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Globals import package_home


test_zcml = """<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:meta="http://namespaces.zope.org/meta"
    xmlns:five="http://namespaces.zope.org/five">

  <!-- this comes from Five/skel/site.zcml -->

  <include package="Products.Five"/>
  <include files="%(INSTANCE_HOME)s/etc/package-includes/*-meta.zcml" />
  <include files="%(INSTANCE_HOME)s/etc/package-includes/*-configure.zcml" />
  <meta:redefinePermission from="zope2.Public" to="zope.Public" />

  <five:loadProducts/>
  <five:loadProductsOverrides/>

</configure>
""" % {'INSTANCE_HOME': INSTANCE_HOME}

xmlconfig(StringIO(test_zcml), testing=True)

ZopeTestCase.installProduct('Localizer')
ZopeTestCase.installProduct('TextIndexNG3')
ZopeTestCase.installProduct('NaayaCore')
ZopeTestCase.installProduct('NaayaContent')
ZopeTestCase.installProduct('NaayaBase')
ZopeTestCase.installProduct('naayaHotfix')
ZopeTestCase.installProduct('Naaya')
ZopeTestCase.installProduct('PythonScripts')
ZopeTestCase.installProduct('ZMIntrospection')

class MailDivertLayer(object):
    def get_log(self):
        return self.log
    
    def clear_log(self):
        self.log = []
    
    def divert(self):
        class smtplib_replacement(object):
            class SMTP:
                def __init__(s, server, port):
                    self.log.append( ('init', {}) )
                
                def sendmail(s, from_addr, to_addr, message):
                    self.log.append( ('sendmail', {'from': from_addr, 'to': to_addr, 'message': message}) )
                
                def quit(s):
                    self.log.append( ('quit', {}) )
        
        from Products.NaayaCore.EmailTool import EmailTool
        self._orig_smtplib = EmailTool.smtplib
        EmailTool.smtplib = smtplib_replacement
        self.log = []
    
    def restore(self):
        from Products.NaayaCore.EmailTool import EmailTool
        EmailTool.smtplib = self._orig_smtplib

class NaayaLayerClass(object):
    """Layer to test Naaya.

    The goal of a testrunner layer is to isolate initializations common
    to a lot of testcases. The setUp of the layer is run only once, then
    all tests for the testcases belonging to the layer are run.
    """

    # The setUp of bases is called autmatically first
    __bases__ = []

    def __init__(self, module, name):
        self.__module__ = module
        self.__name__ = name
        self.mail_divert = MailDivertLayer()

    def setUp(self):
        from Products.ExtFile import ExtFile
        ExtFile.REPOSITORY_PATH = ['var', 'testing']
        self.app = ZopeTestCase.app()
        self.install()
        self.mail_divert.divert()

    def tearDown(self):
        self.mail_divert.restore()
        repository = os.path.join(INSTANCE_HOME, 'var', 'testing')
        if os.path.isdir(repository):
            import shutil
            shutil.rmtree(repository, 1)

    def install(self):
        self.addRootUser()
        self.login()
        self.addPortal()
        self.addPortalManager()
        self.addPortalContributor()
        self.addPortalReviewer()
        self.logout()
        transaction.commit()

    def addRootUser(self):
        atool = self.app.acl_users
        atool._doAddUser('admin', '', ['Manager'], [])
        
    def addPortalManager(self, portal_id='portal', user=user_name, password=user_password):
        portal = getattr(self.app, portal_id)
        atool = getattr(portal, 'acl_users')
        atool._doAddUser(user, password, ['Manager'], '', '', '', '')
    
    def addPortalContributor(self, portal_id='portal'):
        portal = getattr(self.app, portal_id)
        atool = getattr(portal, 'acl_users')
        atool._doAddUser('contributor', 'contributor', ['Contributor'], '',
            'Contributor', 'Test', 'contrib@example.com')

    def addPortalReviewer(self, portal_id='portal'):
        portal = getattr(self.app, portal_id)
        atool = getattr(portal, 'acl_users')
        atool._doAddUser('reviewer', 'reviewer', ['Reviewer'], '',
            'Reviewer', 'Test', 'reviewer@example.com')

    def login(self):
        '''Logs in.'''
        aclu = self.app.acl_users
        user = aclu.getUserById('admin').__of__(aclu)
        self.app.REQUEST.AUTHENTICATED_USER = user
        newSecurityManager(None, user)

    def logout(self):
        noSecurityManager()

    def addPortal(self):
        from Products.Naaya.NySite import manage_addNySite
        manage_addNySite(self.app, 'portal', 'Naaya Test Site')
        self.portal = getattr(self.app, 'portal')
        self.portal.mail_address_from = 'from.zope@example.com'

NaayaDefaultLayer = NaayaLayerClass(__name__, 'NaayaDefaultLayer')

class NaayaTestCase(ZopeTestCase.PortalTestCase):

    layer = NaayaDefaultLayer

    # configuration is already done in the layer
    _configure_portal = 0

    def _setup(self):
        ZopeTestCase.PortalTestCase._setup(self)

        # Some skins need sessions (not sure if it's a good thing).
        # Localizer too.
        # Both lines below are needed.
        from Products.Transience.TransientObject import TransientObject
        SESSION = TransientObject('x')
        self.app.REQUEST['SESSION'] = SESSION
        self.app.REQUEST.SESSION = SESSION
        self.portal.REQUEST.AUTHENTICATED_USER = nobody
        self.portal.REQUEST.PARENTS = [self.portal, self.app]
    
    def login(self, name=user_name):
        '''Logs in.'''
        uf = self.portal.acl_users
        user = uf.getUserById(name)
        if not hasattr(user, 'aq_base'):
            user = user.__of__(uf)
        self.portal.REQUEST.AUTHENTICATED_USER = user
        newSecurityManager(None, user)
    
    def portalLogin(self, name=user_name):
        return self.login(name)

    def portalLogout(self):
        self.portal.REQUEST.AUTHENTICATED_USER = nobody
        newSecurityManager(None, nobody)

    def printLogErrors(self, min_severity=0):
        """Print out the log output on the console.
        """
        import zLOG
        if hasattr(zLOG, 'old_log_write'):
            return
        def log_write(subsystem, severity, summary, detail, error,
                      PROBLEM=zLOG.PROBLEM, min_severity=min_severity):
            if severity >= min_severity:
                print "%s(%s): %s %s" % (subsystem, severity, summary, detail)
        zLOG.old_log_write = zLOG.log_write
        zLOG.log_write = log_write

    def install_content_type(self, meta_type):
        content_type = self.portal.get_pluggable_item(meta_type)
        self.portal.manage_install_pluggableitem(meta_type)
        add_content_permissions = deepcopy(self.portal.acl_users.getPermission('Add content'))
        add_content_permissions['permissions'].append(content_type['permission'])
        self.portal.acl_users.editPermission('Add content', **add_content_permissions)

    def remove_content_type(self, meta_type):
        content_type = self.portal.get_pluggable_item(meta_type)
        add_content_permissions = deepcopy(self.portal.acl_users.getPermission('Add content'))
        add_content_permissions['permissions'].remove(content_type['permission'])
        self.portal.acl_users.editPermission('Add content', **add_content_permissions)
        self.portal.manage_uninstall_pluggableitem(meta_type)

def load_test_file(filename, globals_):
    """ Load data from a test file """
    home = package_home(globals_)
    filename = os.path.sep.join([home, filename])
    data = StringIO(open(filename, 'rb').read())
    data.filename = os.path.basename(filename)
    return data

class FunctionalTestCase(Functional, NaayaTestCase):
    '''Base class for functional Plone tests'''

    __implements__ = (Functional.__implements__, NaayaTestCase.__implements__)
    
    home = package_home(globals())
    
    def loadFile(self, filename):
        """ load a file"""
        filename = os.path.sep.join([self.home, filename])
        data = StringIO(open(filename, 'rb').read())
        data.filename = os.path.basename(filename)
        return data

