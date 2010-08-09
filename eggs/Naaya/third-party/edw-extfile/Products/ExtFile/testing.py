
import os
import transaction

from Testing import ZopeTestCase

from Globals import package_home
from ZPublisher.HTTPRequest import FileUpload
from OFS.Image import Pdata

from zope.testing import cleanup
from Products.Five import zcml
from Testing.ZopeTestCase import utils

from zope import component

try:
    from zope.component.interfaces import IObjectEvent
except ImportError:
    from zope.app.event.interfaces import IObjectEvent

from Products.ExtFile import ExtFile
from Products.ExtFile import ExtImage
from Products.ExtFile import configuration

# Test data
here = os.path.join(package_home(globals()), 'tests')
gifImage = os.path.join(here, 'data', 'Folder_icon.gif')
jpegImage = os.path.join(here, 'data', 'Teneriffa_small.jpg')
tiffImage = os.path.join(here, 'data', 'Mountain_cmyk.tif')
notImage = os.path.join(here, 'data', 'Binary.foo')

# Permission sets
standard_perms = ZopeTestCase.standard_permissions
copymove_perms = ['View management screens', 'Add ExtImages', 'Add ExtFiles', 'Delete objects']
access_perms = ['View management screens']
change_perms = ['Change ExtFile/ExtImage']


# FileUpload factory
class DummyFieldStorage:
    def __init__(self, file, filename, headers):
        self.file = file
        self.filename = filename
        self.headers = headers

def makeFileUpload(file, content_type=None, filename=None):
    headers = {}
    if type(file) == type(''):
        file = open(file, 'rb')
    if content_type:
        headers['content-type'] = content_type
    fs = DummyFieldStorage(file, filename, headers)
    return FileUpload(fs)


# Pdata factory
def makePdata(file, size=1024):
    if type(file) == type(''):
        file = open(file, 'rb')
    chunk = file.read(size)
    pdata = p = Pdata(chunk)
    while chunk:
        chunk = file.read(size)
        if chunk:
            p.next = Pdata(chunk)
            p = p.next
    return pdata


# Adds helper objects to the ZODB
def setup_objects(app):
    factory = app.manage_addProduct['OFSP']
    factory.manage_addImage('GifImage', file=open(gifImage, 'rb'), content_type='image/gif')
    factory.manage_addImage('JpegImage', file=open(jpegImage, 'rb'), content_type='image/jpeg')
    factory.manage_addImage('TiffImage', file=open(tiffImage, 'rb'), content_type='image/tiff')
    factory.manage_addFile('NotImage', file=open(notImage, 'rb'))
    transaction.commit()


# Removes helper objects
def cleanup_objects(app):
    for id in ('GifImage', 'JpegImage', 'TiffImage', 'NotImage'):
        app._delObject(id)
    transaction.commit()


# Test layers
class ZCMLLayer:

    @classmethod
    def setUp(cls):
        cleanup.cleanUp()
        zcml._initialized = 0
        zcml.load_site()

    @classmethod
    def tearDown(cls):
        cleanup.cleanUp()
        zcml._initialized = 0

try:
    # Derive from ZopeLite layer if available
    from Testing.ZopeTestCase.layer import ZopeLite
    ZCMLLayer.__bases__ = (ZopeLite,)
except ImportError:
    pass


class ExtFileLayer(ZCMLLayer):

    @classmethod
    def setUp(cls):
        # Repository configuration
        ExtFile.REPOSITORY_PATH = ['reposit']
        ExtFile.REPOSITORY = configuration.FLAT
        ExtFile.NORMALIZE_CASE = configuration.KEEP
        ExtFile.ZODB_PATH = configuration.VIRTUAL
        ExtFile.COPY_OF_PROTECTION = configuration.ENABLED
        ExtFile.REPOSITORY_EXTENSIONS = configuration.MIMETYPE_REPLACE
        ExtFile.UNDO_POLICY = configuration.BACKUP_ON_DELETE
        utils.appcall(setup_objects)

    @classmethod
    def tearDown(cls):
        utils.appcall(cleanup_objects)


