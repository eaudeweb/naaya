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
PART_MANDATORY_FIELDS = ['last_name', 'country', 'phone_number', 'email', 'passport_no', 'passport_expire']
PRESS_MANDATORY_FIELDS = ['last_name', 'country', 'phone_number', 'email', 'passport_no', 'passport_expire']
AUTH_MANDATORY_FIELDS = ['registration_no']

DATE_FIELDS = ['passport_expire', 'arrival_date', 'departure_date']
TIME_FIELDS = ['arrival_time', 'departure_time']

SMTP_HOST = 'mail.eaudeweb.ro'
SMTP_PORT = '25'
NO_REPLY_MAIL = 'no-reply@ufm-water.net'


VIEW_PERMISSION = 'View'
MANAGE_PERMISSION = 'Manage Semide Registration'

from os.path import dirname
PRODUCT_PATH = dirname(__file__)