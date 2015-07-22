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
#$Id: constants.py 2542 2004-11-11 13:50:03Z finrocvs $

#Python imports
from os.path import join, dirname

#Zope imports

#Product imports
EWAPPLICATIONS_PRODUCT_NAME = 'EnviroWindowsApplications'
EWAPPLICATIONS_PRODUCT_PATH = dirname(__file__)
EWAPPLICATIONS_VAR_PATH = join(CLIENT_HOME, EWAPPLICATIONS_PRODUCT_NAME)

#Meta types
METATYPE_EWAPPLICATIONS = 'EWApplications'
METATYPE_EWAPPLICATION = 'EWApplication'

#Prefixes
PREFIX_EWAPPLICATIONS = 'apps'
PREFIX_EWAPPLICATION = 'app'

#Session key
APPLICATION_DATA = 'application_data'

#Others
APPLICATION_STATUS_PENDING = 'Pending'
APPLICATION_STATUS_APPROVED = 'Approved'
APPLICATION_STATUS_REJECTED = 'Rejected'
APPLICATION_STATUS_MESSAGE_REJECTED = 'portal not created'
APPLICATION_STATUS_MESSAGE_WORKING = 'portal not created, work in progress'
APPLICATION_STATUS_MESSAGE_FINISHED = 'portal successfully created'
APPLICATION_STATUS_MESSAGE_ABORTED = 'portal not created, installation aborted by end user'
APPLICATION_STATUS_MESSAGE_PENDING = 'the application has not been processed yet'
