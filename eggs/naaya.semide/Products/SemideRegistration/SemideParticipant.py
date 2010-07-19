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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from BaseParticipant import BaseParticipant

import constants


class SemideParticipant(BaseParticipant):
    """ Participant class """

    meta_type = 'Semide Participant'
    product_name = 'SemideRegistration'
    icon = 'misc_/SemideRegistration/SemideParticipant.png'

    security = ClassSecurityInfo()

    def __init__(self, registration_no, first_name, last_name, email, country, organisation, official_title, \
                passport_no, passport_expire, phone_number, fax_number, arrival_date, arrival_from, \
                arrival_flight, arrival_time, departure_date, departure_flight, departure_time, hotel_reservation):
        """ constructor """
        self.organisation = organisation
        self.official_title = official_title
        self.hotel_reservation = hotel_reservation
        BaseParticipant.__dict__['__init__'](self, registration_no, first_name, last_name, email, country, 
                        passport_no, passport_expire, phone_number, fax_number, arrival_date, arrival_from, 
                        arrival_flight, arrival_time, departure_date, departure_flight, departure_time, is_journalist=False)

    def edit(self, first_name, last_name, email, country, organisation, official_title, passport_no, passport_expire, phone_number, \
                    fax_number, arrival_date, arrival_from, arrival_flight, arrival_time, departure_date, departure_flight, departure_time, hotel_reservation):
        """ edit properties """
        self.organisation = organisation
        self.official_title = official_title
        self.hotel_reservation = hotel_reservation
        BaseParticipant.__dict__['edit'](self,first_name, last_name, email, country, passport_no, passport_expire, phone_number, fax_number, 
                                        arrival_date, arrival_from, arrival_flight, arrival_time, departure_date, departure_flight, departure_time)

    security.declareProtected(constants.VIEW_PERMISSION, 'edit_html')
    def edit_html(self, REQUEST=None):
        """ edit properties interface """
        return BaseParticipant.__dict__['edit_html'](self, constants.PART_MANDATORY_FIELDS, REQUEST)

InitializeClass(SemideParticipant)