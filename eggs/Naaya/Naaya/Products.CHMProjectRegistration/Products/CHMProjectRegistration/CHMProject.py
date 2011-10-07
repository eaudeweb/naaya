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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem
from datetime import datetime

from utilities import checkPermission
from utilities.validators import form_validation, str2date
import constants

class CHMProject(SimpleItem):
    """ Project class """

    meta_type = 'CHM Project'
    product_name = 'CHMProjectRegistration'
    icon = 'misc_/CHMProjectRegistration/CHMProject.png'

    security = ClassSecurityInfo()

    def __init__(self, id,
                title, requesting_organisations, other_partners, other_requests,
                contact_name, contact_address, contact_telephone, contact_fax, contact_email,
                start_date, end_date, important_dates,
                goal, subgoals, activities, results, locations, target_group,
                communication_goals, interest, risks, reporting, comments,
                requested_t1_hours, requested_t1_euro, requested_t2_hours, requested_t2_euro,
                requested_t3_hours, requested_t3_euro, requested_material_costs,
                requested_other_costs, own_t1_hours, own_t1_euro, own_t2_hours, own_t2_euro,
                own_t3_hours, own_t3_euro, own_material_costs, own_other_costs, added_value,
                financial_contact_name, financial_contact_address, financial_contact_telephone,
                financial_contact_fax, financial_contact_email,
                admin_comment=''):
        """ constructor """
        self.id = id
        self.title = title
        self.requesting_organisations = requesting_organisations
        self.other_partners = other_partners
        self.other_requests = other_requests
        self.contact_name = contact_name
        self.contact_address = contact_address
        self.contact_telephone = contact_telephone
        self.contact_fax = contact_fax
        self.contact_email = contact_email
        self.start_date = start_date
        self.end_date = end_date
        self.important_dates = important_dates
        self.goal = goal
        self.subgoals = subgoals
        self.activities = activities
        self.results = results
        self.locations = locations
        self.target_group = target_group
        self.communication_goals = communication_goals
        self.interest = interest
        self.risks = risks
        self.reporting = reporting
        self.comments = comments
        self.requested_t1_hours = requested_t1_hours
        self.requested_t1_euro = requested_t1_euro
        self.requested_t2_hours = requested_t2_hours
        self.requested_t2_euro = requested_t2_euro
        self.requested_t3_hours = requested_t3_hours
        self.requested_t3_euro = requested_t3_euro
        self.requested_material_costs = requested_material_costs
        self.requested_other_costs = requested_other_costs
        self.own_t1_hours = own_t1_hours
        self.own_t1_euro = own_t1_euro
        self.own_t2_hours = own_t2_hours
        self.own_t2_euro = own_t2_euro
        self.own_t3_hours = own_t3_hours
        self.own_t3_euro = own_t3_euro
        self.own_material_costs = own_material_costs
        self.own_other_costs = own_other_costs
        self.added_value = added_value
        self.financial_contact_name = financial_contact_name
        self.financial_contact_address = financial_contact_address
        self.financial_contact_telephone = financial_contact_telephone
        self.financial_contact_fax = financial_contact_fax
        self.financial_contact_email = financial_contact_email
        self.admin_comment = admin_comment
        self.registration_date = datetime.now()

    security.declareProtected(constants.EDIT_PROJECTS, 'edit')
    def edit(self, title, requesting_organisations, other_partners, other_requests,
            contact_name, contact_address, contact_telephone, contact_fax, contact_email,
            start_date, end_date, important_dates,
            goal, subgoals, activities, results, locations, target_group,
            communication_goals, interest, risks, reporting, comments,
            requested_t1_hours, requested_t1_euro, requested_t2_hours, requested_t2_euro,
            requested_t3_hours, requested_t3_euro, requested_material_costs,
            requested_other_costs, own_t1_hours, own_t1_euro, own_t2_hours, own_t2_euro,
            own_t3_hours, own_t3_euro, own_material_costs, own_other_costs, added_value,
            financial_contact_name, financial_contact_address, financial_contact_telephone,
            financial_contact_fax, financial_contact_email,
            admin_comment=''):
        """ edit properties """
        self.title = title
        self.requesting_organisations = requesting_organisations
        self.other_partners = other_partners
        self.other_requests = other_requests
        self.contact_name = contact_name
        self.contact_address = contact_address
        self.contact_telephone = contact_telephone
        self.contact_fax = contact_fax
        self.contact_email = contact_email
        self.start_date = start_date
        self.end_date = end_date
        self.important_dates = important_dates
        self.goal = goal
        self.subgoals = subgoals
        self.activities = activities
        self.results = results
        self.locations = locations
        self.target_group = target_group
        self.communication_goals = communication_goals
        self.interest = interest
        self.risks = risks
        self.reporting = reporting
        self.comments = comments
        self.requested_t1_hours = requested_t1_hours
        self.requested_t1_euro = requested_t1_euro
        self.requested_t2_hours = requested_t2_hours
        self.requested_t2_euro = requested_t2_euro
        self.requested_t3_hours = requested_t3_hours
        self.requested_t3_euro = requested_t3_euro
        self.requested_material_costs = requested_material_costs
        self.requested_other_costs = requested_other_costs
        self.own_t1_hours = own_t1_hours
        self.own_t1_euro = own_t1_euro
        self.own_t2_hours = own_t2_hours
        self.own_t2_euro = own_t2_euro
        self.own_t3_hours = own_t3_hours
        self.own_t3_euro = own_t3_euro
        self.own_material_costs = own_material_costs
        self.own_other_costs = own_other_costs
        self.added_value = added_value
        self.financial_contact_name = financial_contact_name
        self.financial_contact_address = financial_contact_address
        self.financial_contact_telephone = financial_contact_telephone
        self.financial_contact_fax = financial_contact_fax
        self.financial_contact_email = financial_contact_email
        self.admin_comment = admin_comment

    def getCountry(self, lang):
        """ get country name """
        language, query, results = self.glossary_coverage.searchGlossary(query=self.country, size=1)
        if results:
            return results[0].get_translation_by_language(lang)
        return ''

    def has_credentials(self, REQUEST):
        """ check if current user has the right credentials """
        return ((REQUEST.SESSION.get('authentication_id','') == str(self.id)) and \
            (REQUEST.SESSION.get('authentication_name','') == self.unicode2UTF8(self.contact_name)))

    security.declarePublic('canViewProject')
    def canViewProject(self, REQUEST):
        """ Check the permissions to view this project """
        return self.canViewProjects() or\
            self.canManageProjects() or\
            self.has_credentials(REQUEST)

    security.declarePublic('canEditProject')
    def canEditProject(self, REQUEST):
        """ Check the permissions to edit this project """
        return self.canEditProjects() or\
            self.canManageProjects() or\
            self.has_credentials(REQUEST)

    _index_html = PageTemplateFile('zpt/project/index', globals())
    #@todo: security
    security.declareProtected(constants.VIEW_REGISTRATION, 'index_html')
    def index_html(self, REQUEST=None):
        """ edit project properties """
        session = REQUEST.SESSION
        submit =  REQUEST.form.get('submit', '')
        lang = self.gl_get_selected_language()
        if REQUEST.form.has_key('authenticate'):
            #The registration number and last name are saved on the session as submitted by the user
            session.set('authentication_id', REQUEST.get('registration_id'))
            session.set('authentication_name', self.unicode2UTF8(REQUEST.get('authentication_name')))
        if REQUEST.form.has_key('resend_mail'):
            #If the email corresponds with the one used at the registration, the confirmation mail will be resent
            email_recipients = [getattr(self, field) for field in constants.PART_EMAIL_RECIPIENTS]
            user_email = REQUEST.form.get('email', '')
            if user_email in email_recipients:
                values = {'registration_edit_link': self.absolute_url(),
                            'registration_event': self.unicode2UTF8(self.aq_parent.title),
                            'website_team': self.unicode2UTF8(self.site_title),
                            'registration_id': self.id,
                            'name': self.unicode2UTF8(self.contact_name)}
                self.send_registration_notification(user_email,
                    'Project registration',
                    self.getEmailTemplate('user_registration_html', lang) % values,
                    self.getEmailTemplate('user_registration_text', lang) % values)
                REQUEST.set('email_sent', True)
            else:
                REQUEST.set('wrong_email', True)
        return self._index_html(REQUEST)

    _edit_html = PageTemplateFile('zpt/project/edit', globals())

    security.declareProtected(constants.VIEW_REGISTRATION, 'edit_html')
    def edit_html(self, REQUEST=None):
        """ edit project properties """
        session = REQUEST.SESSION
        submit =  REQUEST.form.get('submit', '')
        lang = self.gl_get_selected_language()
        if REQUEST.form.has_key('authenticate'):
            #The registration number and last name are saved on the session as submitted by the user
            if form_validation(mandatory_fields=constants.AUTH_MANDATORY_FIELDS,
                                REQUEST=REQUEST):
                session.set('authentication_id', REQUEST.get('registration_id'))
                session.set('authentication_name', self.unicode2UTF8(REQUEST.get('authentication_name')))
        if REQUEST.form.has_key('resend_mail'):
            #If the email corresponds with the one used at the registration, the confirmation mail will be resent
            email_recipients = [getattr(self, field) for field in constants.PART_EMAIL_RECIPIENTS]
            user_email = REQUEST.form.get('email', '')
            if user_email in email_recipients:
                values = {'registration_edit_link': self.absolute_url(),
                            'registration_event': self.unicode2UTF8(self.aq_parent.title),
                            'website_team': self.unicode2UTF8(self.site_title),
                            'registration_id': self.id,
                            'name': self.unicode2UTF8(self.contact_name)}
                self.send_registration_notification(user_email,
                    'Project registration',
                    self.getEmailTemplate('user_registration_html', lang) % values,
                    self.getEmailTemplate('user_registration_text', lang) % values)
                REQUEST.set('email_sent', True)
            else:
                REQUEST.set('wrong_email', True)
        if submit:
            if form_validation(mandatory_fields=constants.PART_MANDATORY_FIELDS, 
                                date_fields=constants.DATE_FIELDS,
                                time_fields=constants.TIME_FIELDS,
                                number_fields=constants.NUMBER_FIELDS,
                                pair_fields=constants.PAIR_FIELDS,
                                email_fields=constants.EMAIL_FIELDS,
                                REQUEST=REQUEST):
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                del cleaned_data['total_requested']
                del cleaned_data['total_own']
                self.edit(**cleaned_data)

                #send notifications
                values = {'registration_edit_link': self.absolute_url(),
                            'registration_event': self.aq_parent.title,
                            'website_team': self.site_title,
                            'registration_id': self.id}
                self.send_registration_notification(self.administrative_email,
                    'Project registration',
                    self.getEmailTemplate('admin_registration_html', 'en') % values,
                    self.getEmailTemplate('admin_registration_text', 'en') % values)

                return REQUEST.RESPONSE.redirect(self.absolute_url())
        return self._edit_html(REQUEST)

    def format_view(self, message=''):
        return message.replace('&','&amp;').replace('<', '&lt').replace('>','&gt').replace('\r\n','<br/>')

InitializeClass(CHMProject)