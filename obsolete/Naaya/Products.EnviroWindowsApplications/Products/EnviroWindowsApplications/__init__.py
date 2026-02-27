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
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania
#
#
#$Id: __init__.py 2144 2004-09-10 16:30:43Z finrocvs $

#Python imports

#Zope imports
from App.ImageFile import ImageFile

#Product imports
import EWApplications

def initialize(context):
    """ initialize the EWApplications component """

    #register classes
    context.registerClass(
        EWApplications.EWApplications,
        permission = 'Add EWApplications object',
        constructors = (
                EWApplications.manage_addEWApplications_html,
                EWApplications.addEWApplications,
                ),
        icon = 'images/applications.gif'
        )

misc_ = {
    'application.gif':ImageFile('images/application.gif', globals()),
    'icon_accepted.gif':ImageFile('images/icon_accepted.gif', globals()),
    'icon_rejected.gif':ImageFile('images/icon_rejected.gif', globals()),
    'icon_pending.gif':ImageFile('images/icon_pending.gif', globals()),
    'eionet_screenshots.gif':ImageFile('images/eionet_screenshots.gif', globals()),
    'metal_screenshots.gif':ImageFile('images/metal_screenshots.gif', globals()),
    'autumn_screenshots.gif':ImageFile('images/autumn_screenshots.gif', globals()),
    "sort_asc": ImageFile("images/sort_asc.gif", globals()),
    "sort_desc": ImageFile("images/sort_desc.gif", globals()),
    "minus.gif": ImageFile("images/minus.gif", globals()),
    "plus.gif": ImageFile("images/plus.gif", globals()),
    "square.gif": ImageFile("images/square.gif", globals()),
}
