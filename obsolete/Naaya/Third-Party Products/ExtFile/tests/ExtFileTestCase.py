
from Testing import ZopeTestCase

import os, sys, tempfile

from Products.ExtFile import transaction

# Repository configuration
from Products.ExtFile import ExtFile, Config
ExtFile.ExtFile._repository = ['reposit']
ExtFile.REPOSITORY = Config.FLAT
ExtFile.NORMALIZE_CASE = Config.KEEP
ExtFile.ZODB_PATH = Config.VIRTUAL
ExtFile.REPOSITORY_EXTENSIONS = Config.MIMETYPE_REPLACE
ExtFile.UNDO_POLICY = Config.BACKUP_ON_DELETE
            
# File names of test data
from Globals import package_home
here = package_home(globals())
gifImage = os.path.join(here, 'data', 'Folder_icon.gif')
jpegImage = os.path.join(here, 'data', 'Teneriffa_small.jpg')
tiffImage = os.path.join(here, 'data', 'Mountain_cmyk.tif')
notImage = os.path.join(here, 'data', 'Binary.foo')

# Define some permission sets
standard_perms = ZopeTestCase.standard_permissions
copymove_perms = ['View management screens', 'Add ExtImages', 'Add ExtFiles', 'Delete objects']
access_perms = ['View management screens']
change_perms = ['Change ExtFile/ExtImage']

# Put some Zope objects into the test ZODB
app = ZopeTestCase.app()
factory = app.manage_addProduct['OFSP']
factory.manage_addImage('GifImage', file=open(gifImage, 'rb'))
factory.manage_addImage('JpegImage', file=open(jpegImage, 'rb'), content_type='image/jpeg')
factory.manage_addImage('TiffImage', file=open(tiffImage, 'rb'), content_type='image/tiff')
factory.manage_addFile('NotImage', file=open(notImage, 'rb'))
transaction.commit()
ZopeTestCase.close(app)

# Use layer to set up ZCML
import layer


class LocalInstanceHome:
            
    local_home = here #tempfile.gettempdir()
            
    def afterSetUp(self):
        try:
            import App.config
        except ImportError:
            # Modify builtins
            b = getattr(__builtins__, '__dict__', __builtins__)
            self._ih = INSTANCE_HOME
            b['INSTANCE_HOME'] = self.local_home
        else:
            # Zope 2.7+
            cfg = App.config.getConfiguration()
            self._ih = cfg.instancehome
            cfg.instancehome = self.local_home
            App.config.setConfiguration(cfg)

    def afterClear(self):
        try:
            import App.config
        except ImportError:
            # Restore builtins
            b = getattr(__builtins__, '__dict__', __builtins__)
            if hasattr(self, '_ih'):
                b['INSTANCE_HOME'] = self._ih
        else:
            # Zope 2.7+
            cfg = App.config.getConfiguration()
            if hasattr(self, '_ih'):
                cfg.instancehome = self._ih
            App.config.setConfiguration(cfg)


class ExtFileTestCase(LocalInstanceHome, ZopeTestCase.ZopeTestCase):
        
    if layer.USELAYER:
        layer = layer.ZCML

    def afterSetUp(self):
        LocalInstanceHome.afterSetUp(self)
        self._nuke_reposit = 1

    def afterClear(self):
        if getattr(self, '_nuke_reposit', 0):
            # Remove repository
            repository = os.path.join(INSTANCE_HOME, 'reposit')
            if os.path.isdir(repository): 
                import shutil
                shutil.rmtree(repository, 1)
            del self._nuke_reposit
        LocalInstanceHome.afterClear(self)
        
    def _fsname(self, id):
        return os.path.join(INSTANCE_HOME, 'reposit', id)
        
    def _exists(self, id):
        return os.path.isfile(self._fsname(id))
        
    def _listdir(self):
        return os.listdir(os.path.join(INSTANCE_HOME, 'reposit'))
        
    def _fsize(self, id):
        return os.stat(id)[6]
        
    def addExtFile(self, id, file, content_type='', folder=None):
        # Add an ExtFile
        if folder is None:
            folder = self.folder
        id = folder.manage_addProduct['ExtFile'].manage_addExtFile(id=id, file=file, content_type=content_type)
        self.file = folder[id]
        return self.file
        
    def addExtImage(self, id, file, content_type='', folder=None):
        # Add an ExtImage
        if folder is None:
            folder = self.folder
        id = folder.manage_addProduct['ExtFile'].manage_addExtImage(id=id, file=file, content_type=content_type)
        self.image = folder[id]
        return self.image


# FileUpload factory
from ZPublisher.HTTPRequest import FileUpload

class DummyFieldStorage:
    '''Quacks like a FieldStorage'''

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

