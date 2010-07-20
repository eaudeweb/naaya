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

"""
This module contains global constants.
"""

#Python imports

#Zope imports
import Globals

#Product imports

NAAYAFORUM_PRODUCT_NAME = 'NaayaForum'
NAAYAFORUM_PRODUCT_PATH = Globals.package_home(globals())

PERMISSION_ADD_FORUM = 'Add Naaya Forum'
PERMISSION_MODIFY_FORUMTOPIC = 'Add/Edit/Delete Naaya Forum Topic'
PERMISSION_ADD_FORUMMESSAGE = 'Add Naaya Forum Message'
PERMISSION_MODIFY_FORUMMESSAGE = 'Edit/Delete Forum Message'

METATYPE_NYFORUM = 'Naaya Forum'
METATYPE_NYFORUMTOPIC = 'Naaya Forum Topic'
METATYPE_NYFORUMMESSAGE = 'Naaya Forum Message'

LABEL_NYFORUM = 'Forum'
LABEL_NYFORUMTOPIC = 'Topic'
LABEL_NYFORUMMESSAGE = 'Message'

PREFIX_NYFORUM = 'frm'
PREFIX_NYFORUMTOPIC = 'tpc'
PREFIX_NYFORUMMESSAGE = 'msg'

DEFAULT_MAX_FILE_SIZE = 1048576 #1 Mega
