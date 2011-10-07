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


class CHMParticipant(BaseParticipant):
    """ Participant class """

    meta_type = 'CHM Participant'
    product_name = 'CHMRegistration'
    icon = 'misc_/CHMRegistration/CHMParticipant.png'

    security = ClassSecurityInfo()

    def __init__(self, registration_no, first_last_name, position, organisation, address, zip_code,\
                email, phone_number, event_1, event_2, event_3, topic_1, topic_2, topic_3, topic_4, explanation, private_email=False):
        """ constructor """
        BaseParticipant.__dict__['__init__'](self, registration_no, first_last_name, position,\
                organisation, address, zip_code, email, phone_number, event_1, event_2, event_3,\
                topic_1, topic_2, topic_3, topic_4, explanation, private_email)

    def edit(self, first_last_name, position, organisation, address, zip_code,\
                email, phone_number, event_1, event_2, event_3, topic_1, topic_2, topic_3, topic_4, explanation, private_email=False):
        """ edit properties """
        BaseParticipant.__dict__['edit'](self, first_last_name, position, organisation, address,\
                zip_code, email, phone_number, event_1, event_2, event_3,\
                topic_1, topic_2, topic_3, topic_4, explanation, private_email)

    security.declareProtected(constants.VIEW_PERMISSION, 'edit_html')
    def edit_html(self, REQUEST=None):
        """ edit properties interface """
        return BaseParticipant.__dict__['edit_html'](self, constants.PART_MANDATORY_FIELDS, REQUEST)

InitializeClass(CHMParticipant)