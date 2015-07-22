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
import Globals

#Product imports

NAAYAPHOTOARCHIVE_PRODUCT_NAME = 'NaayaPhotoArchive'
NAAYAPHOTOARCHIVE_PRODUCT_PATH = Globals.package_home(globals())

PERMISSION_ADD_PHOTOGALLERY = 'Naaya - Add Naaya Photo Gallery'
PERMISSION_ADD_PHOTOFOLDER = 'Naaya - Add Naaya Photo Folder'
PERMISSION_ADD_PHOTO = 'Naaya - Add Naaya Photo'

METATYPE_NYPHOTOGALLERY = 'Naaya Photo Gallery'
METALABEL_NYPHOTOGALLERY = 'Photo Gallery'
METATYPE_NYPHOTOFOLDER = 'Naaya Photo Folder'
METALABEL_NYPHOTOFOLDER = 'Photo Folder'
METATYPE_NYPHOTO = 'Naaya Photo'

PREFIX_NYPHOTOGALLERY = 'pgl'
PREFIX_NYPHOTOFOLDER = 'pfl'
PREFIX_NYPHOTO = 'pht'

#others
NUMBER_OF_RESULTS_PER_PAGE = 50
NUMBER_OF_RESULTS_PER_LINE = 4
DEFAULT_QUALITY = 90
DEFAULT_DISPLAYS = {
    'Thumbnail': (100,100),
    'XSmall': (200,200),
    'Small': (320,320),
    'Medium': (480,480),
    'Large': (768,768),
    'XLarge': (1024,1024)
}

LISTING_DISPLAYS = {
    'Gallery': 200,
    'Album': 100,
}

ARCHIVE_PROPERTIES = (
    'title',
    'description',
    'coverage',
    'keywords',
    'sortorder',
    'releasedate',
    'discussion',
    'author',
    'source',
    'max_photos',
)
