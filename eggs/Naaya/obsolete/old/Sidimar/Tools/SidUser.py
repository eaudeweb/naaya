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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania

import time

from Products.NaayaCore.AuthenticationTool.User import User
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class SidUser(User):
    """ """

    def __init__(self, name, password, roles, domains, firstname, lastname, job, organisation, country, 
                street, street_number, zip, city, region, phone, mail, note, download, privacy):
        self.job = job
        self.organisation = organisation
        self.country = country
        self.street = street
        self.street_number = street_number
        self.zip = zip
        self.city = city
        self.region = region
        self.phone = phone
        self.note = note
        self.download = download
        self.privacy = privacy
        self.logs = []
        self.downloads = []
        User.__dict__['__init__'](self, name, password, roles, domains, firstname, lastname, mail)



class FakeUser:
    """ """

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, id, firstname, lastname, job, organisation, country, street, street_number, zip, 
                city, region, phone, mail, note, download, privacy):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.job = job
        self.organisation = organisation
        self.country = country
        self.street = street
        self.street_number = street_number
        self.zip = zip
        self.city = city
        self.region = region
        self.phone = phone
        self.mail = mail
        self.note = note
        self.download = download
        self.privacy = privacy
        self.created = time.strftime('%d %b %Y %H:%M:%S')

InitializeClass(FakeUser)