class HookLayer(ZCMLLayer):
    # Used by testCopySupportHooks

    @classmethod
    def setUp(cls):
        # Mark HookCounter as five:deprecatedManageAddDelete
        from Products.Five.eventconfigure import setDeprecatedManageAddDelete
        from Products.ExtFile.tests import testCopySupportHooks
        setDeprecatedManageAddDelete(testCopySupportHooks.TestItem)
        setDeprecatedManageAddDelete(testCopySupportHooks.TestFolder)

    @classmethod
    def tearDown(cls):
        pass


class EventLayer(ZCMLLayer):
    # Used by testCopySupportEvents

    @classmethod
    def setUp(cls):
        # Register event subscribers
        from Products.ExtFile.tests.testCopySupportEvents import ITestItem
        from Products.ExtFile.tests.testCopySupportEvents import ITestFolder
        from Products.ExtFile.tests.testCopySupportEvents import eventlog
        component.provideHandler(eventlog.trace, (ITestItem, IObjectEvent))
        component.provideHandler(eventlog.trace, (ITestFolder, IObjectEvent))

    @classmethod
    def tearDown(cls):
        from Products.ExtFile.tests.testCopySupportEvents import ITestItem
        from Products.ExtFile.tests.testCopySupportEvents import ITestFolder
        from Products.ExtFile.tests.testCopySupportEvents import eventlog
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(eventlog.trace, (ITestItem, IObjectEvent))
        gsm.unregisterHandler(eventlog.trace, (ITestFolder, IObjectEvent))


# Base classes
class LocalInstanceHome:

    local_home = here

    def afterSetUp(self):
        import App.config
        cfg = App.config.getConfiguration()
        self._ih = cfg.instancehome
        cfg.instancehome = self.local_home
        App.config.setConfiguration(cfg)

    def afterClear(self):
        import App.config
        cfg = App.config.getConfiguration()
        if hasattr(self, '_ih'):
            cfg.instancehome = self._ih
        App.config.setConfiguration(cfg)


class ExtFileTestCase(LocalInstanceHome, ZopeTestCase.ZopeTestCase):

    layer = ExtFileLayer

    def afterSetUp(self):
        LocalInstanceHome.afterSetUp(self)
        self._nuke_reposit = 1

    def afterClear(self):
        if getattr(self, '_nuke_reposit', 0):
            repository = os.path.join(INSTANCE_HOME, 'reposit')
            if os.path.isdir(repository):
                import shutil
                shutil.rmtree(repository, 1)
            del self._nuke_reposit
        LocalInstanceHome.afterClear(self)

    def _fsname(self, id):
        return os.path.join(INSTANCE_HOME, 'reposit', id)

    def _exists(self, id):
        return os.path.exists(self._fsname(id))

    def _listdir(self, *args):
        return os.listdir(os.path.join(INSTANCE_HOME, 'reposit', *args))

    def _fsize(self, id):
        return os.stat(id)[6]

    def addExtFile(self, id, file, content_type='', folder=None):
        if folder is None:
            folder = self.folder
        factory = folder.manage_addProduct['ExtFile'].manage_addExtFile
        id = factory(id=id, file=file, content_type=content_type)
        self.file = folder[id]
        return self.file

    def addExtImage(self, id, file, content_type='', folder=None, is_preview=False):
        if folder is None:
            folder = self.folder
        factory = folder.manage_addProduct['ExtFile'].manage_addExtImage
        if is_preview:
            id = factory(id=id, preview=file, content_type=content_type,
                         create_prev=configuration.UPLOAD_NORESIZE)
        else:
            id = factory(id=id, file=file, content_type=content_type)
        self.image = folder[id]
        return self.image

    def reposit(self, *args):
        dir = os.path.join(INSTANCE_HOME, 'reposit', *args)
        if os.path.exists(dir):
            return sorted(os.listdir(dir))
        return []

