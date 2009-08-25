from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem

PART_MANDATORY_FIELDS = ['last_name', 'country', 'phone_number', 'email', 'passport_no', 'passport_expire']
PRESS_MANDATORY_FIELDS = ['last_name', 'country', 'phone_number', 'email', 'passport_no', 'passport_expire']
DATE_FIELDS = ['passport_expire', 'arrival_date', 'departure_date']
TIME_FIELDS = ['arrival_time', 'departure_time']

class BaseParticipant(SimpleItem):
    """ Base class for participants """

    def __init__(self, registration_no, first_name, last_name, email, country, passport_no, \
                passport_expire, phone_number, fax_number, arrival_date, arrival_from, \
                arrival_flight, arrival_time, departure_date, departure_flight, departure_time, hotel_reservation, is_journalist):
        """ constructor """
        self.registration_no = registration_no
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
        self.hotel_reservation = hotel_reservation
        self.registration_date = DateTime()

    index_html = PageTemplateFile('zpt/participant/index', globals())

InitializeClass(BaseParticipant)

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
        BaseParticipant.__dict__['__init__'](self, registration_no, first_name, last_name, email, country, \
                        passport_no, passport_expire, phone_number, fax_number, arrival_date, arrival_from, \
                        arrival_flight, arrival_time, departure_date, departure_flight, departure_time, hotel_reservation, is_journalist=False)

InitializeClass(SemideParticipant)


class SemidePress(BaseParticipant):
    """ Press Participant class """

    meta_type = 'Semide Press Participant'
    product_name = 'SemideRegistration'
    icon = 'misc_/SemideRegistration/SemidePress.gif'

    security = ClassSecurityInfo()

    def __init__(self, registration_no, first_name, last_name, email, country, media_name, media_type, \
                media_description, media_position, passport_no, passport_expire, phone_number, mobile_number, \
               fax_number, arrival_date, arrival_from, arrival_flight, arrival_time, departure_date, departure_flight, departure_time, hotel_reservation):
        """ constructor """
        self.media_name = media_name
        self.media_type = media_type
        self.media_description = media_description
        self.media_position = media_position
        self.mobile_number = mobile_number
        BaseParticipant.__dict__['__init__'](self, registration_no, first_name, last_name, email, country, \
                        passport_no, passport_expire, phone_number, fax_number, arrival_date, arrival_from, \
                        arrival_flight, arrival_time, departure_date, departure_flight, departure_time, hotel_reservation, is_journalist=True)

InitializeClass(SemidePress)