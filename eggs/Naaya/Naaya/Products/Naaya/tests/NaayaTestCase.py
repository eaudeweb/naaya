import os
import unittest
import tempfile
import shutil

from mock import patch
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
    from StringIO import StringIO
    from ZPublisher.HTTPRequest import HTTPRequest
    from ZPublisher.HTTPResponse import HTTPResponse
    from Acquisition import Implicit

    class FakeRootObject(Implicit): pass

    fake_root = FakeRootObject()
    fake_root.app = app

    stdin = StringIO()
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
        wrapper.func_name = func.func_name
        return wrapper
    return decorator

class NaayaTestCase(unittest.TestCase):

    _naaya_plugin = 'NaayaPortalTestPlugin'
    _naaya_test_enabled = False

    def run(self, result=None):
        if self._naaya_test_enabled:
            super(NaayaTestCase, self).run(result)
        else:
            from nose import SkipTest
            raise SkipTest("NaayaPortalTestPlugin needed for %s" % type(self))

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
        print 'serving pages on http://%s:%d/; press ^C to stop' % (host, port)
        server.serve_forever()

class FunctionalTestCase(NaayaTestCase, Functional): # not really, but good enough for us
    pass

from nose.plugins import Plugin

class NaayaPortalTestPlugin(Plugin):
    """
    Nose plugin that prepares the environment for a NaayaTestCase to run
    """
    name = 'naaya-portal'

    def __init__(self, tzope):
        Plugin.__init__(self)
        self.tzope = tzope
        self.cleanup_portal_layer = None
        self.cleanup_test_layer = None

    def portal_fixture(self, app):
        """ Create and return a portal"""
        from Products.Naaya.NySite import manage_addNySite
        portal_id = 'portal'
        manage_addNySite(app, portal_id, 'Naaya Test Site')
        return portal_id

    def portal_setup(self, app):
        """ Do some setup for this portal """
        portal = getattr(app, self.portal_id)
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

    def begin(self):
        from Products.ExtFile import ExtFile
        ExtFile.REPOSITORY_PATH = ['var', 'testing']

        cleanup, portal_db_layer = self.tzope.db_layer()

        app = portal_db_layer.open().root()['Application']
        app.acl_users._doAddUser('admin', '', ['Manager', 'Administrator'], [])
        transaction.commit()

        fake_root = wrap_with_request(app)
        wrapped_app = fake_root.app
        admin_user = wrapped_app.acl_users.getUserById('admin')
        fake_root.REQUEST.AUTHENTICATED_USER = admin_user

        self.portal_id = self.portal_fixture(wrapped_app)
        self.portal_setup(wrapped_app)

        transaction.commit()
        self.cleanup_portal_layer = cleanup

        # prepare a temporary directory for test files, save the old
        # tempfile.tempdir to restore when unloading the plugin
        self.old_tmp, tempfile.tempdir = tempfile.tempdir, tempfile.mkdtemp()

    def finalize(self, result):
        assert self.cleanup_test_layer is None
        self.cleanup_portal_layer()
        self.cleanup_portal_layer = None

        repository = os.path.join(INSTANCE_HOME, 'var', 'testing')
        if os.path.isdir(repository):
            shutil.rmtree(repository)

        # remove the temporary files created when testing, restore the old
        # tempfile.tempdir
        shutil.rmtree(tempfile.tempdir, True)
        tempfile.tempdir = self.old_tmp

    def prepareTestCase(self, testCase):
        assert self.cleanup_test_layer is None
        the_test = testCase.test

        if getattr(the_test, '_naaya_plugin', None) == self.__class__.__name__:
            the_test.mail_log, self.restore_mail = divert_mail()
            cleanup, test_db_layer = self.tzope.db_layer()

            self.db_connection = test_db_layer.open()
            app = self.db_connection.root()['Application']
            fake_root = wrap_with_request(app)
            wrapped_app = fake_root.app

            the_test.wsgi_request = self.tzope.wsgi_app
            the_test.app = wrapped_app
            the_test.portal = wrapped_app[self.portal_id]
            the_test.fake_request = fake_root.REQUEST
            populate_threading_local(the_test.portal, the_test.portal.REQUEST)
            the_test.portal.REQUEST['PARENTS'] = [the_test.portal, the_test.app]

            self.cleanup_test_layer = cleanup

            the_test._naaya_test_enabled = True

    def afterTest(self, test):
        if getattr(test.test, '_naaya_plugin', None) == self.__class__.__name__:
            self.restore_mail()
            del self.restore_mail
        if self.cleanup_test_layer is not None:
            import transaction
            transaction.abort()
            # TODO
            # self.db_connection.close()
            self.cleanup_test_layer()
            self.cleanup_test_layer = None
