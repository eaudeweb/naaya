from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem

from utilities.validators import form_validation
import constants

class BaseParticipant(SimpleItem):
    """ Base class for participants """

    def __init__(self, registration_no, first_name, last_name, email, country, passport_no, \
                passport_expire, phone_number, fax_number, arrival_date, arrival_from, \
                arrival_flight, arrival_time, departure_date, departure_flight, departure_time, is_journalist):
        """ constructor """
        self.id = registration_no
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.country = country
        self.passport_no = passport_no
        self.passport_expire = passport_expire
        self.phone_number = phone_number
        self.fax_number = fax_number
        self.arrival_date = arrival_date
        self.arrival_from = arrival_from
        self.arrival_flight = arrival_flight
        self.arrival_time = arrival_time
        self.departure_date = departure_date
        self.departure_flight = departure_flight
        self.departure_time = departure_time
        self.is_journalist = is_journalist
        self.registration_date = DateTime()

    def edit(self, first_name, last_name, email, country, passport_no, passport_expire, phone_number, \
                    fax_number, arrival_date, arrival_from, arrival_flight, arrival_time, departure_date, \
                    departure_flight, departure_time, hotel_reservation):
        """ edit properties """
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.country = country
        self.passport_no = passport_no
        self.passport_expire = passport_expire
        self.phone_number = phone_number
        self.fax_number = fax_number
        self.arrival_date = arrival_date
        self.arrival_from = arrival_from
        self.arrival_flight = arrival_flight
        self.arrival_time = arrival_time
        self.departure_date = departure_date
        self.departure_flight = departure_flight
        self.departure_time = departure_time
        self.hotel_reservation = hotel_reservation
        self_p_changed = 1

    def isEntitled(self, REQUEST):
        """ check if current user has the right to modify this object """
        return (REQUEST.SESSION.get('authentication_id','') == str(self.id)) and \
            (REQUEST.SESSION.get('authentication_name','') == str(self.last_name))

    #@todo: security
    _index_html = PageTemplateFile('zpt/participant/index', globals())
    #@todo: security
    def index_html(self, REQUEST=None):
        """ edit base participant properties """
        session = REQUEST.SESSION
        submit =  REQUEST.form.get('submit', '')
        if REQUEST.form.has_key('authenticate'):
            #if the user has submitted a valid registration number, this is saved on the session
            REQUEST.SESSION.set('authentication_id', REQUEST.get('registration_no'))
            REQUEST.SESSION.set('authentication_name', REQUEST.get('last_name'))
        return self._index_html(REQUEST)

    #@todo: security
    _edit_html = PageTemplateFile('zpt/participant/edit', globals())
    #@todo: security
    def edit_html(self, mandatory_fields, REQUEST=None):
        """ edit base participant properties """
        session = REQUEST.SESSION
        submit =  REQUEST.form.get('submit', '')
        if REQUEST.form.has_key('authenticate'):
            #if the user has submitted a valid registration number, this is saved on the session
            if form_validation(mandatory_fields=constants.AUTH_MANDATORY_FIELDS, 
                                date_fields=constants.DATE_FIELDS,
                                time_fields=constants.TIME_FIELDS,
                                REQUEST=REQUEST):
                REQUEST.SESSION.set('authentication_id', REQUEST.get('registration_no'))
                REQUEST.SESSION.set('authentication_name', REQUEST.get('last_name'))
        if submit:
            if form_validation(mandatory_fields=mandatory_fields, 
                                date_fields=constants.DATE_FIELDS,
                                time_fields=constants.TIME_FIELDS,
                                REQUEST=REQUEST):
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                self.edit(**cleaned_data)
                return REQUEST.RESPONSE.redirect(self.absolute_url())
        return self._edit_html(REQUEST)

InitializeClass(BaseParticipant)