import re
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder

from Products.NaayaCore.managers import utils as naaya_utils
from SemideParticipant import SemideParticipant
from SemidePress import SemidePress
from utilities.Slugify import slugify
from utilities.validators import form_validation, registration_validation
import constants

add_registration = PageTemplateFile('zpt/registration/add', globals())
def manage_add_registration(self, id='', title='', administrative_email ='', start_date='', end_date='', introduction='', REQUEST=None):
    """ Adds a Semide registration instance"""
    if registration_validation(REQUEST):
        if not id:
            id = slugify(title)
        ob = SemideRegistration(id, title, administrative_email, start_date, end_date, introduction)
        self._setObject(id, ob)
        ob = self._getOb(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return add_registration.__of__(self)(REQUEST)


class SemideRegistration(Folder):
    """ Main class of the meeting registration"""

    meta_type = 'Semide Registration'
    product_name = 'SemideRegistration'

    security = ClassSecurityInfo()

    def __init__(self, id, title, administrative_email, start_date, end_date, introduction):
        """ constructor """
        self.id = id
        self.title = title
        self.administrative_email = administrative_email
        self.start_date = start_date
        self.end_date = end_date
        self.introduction = introduction

    _registration_html = PageTemplateFile('zpt/registration/registration', globals())
    def registration_html(self, REQUEST):
        """ registration form """
        submit =  REQUEST.form.get('submit', '')
        if submit:
            form_valid = form_validation(constants.PART_MANDATORY_FIELDS,
                                            constants.DATE_FIELDS,
                                            constants.TIME_FIELDS,
                                            REQUEST)
            if form_valid:
                registration_no = naaya_utils.genRandomId(10)
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                ob = SemideParticipant(registration_no, **cleaned_data)
                self._setObject(registration_no, ob)
                import pdb; pdb.set_trace()
                participant = self._getOb(registration_no, None)
                if participant:
                    return REQUEST.RESPONSE.redirect(participant.absolute_url())
        return self._registration_html(REQUEST)

    _registration_press_html = PageTemplateFile('zpt/registration/registration_press', globals())
    def registration_press_html(self, REQUEST):
        """ registration form """
        submit =  REQUEST.form.get('submit', '')
        if submit:
            form_valid = form_validation(constants.PRESS_MANDATORY_FIELDS,
                                            constants.DATE_FIELDS,
                                            constants.TIME_FIELDS,
                                            REQUEST)
            if form_valid:
                registration_no = naaya_utils.genRandomId(10)
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                ob = SemidePress(registration_no, **cleaned_data)
                self._setObject(registration_no, ob)
                press = self._getOb(registration_no, None)
                if press:
                    return REQUEST.RESPONSE.redirect(press.absolute_url())
        return self._registration_press_html(REQUEST)

    def formatDate(self, sdate):
        return sdate.strftime('%d %b %Y')

    #@todo: security
    participants = PageTemplateFile('zpt/registration/participants', globals())
    #@todo: security
    def getParticipants(self, skey, rkey):
        """ Returns the list of participants """
        participants = [ (getattr(p, skey), p) for p in self.objectValues('Semide Participant') if p.is_journalist is False ]
        participants.sort()
        if rkey:
            participants.reverse()
        return [p for (key, p) in participants]

InitializeClass(SemideRegistration)