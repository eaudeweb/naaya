#Python imports
from base64 import urlsafe_b64encode
from random import randrange

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Persistence import Persistent
from BTrees.OOBTree import OOBTree

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

    def signup(self, REQUEST):
        """ """
        if REQUEST.REQUEST_METHOD == 'GET':
            return self.getFormsTool().getContent({'here': self},
                                 'meeting_subscription_signup')

        if REQUEST.REQUEST_METHOD == 'POST':
            formdata, formerrors = self._validate_signup(REQUEST.form)
            if formerrors is not None:
                return self.getFormsTool().getContent({'here': self,
                                                     'formdata': formdata,
                                                     'formerrors': formerrors},
                                         'meeting_subscription_signup')
            else:
                self._add_signup(formdata)
                REQUEST.RESPONSE.redirect(self.aq_parent.aq_parent.absolute_url())

    def subscribe(self, REQUEST):
        """ """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/signup')

    def getSignups(self):
        """ """
        return self._signups.itervalues()

    def getSignup(self, key):
        """ """
        return self._signups.get(key, None)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'index_html')
    def index_html(self, REQUEST):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'meeting_subscription_index')

    def _accept_signup(self, key):
        """ """
        self.aq_parent._set_attendee(key, PARTICIPANT_ROLE)
        self._signups[key].accepted = True

    def _reject_signup(self, key):
        """ """
        del self._signups[key]

    def _is_signup(self, key):
        """ """
        return self._signups.has_key(key)

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
        REQUEST.RESPONSE.redirect(self.absolute_url())

InitializeClass(Subscriptions)

class SignUp(Persistent):
    def __init__(self, key, name, email, organization, phone):
        self.key = key
        self.name = name
        self.email = email
        self.organization = organization
        self.phone = phone
        self.accepted = False

NaayaPageTemplateFile('zpt/subscription_signup', globals(), 'meeting_subscription_signup')
NaayaPageTemplateFile('zpt/subscription_index', globals(), 'meeting_subscription_index')

def random_key():
    """ generate a 120-bit random key, expressed as 20 base64 characters """
    return urlsafe_b64encode(''.join(chr(randrange(256)) for i in xrange(15)))

