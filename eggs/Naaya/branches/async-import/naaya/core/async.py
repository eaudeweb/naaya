from AccessControl.SecurityManagement import noSecurityManager
from App.config import getConfiguration
from ZODB.interfaces import IDatabase
from Zope2.App import startup
#from naaya.async.interfaces import IInitAsync, IAsyncDatabase
from zc.async import subscribers
from zope import interface, component
from zope.app.appsetup.interfaces import DatabaseOpened
import Zope2
import logging
import zc.async.dispatcher
import zc.monitor

logger = logging.getLogger('naaya.core.async')


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
        subscribers.threaded_dispatcher_installer.poll_interval = 2
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


import os
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

