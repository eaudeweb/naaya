import logging
import transaction
from App.ImageFile import ImageFile

import NaayaUpdater

UpdaterID = NaayaUpdater.UPDATERID
logger = logging.getLogger('naayaUpdater')

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
            logger.info('Added Naaya Updater')
            transaction.commit()
        except:
            pass
        updater = getattr(app, UpdaterID)
    assert updater is not None

misc_ = {
    "updater.jpg":  ImageFile("www/updater.jpg", globals()),
    "updater.css":  ImageFile("www/updater.css", globals()),
    "updater.js":  ImageFile("www/updater.js", globals()),
}
