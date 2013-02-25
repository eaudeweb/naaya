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
from App.ImageFile import ImageFile

#Product imports
from constants import *
from permissions import (PERMISSION_ADD_PHOTOGALLERY,
                         PERMISSION_ADD_PHOTOFOLDER,
                         PERMISSION_ADD_PHOTO)
import NyPhotoGallery
import NyPhotoFolder
import NyPhoto

from Products.Naaya import register_content
from Products.NaayaCore.SchemaTool.SchemaTool import register_schema_product

# Register as a folder content type
register_content(
    module=NyPhotoGallery,
    klass=NyPhotoGallery.NyPhotoGallery,
    module_methods={'addNyPhotoGallery': PERMISSION_ADD_PHOTOGALLERY,
        'gallery_add_html': PERMISSION_ADD_PHOTOGALLERY},
    klass_methods={},
    add_method=('gallery_add_html', PERMISSION_ADD_PHOTOGALLERY),
)

register_content(
    module=NyPhotoFolder,
    klass=NyPhotoFolder.NyPhotoFolder,
    module_methods={'addNyPhotoFolder': PERMISSION_ADD_PHOTOFOLDER,
       'photofolder_add_html': PERMISSION_ADD_PHOTOFOLDER},
    klass_methods={},
    add_method=('photofolder_add_html', PERMISSION_ADD_PHOTOFOLDER),
)

register_schema_product(name='NyPhotoGallery', label='Photo Gallery',
    meta_type=NyPhotoGallery.METATYPE_NYPHOTOGALLERY,
    default_schema=NyPhotoGallery.DEFAULT_SCHEMA)
register_schema_product(name='NyPhoto', label='Photo',
    meta_type=NyPhoto.METATYPE_NYPHOTO,
    default_schema=NyPhoto.DEFAULT_SCHEMA)

register_schema_product(name='NyPhotoFolder', label='Photo Folder',
    meta_type=NyPhotoFolder.METATYPE_NYPHOTOFOLDER,
    default_schema=NyPhotoFolder.DEFAULT_SCHEMA)

def initialize(context):
    """ """

    context.registerClass(
        NyPhotoGallery.NyPhotoGallery,
        permission = PERMISSION_ADD_PHOTOGALLERY,
        constructors = (
                NyPhotoGallery.gallery_add_html,
                NyPhotoGallery.addNyPhotoGallery,
                ),
        icon = 'www/NyPhotoGallery.gif'
        )

    context.registerClass(
        NyPhotoFolder.NyPhotoFolder,
        permission = PERMISSION_ADD_PHOTOFOLDER,
        constructors = (
                NyPhotoFolder.photofolder_add_html,
                NyPhotoFolder.addNyPhotoFolder,
                ),
        icon = 'www/NyPhotoFolder.gif'
        )

    register_permissions()

def register_permissions():
    from Products.Naaya.permissions import register_naaya_permission
    register_naaya_permission(PERMISSION_ADD_PHOTO,
                              'Submit Photo objects')

