from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import SpecialUser
from App.config import getConfiguration
from OFS.interfaces import ITraversable
from ZODB.interfaces import IDatabase
from Zope2.App import startup
from zc.async import subscribers
from zope import interface, component
from zope.app.appsetup.interfaces import DatabaseOpened
from zope.site.hooks import getSite, setSite
import Zope2
import logging
import os
import rwproperty
import threading
import types
import zc.async.dispatcher
import zc.async.job
import zc.monitor


logger = logging.getLogger('naaya.core.async')
tldata = threading.local()


class IInitAsync(interface.Interface):

    def init():
        """ init zc.async """


class IAsyncDatabase(interface.Interface):
    """ zc.async database """


class InitSingleDBInstance(object):

    interface.implements(IInitAsync)

    db_name = 'main'

    def init(self):
        component.provideUtility(Zope2.DB, IDatabase)

        configuration = getConfiguration()
        for name in configuration.dbtab.listDatabaseNames():
            db = configuration.dbtab.getDatabase(name=name)
            component.provideUtility(db, IDatabase, name=name)

        db = configuration.dbtab.getDatabase(name=self.db_name)
        component.provideUtility(db, IAsyncDatabase)

        ev = DatabaseOpened(db)
        subscribers.queue_installer(ev)
        subscribers.threaded_dispatcher_installer.poll_interval = 5
        subscribers.threaded_dispatcher_installer(ev)

        config = configuration.product_config.get('zc.z3monitor')
        if config and 'port' in config:
            logger.info('Starting zc.monitor service on port %s',
                        config['port'])
            zc.monitor.start(int(config['port']))


def init_zasync():
    noSecurityManager()

    initializer = component.queryUtility(IInitAsync)
    if initializer is not None:
        initializer.init()

    startup.noSecurityManager = noSecurityManager


# TODO: Subscribe to IProcessStarting instead (Zope >= 2.11)
startup.noSecurityManager = init_zasync


def shutdownDispatcher():
    dispatcher = zc.async.dispatcher.get()
    if dispatcher is not None:
        dispatcher.reactor.callFromThread(dispatcher.reactor.stop)
        dispatcher.thread.join(3)


if os.name == 'nt':
    try:
        from Signals.WinSignalHandler import SignalHandler
    except ImportError:
        SignalHandler = None
else:
    from Signals.SignalHandler import SignalHandler

if SignalHandler is not None:
    from signal import SIGTERM, SIGINT
    SignalHandler.registerHandler(SIGINT, shutdownDispatcher)
    SignalHandler.registerHandler(SIGTERM, shutdownDispatcher)


class Job(zc.async.job.Job):
    # A job to be run in a Zope 2 context.
    # Stores the current site and user when the job is created,
    # and sets them back up while the job is run.

    portal_path = None
    uf_path = None
    user_id = None

    _callable_path = None

    @property
    def callable(self):
        if self._callable_path is not None:
            path = self._callable_path
            callable_root = tldata.app.unrestrictedTraverse(path)
            return getattr(callable_root, self._callable_name)
        return super(Job, self).callable
    @rwproperty.setproperty
    def callable(self, value):
        if isinstance(value, types.MethodType) and ITraversable.providedBy(value.im_self):
            self._callable_path = value.im_self.getPhysicalPath()
            self._callable_name = value.__name__
        else:
            zc.async.job.Job.callable.fset(self, value)

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)

        site = kwargs['site']
        self.portal_path = site.getPhysicalPath()

        user = getSecurityManager().getUser()
        if isinstance(user, SpecialUser):
            self.uf_path, user_id = (), None
        else:
            self.uf_path = user.aq_parent.getPhysicalPath()
            self.user_id = user.getId()

    def setUp(self):
        db_name = Zope2.bobo_application._stuff[0].database_name
        tldata.app = app = Zope2.app(self._p_jar.get_connection(db_name))

        portal = app.unrestrictedTraverse(self.portal_path, None)
        old_site = getSite()
        setSite(portal)

        if self.uf_path:
            acl_users = app.unrestrictedTraverse(self.uf_path, None)
            user = acl_users.getUserById(self.user_id)
            user = user.__of__(acl_users)
            newSecurityManager(None, user)

        return old_site

    def tearDown(self, setup_info):
        del tldata.app
        noSecurityManager()
        setSite(setup_info)

