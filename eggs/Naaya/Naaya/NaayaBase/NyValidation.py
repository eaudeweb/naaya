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
# Copyright   European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Anton Cupcea, Finsiel Romania
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

#Product imports

class NyValidation:

    security = ClassSecurityInfo()

    def __init__(self):
        self.validation_status = 0
        self.validation_date = ''
        self.validation_by = ''
        self.validation_comment = ''
        self.contributor = ''
        self.approved_by = ''

    def checkThis(self, validation_status, validation_comment, validation_by, validation_date=None):
        if validation_date is None:
            validation_date = self.utGetTodayDate()
        elif validation_date == '' or validation_date =='2010/01/01':
            validation_date = ''
        else:
            validation_date = self.utGetDate(validation_date)
        self.validation_status = validation_status
        self.validation_date = validation_date
        self.validation_by = validation_by
        if validation_status == -1:
            self.validation_comment = validation_comment
        if validation_status in [0, 1] :
            self.validation_comment = ''
        self._p_changed = 1

InitializeClass(NyValidation)
