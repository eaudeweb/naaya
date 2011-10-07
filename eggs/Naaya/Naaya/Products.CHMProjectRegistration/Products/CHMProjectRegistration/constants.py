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
PART_MANDATORY_FIELDS = [
                'title', 'requesting_organisations',
                'contact_name', 'contact_address', 'contact_telephone', 'contact_email',
                'start_date', 'end_date',
                'goal', 'subgoals', 'activities', 'results', 'locations', 'target_group',
                'communication_goals', 'interest', 'risks', 'reporting', 'added_value',
                ]
PART_EMAIL_RECIPIENTS = ['contact_email']
REG_MANDATORY_FIELDS = ['title', 'administrative_email', 'start_date', 'end_date']
REG_DATE_FIELDS = ['start_date', 'end_date']
REG_TIME_FIELDS = []

AUTH_MANDATORY_FIELDS = ['registration_id']

DATE_FIELDS = ['start_date', 'end_date']
TIME_FIELDS = []
NUMBER_FIELDS = ['requested_t1_hours', 'requested_t1_euro', 'requested_t2_hours', 'requested_t2_euro',
                'requested_t3_hours', 'requested_t3_euro', 'requested_material_costs',
                'requested_other_costs', 'own_t1_hours', 'own_t1_euro', 'own_t2_hours', 'own_t2_euro',
                'own_t3_hours', 'own_t3_euro', 'own_material_costs', 'own_other_costs']
PAIR_FIELDS = [
              ['requested_t1_hours', 'requested_t1_euro'],
              ['requested_t2_hours', 'requested_t2_euro'],
              ['requested_t3_hours', 'requested_t3_euro'],
              ['own_t1_hours', 'own_t1_euro'],
              ['own_t2_hours', 'own_t2_euro'],
              ['own_t3_hours', 'own_t3_euro'],
              ]
EMAIL_FIELDS = ['contact_email', 'financial_contact_email']

SMTP_HOST = 'localhost'
SMTP_PORT = '25'
NO_REPLY_MAIL = 'no-reply@biodiversiteit.nl'

VIEW_REGISTRATION = 'CHM Project Registration - View Registration'
MANAGE_REGISTRATION = 'CHM Project Registration - Manage Registration'

ADD_PROJECTS = 'CHM Project Registration - Add Project'
VIEW_PROJECTS = 'CHM Project Registration - View Projects'
EDIT_PROJECTS = 'CHM Project Registration - Edit Projects'

from os.path import dirname
PRODUCT_PATH = dirname(__file__)