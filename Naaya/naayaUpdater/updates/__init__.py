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
import os
import glob
import logging

import zLOG
from Products.naayaUpdater.NaayaUpdater import UPDATERID
import Globals

# Config custom logger
LOG_ROOT = os.path.join(Globals.INSTANCE_HOME, 'log')
LOG_FILE = os.path.join(LOG_ROOT, 'updates.log')

logging.basicConfig()
_handler = logging.FileHandler(LOG_FILE)
_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
_handler.setFormatter(_formatter)

nyUpdateLogger = logging.getLogger('naayaUpdater')
nyUpdateLogger.setLevel(logging.DEBUG)
nyUpdateLogger.handlers = [_handler]
nyUpdateLogger.propagate = 0

def _get_available_updates():
    """ Return available updates in current dir."""
    name = __name__.split('.')
    curent_dir = Globals.package_home(globals())
    modules = [i.split('.')[0] for i in glob.glob1(curent_dir, "*.py")]
    updates = {}
    for mod in modules:
        try:
            update = __import__(mod, globals(), locals(), name)
        except:
            zLOG.LOG('NaayaUpdater', zLOG.WARNING,
                     "Could not import module %s" % mod)
            continue
        if not hasattr(update, 'register'):
            continue
        updates[mod] = update
    return updates

def registerUpdate(utool, uid, uhandler):
    """
    Register externals updates. uhandler should have a register method 
    that accepts uid as parameter.
    @param utool: updater tool
    @type utool: NaayaUpdater instance
    @param uid: update id
    @type uid: string
    @param uhandler: update handler to register
    @type uhandler: module or class
    """
    if uid in utool.objectIds():
        return
    try:
        update = uhandler.register(uid)
    except AttributeError:
        zLOG.LOG('NaayaUpdater', zLOG.WARNING, 
                 "Could not register updater %s" % uid)
    else:
        utool._setObject(uid, update)
        zLOG.LOG('NaayaUpdater', zLOG.INFO, 
                 "Register update %s" % uid)

def initialize(context):
    """ Register available updates """
    app = context._ProductContext__app
    utool = getattr(app, UPDATERID, None)
    if not utool:
        return
    updates = _get_available_updates()
    for name, update in updates.items():
        registerUpdate(utool, name, update)
