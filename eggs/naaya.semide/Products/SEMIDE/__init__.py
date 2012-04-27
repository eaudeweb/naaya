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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
#Zope imports

import os
import Globals
from App.ImageFile import ImageFile

#Product imports
from constants import *
from Products.NaayaCore.constants import *
import SEMIDESite
from Tools import FlashTool

def initialize(context):
    """ """
    #register classes
    context.registerClass(
        SEMIDESite.SEMIDESite,
        permission = PERMISSION_ADD_SEMIDESITE,
        constructors = (
                SEMIDESite.manage_addSEMIDESite_html,
                SEMIDESite.manage_addSEMIDESite,
                ),
        icon = 'www/Site.gif'
        )

    context.registerClass(
        FlashTool.FlashTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                FlashTool.manage_addFlashTool,
                ),
        icon = 'www/FlashTool.gif'
        )

misc_ = {
    'print.gif':ImageFile('www/print.gif', globals()),
    'Site.gif':ImageFile('www/Site.gif', globals()),
    'FlashTool.gif':ImageFile('www/FlashTool.gif', globals()),
    'FlashTemplate.gif':ImageFile('www/FlashTemplate.gif', globals()),
    'FlashCategory.gif':ImageFile('www/FlashCategory.gif', globals()),
}

def semide_bundle_registration():
    """ Register things from skel into the CHM bundle """
    from Products.NaayaCore.FormsTool.bundlesupport import \
        register_templates_in_directory

    def forms_path(skel_name):
        return os.path.join(os.path.dirname(__file__), skel_name, 'forms')

    register_templates_in_directory(forms_path('skel'), 'SEMIDE')
