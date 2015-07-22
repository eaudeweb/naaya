# check for converter modules

from Products.TextIndexNG2.Registry import StorageRegistry

import StandardStorage
import StupidStorage

StorageRegistry.register('StandardStorage', StandardStorage.Storage)
StorageRegistry.register('StupidStorage', StupidStorage.Storage)
