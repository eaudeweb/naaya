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
from ImageFile import ImageFile

#Product imports
from constants import *
import NyPhotoFolder

def initialize(context):
    """ """

    context.registerClass(
        NyPhotoFolder.NyPhotoFolder,
        permission = PERMISSION_ADD_PHOTOFOLDER,
        constructors = (
                NyPhotoFolder.manage_addNyPhotoFolder_html,
                NyPhotoFolder.manage_addNyPhotoFolder,
                ),
        icon = 'www/NyPhotoFolder.gif'
        )

misc_ = {
    'NyPhotoFolder.gif':ImageFile('www/NyPhotoFolder.gif', globals()),
    'NyPhoto.gif':ImageFile('www/NyPhoto.gif', globals()),
    'NyPhoto_marked.gif':ImageFile('www/NyPhoto_marked.gif', globals()),
}
