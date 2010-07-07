#Python imports
from base64 import urlsafe_b64encode
from random import randrange

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Persistence import Persistent
from BTrees.OOBTree import OOBTree
from AccessControl.User import BasicUserFolder, SimpleUser

#Naaya imports
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

#meeting imports
from naaya.content.meeting import PARTICIPANT_ROLE

class Subscriptions(SimpleItem):
    security = ClassSecurityInfo()

    title = "Meeting subscriptions"

    def __init__(self, id):
        """ """
        super(SimpleItem, self).__init__(id)
        self.id = id
        self._signups = OOBTree()

    def getMeeting(self):
        return self.aq_parent.aq_parent

    def _validate_signup(self, form):
        """ """
        formdata = {}
        formerrors = {}

        keys = ('first_name', 'last_name', 'email', 'organization', 'phone')
        formdata = dict( (key, form.get(key, '')) for key in keys )
        for key in formdata:
            if formdata[key] == '':
                formerrors[key] = 'This field is mandatory'

        if formerrors == {}:
            if formdata['email'].count('@') != 1:
                formerrors['email'] = 'An email address must contain a single @'

        if formerrors == {}:
            formerrors = None
        return formdata, formerrors

    def _add_signup(self, formdata):
        """ """
        key = random_key()
        name = formdata['first_name'] + ' ' + formdata['last_name']
        email = formdata['email']
        organization = formdata['organization']
        phone = formdata['phone']

        signup = SignUp(key, name, email, organization, phone)

        self._signups.insert(key, signup)

        email_sender = self.getMeeting().getEmailSender()
        email_sender.send_signup_email(signup)
        

    def signup(self, REQUEST):
        """ """
        if REQUEST.REQUEST_METHOD == 'GET':
            return self.getFormsTool().getContent({'here': self},
                                 'naaya.content.meeting.subscription_signup')

        if REQUEST.REQUEST_METHOD == 'POST':
            formdata, formerrors = self._validate_signup(REQUEST.form)
            if formerrors is not None:
                return self.getFormsTool().getContent({'here': self,
                                                     'formdata': formdata,
                                                     'formerrors': formerrors},
                                         'naaya.content.meeting.subscription_signup')
            else:
                self._add_signup(formdata)
                REQUEST.RESPONSE.redirect(self.getMeeting().absolute_url())

    def subscribe(self, REQUEST):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'naaya.content.meeting.subscription_subscribe')

    def getSignups(self):
        """ """
        return self._signups.itervalues()

    def getSignup(self, key):
        """ """
        return self._signups.get(key, None)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'index_html')
    def index_html(self, REQUEST):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'naaya.content.meeting.subscription_index')

    def _accept_signup(self, key):
        """ """
        meeting = self.getMeeting()
        meeting.getParticipants()._set_attendee(key, PARTICIPANT_ROLE)
        signup = self._signups[key]
        signup.accepted = 'accepted'

        if not signup.email_sent:
            email_sender = meeting.getEmailSender()
            result = email_sender.send_signup_accepted_email(signup)

            if result == 1:
                signup.email_send = True

    def _reject_signup(self, key):
        """ """
        self._signups[key].accepted = 'rejected'

        participants = self.getMeeting().getParticipants()
        if key in participants._get_attendees():
            participants._del_attendee(key)

    def _is_signup(self, key):
        """ """
        return self._signups.has_key(key) and self._signups[key].accepted == 'accepted'

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'manageSignups')
    def manageSignups(self, REQUEST):
        """ """
        keys = REQUEST.form.get('keys', [])
        assert isinstance(keys, list)
        if 'accept' in REQUEST.form:
            for key in keys:
                self._accept_signup(key)
        elif 'reject' in REQUEST.form:
            for key in keys:
                self._reject_signup(key)

        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def welcome(self, REQUEST):
        """ """
        if 'logout' in REQUEST.form:
            REQUEST.SESSION['nymt-current-key'] = None
            return REQUEST.RESPONSE.redirect(self.getMeeting().absolute_url())

        key = REQUEST.get('key', None)
        signup = self.getSignup(key)
        if self._is_signup(key): 
            REQUEST.SESSION['nymt-current-key'] = key

        return self.getFormsTool().getContent({'here': self,
                                                'signup': signup},
                                         'naaya.content.meeting.subscription_welcome')

InitializeClass(Subscriptions)

class SignUp(Persistent):
    def __init__(self, key, name, email, organization, phone):
        self.key = key
        self.name = name
        self.email = email
        self.organization = organization
        self.phone = phone
        self.accepted = 'new'
        self.email_sent = False

class SignupUsersTool(BasicUserFolder):
    def getMeeting(self):
        return self.aq_parent

    def authenticate(self, name, password, REQUEST):
        participants = self.getMeeting().getParticipants()
        subscriptions = participants.getSubscriptions()

        key = REQUEST.SESSION.get('nymt-current-key', None)
        if subscriptions._is_signup(key):
            role = participants._get_attendees()[key]
            return SimpleUser('signup:' + key, '', (role,), [])
        else:
            return None

NaayaPageTemplateFile('zpt/subscription_subscribe', globals(),
        'naaya.content.meeting.subscription_subscribe')
NaayaPageTemplateFile('zpt/subscription_signup', globals(),
        'naaya.content.meeting.subscription_signup')
NaayaPageTemplateFile('zpt/subscription_index', globals(),
        'naaya.content.meeting.subscription_index')
NaayaPageTemplateFile('zpt/subscription_welcome', globals(),
        'naaya.content.meeting.subscription_welcome')

def random_key():
    """ generate a 120-bit random key, expressed as 20 base64 characters """
    return urlsafe_b64encode(''.join(chr(randrange(256)) for i in xrange(15)))

