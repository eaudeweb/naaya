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

NAAYABASE_PRODUCT_NAME = 'NaayaBase'
NAAYABASE_PRODUCT_PATH = Globals.package_home(globals())

PERMISSION_ADMINISTRATE = 'Naaya - Access administrative area'
PERMISSION_PUBLISH_OBJECTS = 'Naaya - Publish content'
PERMISSION_EDIT_OBJECTS = 'Naaya - Edit content'
PERMISSION_COPY_OBJECTS = 'Naaya - Copy content'
PERMISSION_DELETE_OBJECTS = 'Naaya - Delete content'
PERMISSION_TRANSLATE_PAGES = 'Naaya - Translate pages'
PERMISSION_VALIDATE_OBJECTS = 'Naaya - Validate content'
PERMISSION_COMMENTS_ADD = 'Naaya - Add comments for content'
PERMISSION_COMMENTS_MANAGE = 'Naaya - Manage comments for content'
PERMISSION_PUBLISH_DIRECT = 'Naaya - Publish direct'
PERMISSION_SKIP_CAPTCHA = 'Naaya - Skip Captcha'
PERMISSION_BULK_DOWNLOAD = 'Naaya - Bulk download'

# Exceptions
EXCEPTION_NOTIMPLEMENTED = 'NotImplemented'
EXCEPTION_NOTACCESIBLE = 'NotAccesible'
EXCEPTION_NOTAUTHORIZED = 'Unauthorized'
EXCEPTION_NOTAUTHORIZED_MSG = 'You are not authorized to access this resource'
EXCEPTION_NOVERSION = 'NoVersionStarted'
EXCEPTION_NOVERSION_MSG = 'The object hasn\'t been locked out'
EXCEPTION_STARTEDVERSION = 'VersionStarted'
EXCEPTION_STARTEDVERSION_MSG = 'The object is locked out'
EXCEPTION_PARSINGFILE = 'Error parsing file %s: %s'

# Others
MESSAGE_SAVEDCHANGES = 'Saved changes. (%s)'
MESSAGE_NOTFROMEMAIL = 'The Sender email was not provided. Changes NOT saved (%s)'
ERROR_NOTHING_SELECTED = 'Nothing was selected.'
