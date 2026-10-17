import os
import unittest
import tempfile
import shutil
import warnings

from unittest.mock import patch
import transaction
from Testing.ZopeTestCase import Functional
from zope.interface import alsoProvides
from zope.component import getGlobalSiteManager
from Products.Naaya.interfaces import INySite
from naaya.i18n.patches import populate_threading_local

class ITestSite(INySite):
    """ Marker interface for a test portal; useful for registering fixtures """

def divert_mail():
    delivery_patch = patch('Products.NaayaCore.EmailTool'
                           '.EmailTool.delivery_for_site')
    mock_delivery = delivery_patch.start().return_value

    mail_log = []
    def mock_send(from_addr, to_addrs, message):
        info = {'from': from_addr, 'to': to_addrs, 'message': message}
        # TODO no need to log `init` and `quit`, just the messages.
        mail_log.append(('init', {}))
        mail_log.append(('sendmail', info))
        mail_log.append(('quit', {}))

    mock_delivery.send.side_effect = mock_send

    return mail_log, delivery_patch.stop

def wrap_with_request(app):
    from io import BytesIO
    from ZPublisher.HTTPRequest import HTTPRequest
    from ZPublisher.HTTPResponse import HTTPResponse
    from Acquisition import Implicit

    class FakeRootObject(Implicit):
        def bobobase_modification_time(self):
            from DateTime import DateTime
            return DateTime()

    fake_root = FakeRootObject()
    fake_root.app = app

    stdin = BytesIO()
    environ = {'REQUEST_METHOD': 'GET',
               'SERVER_NAME': 'nohost',
               'SERVER_PORT': '80'}
    request = HTTPRequest(stdin, environ, HTTPResponse(), clean=1)

    anonymous_user = fake_root.app.acl_users._nobody
    request.AUTHENTICATED_USER = anonymous_user

    fake_root.REQUEST = request

    return fake_root

