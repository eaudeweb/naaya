from App.ImageFile import ImageFile
from OFS import Folder

import NaayaUpdater
from update_scripts import LOGS_FOLDERNAME

UpdaterID = NaayaUpdater.UPDATERID

from NaayaPatches import *

def initialize(context):
    """ """
    #add Naaya Updater
    global updater
    app = context._ProductContext__app

    if hasattr(app, UpdaterID):
        updater = getattr(app, UpdaterID)
    else:
        try:
            updater = NaayaUpdater.NaayaUpdater(id=UpdaterID)
            app._setObject(UpdaterID, updater)
            get_transaction().note('Added Naaya Updater')
            get_transaction().commit()
        except:
            pass
        updater = getattr(app, UpdaterID)
    assert updater is not None

    if not hasattr(app, LOGS_FOLDERNAME):
        Folder.manage_addFolder(app, LOGS_FOLDERNAME)

    updater.refresh_updates_dict()

misc_ = {
    "updater.jpg":  ImageFile("www/updater.jpg", globals()),
    "jquery-1.3.2.min.js": ImageFile("www/jquery-1.3.2.min.js", globals()),
}
