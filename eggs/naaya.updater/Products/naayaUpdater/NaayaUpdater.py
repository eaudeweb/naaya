""" `NaayaUpdater` is a tool that is used to run migrations for Naaya portals.

The updater contains `UpdateScript`'s that are registered as utilities and can
be run agains all sites or just the selected ones. After an update is performed
an log file is created that can be used for future reference. If an update
fails for some reason all reversible changes will be rolled back. Scripts can
be registered with

"""

from naaya.core.backport import namedtuple

from os.path import join, isfile
from datetime import datetime

from persistent.list import PersistentList
from zope.interface import implements
from zope.component import queryUtility

import Globals
from OFS.Folder import Folder

from interfaces import IUpdater, IUpdateScript
import utils

UPDATERID = 'naaya_updates'
UPDATERTITLE = 'Update scripts for Naaya'
NAAYAUPDATER_PRODUCT_PATH = Globals.package_home(globals())

LogEntry = namedtuple("LogEntry", ('update_id, datetime, user, portals'))

class NaayaUpdater(Folder):
    """ NaayaUpdater class """

    implements(IUpdater)

    meta_type = 'Naaya Updater'
    icon = 'misc_/naayaUpdater/updater.jpg'
    title = UPDATERTITLE

    #Should be changed to interface
    pmeta_types = ('Naaya Site',
                   'CHM Site',
                   'EnviroWindows Site',
                   'SEMIDE Site',
                   'SMAP Site', )

    def __init__(self, *args, **kw):
        """ Add logs container """

        super(NaayaUpdater, self).__init__(*args, **kw)
        self._logs = PersistentList()

    def manage_options(self):
        """ """
        return (
            {'label': 'Updates', 'action': '@@view.html'},
            {'label': 'Logs', 'action': '@@logs.html'},
            {'label':'Contents', 'action':'manage_main',
             'help':('OFSP','ObjectManager_Contents.stx')},
        )

    def __bobo_traverse__(self, REQUEST, key):
        """ Overriding zope's traversal in order to display only the registered
        update scripts

        """
        if hasattr(self, key):
            return getattr(self, key)

        util = queryUtility(IUpdateScript, name=key)
        if not util:
            raise AttributeError(key)

        script = util()
        script.id = key
        return script.__of__(self)

    def utils(self, utility):
        """ Convenience function for templates to get the required utility
        functions.

        """

        return getattr(utils, utility)

    def add_log(self, update_id, portals, user):
        """Given an `update_id` and a `portal_path` add log entry with the
        `datetime` of the event and other optional data.

        """
        if not hasattr(self, '_logs'):
            self._logs = PersistentList()
        log_entry = LogEntry(update_id=update_id,
                             datetime=datetime.now(),
                             portals=portals,
                             user=user)
        self._logs.append(log_entry)
        self._logs._p_changed = True
