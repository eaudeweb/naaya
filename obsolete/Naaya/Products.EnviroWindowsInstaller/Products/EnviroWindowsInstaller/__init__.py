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
#$Id: __init__.py 2582 2004-11-15 14:07:57Z finrocvs $

#Python imports

#Zope imports
from App.ImageFile import ImageFile

#Product imports
import EWInstaller

def initialize(context):
    """ initialize the EWInstaller object """

    #register classes
    context.registerClass(
        EWInstaller.EWInstaller,
        permission = 'Add EWInstaller object',
        constructors = (
                EWInstaller.addEWInstaller,
                ),
        icon = 'images/EWInstaller.gif'
        )

misc_ = {
    'EWInstaller.gif':ImageFile('images/EWInstaller.gif', globals()),
    'logo.gif':ImageFile('images/logo.gif', globals()),
}
