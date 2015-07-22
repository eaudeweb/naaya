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

NAAYAEUROPE_PRODUCT_NAME = 'NaayaEurope'
NAAYAEUROPE_PRODUCT_PATH = Globals.package_home(globals())

PERMISSION_ADD_EUROPE = 'Add Naaya Europe'

METATYPE_NYEUROPE = 'Naaya Europe'

ID_NYEUROPE = 'portal_europe'
TITLE_NYEUROPE = 'The Regional CHM Network in Europe'

ID_REFLIST = 'europe'
TITLE_REFLIST = 'Europe countries'

DEFAULT_COUNTRY_STATE = 0
COUNTRY_STATE = {
    0: 'No state',
    1: 'CHM European network',
    3: 'Countries using the CHM portal toolkit'
}
