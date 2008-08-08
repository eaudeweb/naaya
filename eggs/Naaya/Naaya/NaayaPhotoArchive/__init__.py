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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
try:
    from App.ImageFile import ImageFile
except ImportError, err:
    # Backward compatible
    from ImageFile import ImageFile

#Product imports
from constants import *
import NyPhotoGallery
import NyPhotoFolder

from Products.Naaya import register_content

# Register as a folder content type
register_content(
    module=NyPhotoGallery,
    klass=NyPhotoGallery.NyPhotoGallery,
    module_methods={'manage_addNyPhotoGallery': PERMISSION_ADD_PHOTOGALLERY},
    klass_methods={'gallery_add_html': PERMISSION_ADD_PHOTOGALLERY},
    add_method=('gallery_add_html', PERMISSION_ADD_PHOTOGALLERY),
)

register_content(
    module=NyPhotoFolder,
    klass=NyPhotoFolder.NyPhotoFolder,
    module_methods={'manage_addNyPhotoFolder': PERMISSION_ADD_PHOTOFOLDER},
    klass_methods={'photofolder_add_html': PERMISSION_ADD_PHOTOFOLDER},
    add_method=('photofolder_add_html', PERMISSION_ADD_PHOTOFOLDER),
)

def initialize(context):
    """ """

    context.registerClass(
        NyPhotoGallery.NyPhotoGallery,
        permission = PERMISSION_ADD_PHOTOGALLERY,
        constructors = (
                NyPhotoGallery.manage_addNyPhotoGallery,
                ),
        icon = 'www/NyPhotoGallery.gif'
        )
    
    context.registerClass(
        NyPhotoFolder.NyPhotoFolder,
        permission = PERMISSION_ADD_PHOTOFOLDER,
        constructors = (
                NyPhotoFolder.manage_addNyPhotoFolder,
                ),
        icon = 'www/NyPhotoFolder.gif'
        )

misc_ = {
    'NyPhotoGallery.gif':ImageFile('www/NyPhotoGallery.gif', globals()),
    'NyPhotoFolder.gif':ImageFile('www/NyPhotoFolder.gif', globals()),
    'NyPhoto.gif':ImageFile('www/NyPhoto.gif', globals()),
    'NyPhoto_marked.gif':ImageFile('www/NyPhoto_marked.gif', globals()),
    'right.gif':ImageFile('www/right.gif', globals()),
    'left.gif':ImageFile('www/left.gif', globals()),
    'album_background.gif': ImageFile('www/album_background.gif', globals()),
    'photo_background.png': ImageFile('www/photo_background.png', globals()),
    'photo_background_hover.png': ImageFile('www/photo_background_hover.png', globals()),
    'rotate_left.gif': ImageFile('www/rotate_left.gif', globals()),
    'rotate_right.gif': ImageFile('www/rotate_right.gif', globals()),
    'flip_vertically.gif': ImageFile('www/flip_vertically.gif', globals()),
    'flip_horizontally.gif': ImageFile('www/flip_horizontally.gif', globals()),
    'empty_album.png': ImageFile('www/empty_album.png', globals()),
}
