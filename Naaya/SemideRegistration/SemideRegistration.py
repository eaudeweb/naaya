import re
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.Folder import Folder
import re
import time

from Products.NaayaCore.managers import utils as naaya_utils
import SemideParticipant
from utilities.Slugify import slugify


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

def registration_validation(REQUEST):
    """ Validates the new meeting registration fields """
    has_errors = False

    title = REQUEST.form.get('title', '')
    administrative_email = REQUEST.form.get('administrative_email', '')
    start_date = REQUEST.form.get('start_date', '')
    end_date = REQUEST.form.get('end_date', '')

    if not title:
        REQUEST.set('title_error', True)
        has_errors = True
    if not administrative_email:
        REQUEST.set('administrative_email_error', True)
        has_errors = True
    if not start_date:
        REQUEST.set('start_date_error', True)
        has_errors = True
    if not end_date:
        REQUEST.set('end_date_error', True)
        has_errors = True
    if administrative_email and not email_expr.match(administrative_email):
        REQUEST.set('administrative_email_invalid', True)
        has_errors = True
    if start_date:
        try:
            date = time.strptime(start_date, "%d/%m/%Y")
        except:
            REQUEST.set('start_date_invalid', True)
            has_errors = True
    if end_date:
        try:
            date = time.strptime(end_date, "%d/%m/%Y")
        except:
            REQUEST.set('end_date_invalid', True)
            has_errors = True
    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors

email_expr = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)
def form_validation (mandatory_fields, date_fields, time_fields, REQUEST):
    has_errors = False
    #@TODO reverse cycling oder mandatory_fields --> REQUEST.form
    for k,v in REQUEST.form.items():
        if k in mandatory_fields:
            if k == 'email' and v:
                if not email_expr.match(v):
                    REQUEST.set('%s_notvalid' % k, True)
                    has_errors = True
            if not v:
                REQUEST.set('%s_error' % k, True)
                has_errors = True
        if k in date_fields and v:
            try:
                temp = time.strptime(v, "%d/%m/%Y")
            except:
                REQUEST.set('%s_notvalid' % k, True)
                has_errors = True
        if k in time_fields and v:
            try:
                temp = time.strptime(v, "%H:%M")
            except:
                REQUEST.set('%s_notvalid' % k, True)
                has_errors = True
    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors

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
            form_valid = form_validation(SemideParticipant.PART_MANDATORY_FIELDS,
                                            SemideParticipant.DATE_FIELDS,
                                            SemideParticipant.TIME_FIELDS,
                                            REQUEST)
            if form_valid:
                registration_no = naaya_utils.genRandomId(10)
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                ob = SemideParticipant.SemideParticipant(registration_no, **cleaned_data)
                self._setObject(registration_no, ob)
                return REQUEST.RESPONSE.redirect(self.absolute_url())
        return self._registration_html(REQUEST)

    _registration_press_html = PageTemplateFile('zpt/registration/registration_press', globals())
    def registration_press_html(self, REQUEST):
        """ registration form """
        submit =  REQUEST.form.get('submit', '')
        if submit:
            form_valid = form_validation(SemideParticipant.PRESS_MANDATORY_FIELDS,
                                            SemideParticipant.DATE_FIELDS,
                                            SemideParticipant.TIME_FIELDS,
                                            REQUEST)
            if form_valid:
                registration_no = naaya_utils.genRandomId(10)
                cleaned_data = REQUEST.form
                del cleaned_data['submit']
                ob = SemideParticipant.SemidePress(registration_no, **cleaned_data)
                self._setObject(registration_no, ob)
                return REQUEST.RESPONSE.redirect(self.absolute_url())
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