def capture_events(*required):
    """
    Register an event handler for `required` and collect events in a list.
    Usage::

        class MyTest(unittest.TestCase):
            @capture_events(IZipImportEvent)
            def test_zip_events(self, events):
                # do something that generates events
                self.assertEqual(len(events), 1)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            events = []
            args += (events,)
            gsm = getGlobalSiteManager()
            gsm.registerHandler(events.append, required)
            try:
                return func(*args, **kwargs)
            finally:
                gsm.unregisterHandler(events.append, required)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

class NaayaTestLayer:
    """zope.testrunner layer that boots Zope from $NAAYA_ZOPE_CONF and creates a test portal."""
    _tzope = None          # ZopeTestEnvironment, started by the first setUp
    _cleanup_portal = None
    _cleanup_test = None
    _portal_id = None

    @classmethod
    def setUp(cls):
        """Layer-level setup: create portal (once per layer)."""
        # Suppress ResourceWarnings from third-party code (ZODB blob
        # storage, zipfile) that we cannot fix.
        warnings.filterwarnings('ignore', category=ResourceWarning,
                                module=r'ZODB\.blob')
        warnings.filterwarnings('ignore', category=ResourceWarning,
                                module=r'zipfile')

        if NaayaTestLayer._tzope is None:
            zope_conf = os.environ.get('NAAYA_ZOPE_CONF')
            if not zope_conf:
                raise RuntimeError("Set NAAYA_ZOPE_CONF to the zope.conf of the instance")
            from Products.Naaya.tests.zope_environment import zope_test_environment
            NaayaTestLayer._tzope = zope_test_environment(zope_conf)
        tzope = cls._tzope

        try:
            from Products.ExtFile import ExtFile
            ExtFile.REPOSITORY_PATH = ['var', 'testing']
        except ImportError:
            pass

        cleanup, portal_db = tzope.db_layer()
        app = portal_db.open().root()['Application']
        app.acl_users._doAddUser('admin', '', ['Manager', 'Administrator'], [])

        # Create temp_folder with session_data for SESSION support.
        # Normally provided by the <zodb_db temporary> mount point, but
        # the test DemoStorage doesn't have it.
        if 'temp_folder' not in app.objectIds():
            from OFS.Folder import Folder
            from Products.Transience.Transience import TransientObjectContainer
            app._setObject('temp_folder', Folder('temp_folder'))
            app.temp_folder._setObject(
                'session_data',
                TransientObjectContainer('session_data',
                                         title='Session Data Container',
                                         timeout_mins=20))

        # Set up session infrastructure: browser_id_manager +
        # session_data_manager so REQUEST.SESSION works in WSGI requests.
        if 'browser_id_manager' not in app.objectIds():
            from Products.Sessions.BrowserIdManager import BrowserIdManager
            from Products.Sessions.SessionDataManager import SessionDataManager
            app._setObject('browser_id_manager', BrowserIdManager('browser_id_manager'))
            app._setObject('session_data_manager',
                           SessionDataManager('session_data_manager',
                                              title='Session Data Manager',
                                              path='/temp_folder/session_data',
                                              requestName='SESSION'))

        transaction.commit()

        fake_root = wrap_with_request(app)
        wrapped_app = fake_root.app
        admin_user = wrapped_app.acl_users.getUserById('admin')
        fake_root.REQUEST.AUTHENTICATED_USER = admin_user

        from Products.Naaya.NySite import manage_addNySite
        cls._portal_id = 'portal'
        manage_addNySite(wrapped_app, cls._portal_id, 'Naaya Test Site')

        portal = getattr(wrapped_app, cls._portal_id)
        alsoProvides(portal, ITestSite)
        portal.mail_address_from = 'from.zope@example.com'
        portal.administrator_email = 'site.admin@example.com'

        acl_users = portal.acl_users
        acl_users._doAddUser('test_user_1_', 'secret', ['Manager'],
                             '', '', '', '')
        acl_users._doAddUser('site_admin', 'site_admin', ['Administrator'], '',
                             'Site', 'Admin', 'site_admin@example.com')
        acl_users._doAddUser('contributor', 'contributor', ['Contributor'], '',
                             'Contributor', 'Test', 'contrib@example.com')
        acl_users._doAddUser('reviewer', 'reviewer', ['Reviewer'], '',
                             'Reviewer', 'Test', 'reviewer@example.com')
        acl_users._doAddUser('user1', 'user1', ['Contributor'], '',
                             'User', 'One', 'user1@example.com')
        acl_users._doAddUser('user2', 'user2', ['Contributor'], '',
                             'User', 'Two', 'user2@example.com')
        acl_users._doAddUser('user3', 'user3', ['Contributor'], '',
                             'User', 'Three', 'user3@example.com')

        transaction.commit()
        cls._cleanup_portal = cleanup

        cls._old_tmp = tempfile.tempdir
        tempfile.tempdir = cls._tmp_dir = tempfile.mkdtemp()

    @classmethod
    def tearDown(cls):
        """Layer-level teardown."""
        if cls._cleanup_portal is not None:
            cls._cleanup_portal()
            cls._cleanup_portal = None

        try:
            from App.config import getConfiguration
            instance_home = getConfiguration().instancehome
        except Exception:
            instance_home = os.environ.get('INSTANCE_HOME', '')
        repository = os.path.join(instance_home, 'var', 'testing')
        if os.path.isdir(repository):
            shutil.rmtree(repository)

        # only the directory created in setUp, tempfile.tempdir may point elsewhere
        shutil.rmtree(cls._tmp_dir, True)
        tempfile.tempdir = cls._old_tmp

    @classmethod
    def testSetUp(cls):
        """Per-test setup: DemoStorage wrapper.

        Stores per-test state on the layer class.  NaayaTestCase._callSetUp()
        copies them to the test instance before setUp() runs.
        """
        tzope = cls._tzope
        cls._mail_log, cls._restore_mail = divert_mail()
        cleanup, test_db = tzope.db_layer()

        cls._db_connection = test_db.open()
        app = cls._db_connection.root()['Application']
        fake_root = wrap_with_request(app)
        wrapped_app = fake_root.app

        cls._current_app = wrapped_app
        cls._current_portal = wrapped_app[cls._portal_id]
        cls._current_fake_request = fake_root.REQUEST

        cls._cleanup_test = cleanup

    @classmethod
    def testTearDown(cls):
        """Per-test teardown."""
        if cls._restore_mail is not None:
            cls._restore_mail()
            cls._restore_mail = None
        if cls._cleanup_test is not None:
            transaction.abort()
            cls._cleanup_test()
            cls._cleanup_test = None
        # Reset the security manager so that functional tests that log in
        # via twill (ZPublisher sets it) don't leak into the next test.
        from AccessControl.SecurityManagement import noSecurityManager
        noSecurityManager()


class NaayaTestCase(unittest.TestCase):

    layer = NaayaTestLayer

    def _callSetUp(self):
        """Called by unittest.TestCase.run() after testSetUp() but before setUp().

        This injects per-test attributes (portal, app, etc.) from the layer
        so they are available even in tests that bypass NaayaTestCase.setUp().
        """
        layer = type(self).layer
        self.app = layer._current_app
        self.portal = layer._current_portal
        self.fake_request = layer._current_fake_request
        self.mail_log = layer._mail_log
        self.wsgi_request = layer._tzope.wsgi_app
        populate_threading_local(self.portal, self.portal.REQUEST)
        self.portal.REQUEST['PARENTS'] = [self.portal, self.app]
        self.setUp()

    def setUp(self):
        #Cleanup all action logs before starting
        action_logger = self.portal.getActionLogger()
        items = dict(action_logger.items())
        for entry_id, log_entry in items.items(): #clean action logger
            del action_logger[entry_id]
        transaction.commit()

        self.afterSetUp()

    def tearDown(self):
        self.beforeTearDown()

    def afterSetUp(self):
        # TODO: deprecate and remove
        pass

    def beforeTearDown(self):
        # TODO: deprecate and remove
        pass

    def login(self, name='test_user_1_'):
        # TODO: deprecate and remove
        acl_users = self.portal.acl_users
        user = acl_users.getUserById(name).__of__(acl_users)
        self.fake_request.AUTHENTICATED_USER = user
        from AccessControl.SecurityManagement import newSecurityManager
        newSecurityManager(None, user)

    def logout(self):
        # TODO: deprecate and remove
        self.fake_request.AUTHENTICATED_USER = self.app.acl_users._nobody
        from AccessControl.SecurityManagement import noSecurityManager
        noSecurityManager()

    def _portal(self):
        # TODO: deprecate and remove
        return self.portal

    def printLogErrors(self, min_severity=0):
        """Print out the log output on the console.
        """
        import logging
        logger = logging.getLogger('event')
        logger.setLevel(min_severity)
        handler = logging.StreamHandler()
        handler.setLevel(min_severity)
        logger.addHandler(handler)

    def install_content_type(self, meta_type):
        self.portal.manage_install_pluggableitem(meta_type)

    def remove_content_type(self, meta_type):
        self.portal.manage_uninstall_pluggableitem(meta_type)

    def serve_http(self, host='localhost', port=8081):
        from webob.dec import wsgify
        @wsgify.middleware
        def no_hop_by_hop(request, app):
            """ remove the Connection hop-by-hop header """
            response = request.get_response(app)
            del response.headers['Connection']
            return response

        from wsgiref.simple_server import make_server
        server = make_server(host, port, no_hop_by_hop(self.wsgi_request))
        print('serving pages on http://%s:%d/; press ^C to stop' % (host, port))
        server.serve_forever()

class FunctionalTestCase(NaayaTestCase, Functional): # not really, but good enough for us
    pass
