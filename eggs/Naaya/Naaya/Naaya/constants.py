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

#Python imports
from os.path import join

#Zope imports
import Globals

#Product imports

NAAYA_PRODUCT_NAME = 'Naaya'
NAAYA_PRODUCT_PATH = Globals.package_home(globals())

PERMISSION_ADD_SITE = 'Naaya - Add Naaya Site objects'
PERMISSION_ADD_FOLDER = 'Naaya - Add Naaya Folder objects'

METATYPE_NYSITE = 'Naaya Site'
METATYPE_FOLDER = 'Naaya Folder'

LABEL_NYFOLDER = 'Folder'

DEFAULT_PORTAL_LANGUAGE_CODE = 'en' #English language is assumed to be the default language
DEFAULT_SORTORDER = 100
DEFAULT_NUMBERLATESTUPLOADS = 5
DEFAULT_NUMBERANNOUNCEMENTS = 5
DEFAULT_MAILSERVERNAME = 'localhost'
DEFAULT_MAILSERVERPORT = 25

PREFIX_SITE = 'portal'
PREFIX_FOLDER = 'fol'

ID_IMAGESFOLDER = 'images'

METATYPE_NYSYNDICATION = 'NYSyndication'
METATYPE_NYSYNDICATIONLOCALCHANNEL = 'NYLocalChannel'
METATYPE_NYSYNDICATIONREMOTECHANNEL = 'NYRemoteChannel'