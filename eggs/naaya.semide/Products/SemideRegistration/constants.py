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

#constants
PART_MANDATORY_FIELDS = ['delegation_of', 'participant_type', 'last_name',
                        'work_address', 'country', 'email', 'fax_number', 'hotel',
                        'arrival_date', 'arrival_flight_number', 'arrival_flight_company',
                        'departure_date', 'departure_flight_number', 'departure_flight_company']
AUTH_MANDATORY_FIELDS = ['registration_no']

DATE_FIELDS = ['arrival_date', 'departure_date']
TIME_FIELDS = ['arrival_time', 'departure_time']

PARTICIPANT_TYPES = ['Head of delegation', 'Member of delegation', 'Observer', 'Press', 'Security']

SMTP_HOST = 'localhost'
SMTP_PORT = '25'
NO_REPLY_MAIL = 'no-reply@ufm-water.net'


VIEW_PERMISSION = 'View'
MANAGE_PERMISSION = 'Manage Semide Registration'

from os.path import dirname
PRODUCT_PATH = dirname(__file__)