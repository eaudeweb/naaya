import logging
import transaction
from App.ImageFile import ImageFile
from Zope2 import app

import NaayaUpdater

UpdaterID = NaayaUpdater.UPDATERID
logger = logging.getLogger('naayaUpdater')


def initialize(context):
    """ """
    # add Naaya Updater
    global updater
    application = app()

    if hasattr(application, UpdaterID):
        updater = getattr(application, UpdaterID)
    else:
        try:
            updater = NaayaUpdater.NaayaUpdater(id=UpdaterID)
            application._setObject(UpdaterID, updater)
            logger.info('Added Naaya Updater')
            transaction.commit()
        except:
            pass
        updater = getattr(application, UpdaterID)
    assert updater is not None


misc_ = {
    "updater.jpg":  ImageFile("www/updater.jpg", globals()),
    "updater.css":  ImageFile("www/updater.css", globals()),
    "updater.js":  ImageFile("www/updater.js", globals()),
}
