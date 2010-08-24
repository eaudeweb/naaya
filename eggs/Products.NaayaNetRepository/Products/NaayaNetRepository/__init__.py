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
import NyNetRepository

def initialize(context):
    """ """

    context.registerClass(
        NyNetRepository.NyNetRepository,
        permission = PERMISSION_ADD_NETREPOSITORY,
        constructors = (
                NyNetRepository.manage_addNyNetRepository_html,
                NyNetRepository.manage_addNyNetRepository,
                ),
        icon = 'www/NyNetRepository.gif'
        )

misc_ = {
    'NyNetRepository.gif':ImageFile('www/NyNetRepository.gif', globals()),
    'NyNetSite.gif':ImageFile('www/NyNetSite.gif', globals()),
    'NyNetChannel.gif':ImageFile('www/NyNetChannel.gif', globals()),
}
