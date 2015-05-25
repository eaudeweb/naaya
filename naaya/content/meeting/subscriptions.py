# Python imports
from base64 import urlsafe_b64encode
from random import randrange

# Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.unauthorized import Unauthorized
from Globals import InitializeClass
from Persistence import Persistent
from BTrees.OOBTree import OOBTree
from AccessControl.User import BasicUserFolder, SimpleUser
from AccessControl.Permissions import view

# Naaya imports
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

# meeting imports
from naaya.content.meeting import PARTICIPANT_ROLE
from permissions import PERMISSION_ADMIN_MEETING
from utils import getUserFullName, getUserEmail, getUserOrganization
from utils import getUserPhoneNumber


class Subscriptions(SimpleItem):
    security = ClassSecurityInfo()

    title = "Meeting registrations"

    def __init__(self, id):
        """ """
        super(SimpleItem, self).__init__(id)
        self.id = id
        self._signups = OOBTree()
        self._account_subscriptions = OOBTree()

    security.declarePublic('getMeeting')

    def getMeeting(self):
        return self.aq_parent.aq_parent

    def _validate_signup(self, form):
        """ """
        formdata = {}
        formerrors = {}

        keys = ('first_name', 'last_name', 'email', 'organization', 'phone')
        formdata = dict((key, form.get(key, '')) for key in keys)
        for key in formdata:
            if formdata[key] == '':
                formerrors[key] = 'This field is mandatory'

        if formerrors == {}:
            if formdata['email'].count('@') != 1:
                formerrors['email'] = ('An email address must contain '
                                       'a single @')

        if formerrors == {}:
            formerrors = None
        return formdata, formerrors

    def _add_signup(self, formdata):
        """ """
        meeting = self.getMeeting()
        key = random_key()
        name = formdata['first_name'] + ' ' + formdata['last_name']
        email = formdata['email']
        organization = formdata['organization']
        phone = formdata['phone']

        signup = SignUp(key, name, email, organization, phone)

        self._signups.insert(key, signup)

        if meeting.auto_register:
            self._accept_signup(key)

        email_sender = self.getMeeting().getEmailSender()
        email_sender.send_signup_email(signup)
        if self.REQUEST.AUTHENTICATED_USER.getUserName() == 'Anonymous User':
            self.REQUEST.SESSION['nymt-current-key'] = key

    security.declareProtected(view, 'signup')

    def signup(self, REQUEST):
        """ """
        meeting = self.getMeeting()
        if not meeting.allow_register:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                             '/subscription_not_allowed')

        if REQUEST.get('add_users'):
            return self.subscribe_accounts(REQUEST)

        if REQUEST.get('add_signup'):
            formdata, formerrors = self._validate_signup(REQUEST.form)

            # check Captcha/reCaptcha
            if not (self.checkPermissionSkipCaptcha() or
                    REQUEST.SESSION.get('captcha_passed')):
                recaptcha_response = REQUEST.form.get('g-recaptcha-response',
                                                      '')
                captcha_validator = self.validateCaptcha(recaptcha_response,
                                                         REQUEST)
                if captcha_validator:
                    if formerrors is None:
                        formerrors = {}
                    formerrors['captcha'] = captcha_validator
                else:
                    REQUEST.SESSION['captcha_passed'] = True

            if formerrors is not None:
                return self.getFormsTool().getContent(
                    {'here': self,
                     'formdata': formdata,
                     'formerrors': formerrors},
                    'naaya.content.meeting.subscription_signup')
            else:
                self._add_signup(formdata)
                if self.getMeeting().survey_required:
                    REQUEST.RESPONSE.redirect(
                        self.getMeeting().absolute_url())
                else:
                    REQUEST.RESPONSE.redirect(self.absolute_url() +
                                              '/signup_successful')

        # check Captcha/reCaptcha also for searching users
        captcha_validator = None
        if (REQUEST.get('search_user') or
                REQUEST.get('search_user_with_role')):
            if not (self.checkPermissionSkipCaptcha() or
                    REQUEST.SESSION.get('captcha_passed')):
                recaptcha_response = REQUEST.form.get('g-recaptcha-response',
                                                      '')
                captcha_validator = self.validateCaptcha(recaptcha_response,
                                                         REQUEST)
                if not captcha_validator:
                    REQUEST.SESSION['captcha_passed'] = True

        return self.getFormsTool().getContent(
            {'here': self, 'captcha_errors': captcha_validator},
            'naaya.content.meeting.subscription_signup')

    security.declareProtected(view, 'signup_successful')

    def signup_successful(self, REQUEST):
        """ """
        return self.getFormsTool().getContent(
            {'here': self},
            'naaya.content.meeting.subscription_signup_successful')

    security.declareProtected(view, 'subscribe')

    def subscribe(self, REQUEST):
        """ """
        meeting = self.getMeeting()
        if not meeting.allow_register:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                             '/subscription_not_allowed')

        return self.getFormsTool().getContent(
            {'here': self}, 'naaya.content.meeting.subscription_subscribe')

    def getSignups(self):
        """ """
        if not self.checkPermissionParticipateInMeeting():
            raise Unauthorized
        return self._signups.itervalues()

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'getSignup')

    def getSignup(self, key):
        """ """
        return self._signups.get(key, None)

    def index_html(self, REQUEST):
        """ """
        if not self.checkPermissionParticipateInMeeting():
            raise Unauthorized
        return self.getFormsTool().getContent(
            {'here': self}, 'naaya.content.meeting.subscription_index')

    def _accept_signup(self, key):
        """ """
        meeting = self.getMeeting()
        meeting.getParticipants()._set_attendee(key, PARTICIPANT_ROLE)
        signup = self._signups[key]
        signup.accepted = 'accepted'

        email_sender = meeting.getEmailSender()
        email_sender.send_signup_accepted_email(signup)

    def _reject_signup(self, key):
        """ """
        meeting = self.getMeeting()
        signup = self._signups[key]
        signup.accepted = 'rejected'

        participants = meeting.getParticipants()
        # delete the 'reimbursed' status
        participants.setAttendeeInfo([key], 'reimbursed', False)
        if key in participants._get_attendees():
            participants._del_attendee(key)

        email_sender = meeting.getEmailSender()
        email_sender.send_signup_rejected_email(signup)

    def _delete_signup(self, key):
        """ """
        meeting = self.getMeeting()
        signup = self._signups.pop(key, None)
        if signup is None:
            return

        participants = meeting.getParticipants()
        if key in participants._get_attendees():
            participants._del_attendee(key)

        email_sender = meeting.getEmailSender()
        email_sender.send_signup_rejected_email(signup)

    def _is_signup(self, key):
        """ """
        return key in self._signups and \
            self._signups[key].accepted == 'accepted'

    def _is_pending_signup(self, key):
        """ """
        return key in self._signups and \
            self._signups[key].accepted == 'new'

    def manageSubscriptions(self, REQUEST):
        """ """
        if not (self.checkPermissionAdminMeeting() or self.nfp_for_country()):
            raise Unauthorized
        uids = REQUEST.form.get('uids', [])
        assert isinstance(uids, list)
        for uid in uids:
            if 'accept' in REQUEST.form:
                if self._is_signup(uid):
                    self._accept_signup(uid)
                else:
                    self._accept_account_subscription(uid)
            elif 'reject' in REQUEST.form:
                if self._is_signup(uid):
                    self._reject_signup(uid)
                else:
                    self._reject_account_subscription(uid)
            elif 'delete' in REQUEST.form:
                if not self.checkPermissionAdminMeeting():
                    raise Unauthorized
                if self._is_signup(uid):
                    self._delete_signup(uid)
                else:
                    self._delete_account_subscription(uid)
        if 'set_representative' in REQUEST.form:
            self.setRepresentatives(REQUEST)
        elif 'unset_representative' in REQUEST.form:
            self.setRepresentatives(REQUEST, remove=True)
        elif 'set_reimbursement' in REQUEST.form:
            self.setReimbursement(REQUEST)
        elif 'unset_reimbursement' in REQUEST.form:
            self.setReimbursement(REQUEST, remove=True)
        elif 'save_changes' in REQUEST.form:
            self.save_changes(REQUEST)

        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declarePublic('welcome')

    def welcome(self, REQUEST, came_from=None):
        """ """
        if 'logout' in REQUEST.form:
            REQUEST.SESSION['nymt-current-key'] = None
            return REQUEST.RESPONSE.redirect(self.getMeeting().absolute_url())

        key = REQUEST.get('key', None)
        signup = self.getSignup(key)
        if self._is_signup(key) or self._is_pending_signup(key):
            REQUEST.SESSION['nymt-current-key'] = key
            if came_from:
                return REQUEST.RESPONSE.redirect(came_from)
            else:
                return REQUEST.RESPONSE.redirect(
                    self.getMeeting().absolute_url())

        return self.getFormsTool().getContent(
            {'here': self,
             'signup': signup},
            'naaya.content.meeting.subscription_welcome')

    def _add_account_subscription(self, uid, accept=False):
        """ """
        # If the subscription already exists or the user is alread signed up
        # skip the whole thing
        if self._is_account_subscription(uid):
            return
        key = uid.replace('signup:', '')
        if self._is_signup(key):
            return
        site = self.getSite()
        meeting = self.getMeeting()
        name = getUserFullName(site, uid)
        # If for any reason we still don't have a name, at least use UID
        if not name:
            name = uid
        email = getUserEmail(site, uid)
        organization = getUserOrganization(site, uid)
        if not organization:
            organization = self.get_survey_answer(uid, 'w_organization')
        if not organization:
            organization = self.get_survey_answer(uid, 'w_organisation')
        phone = getUserPhoneNumber(site, uid)
        if not phone:
            phone = self.get_survey_answer(uid, 'w_telephone')
        if not phone:
            phone = self.get_survey_answer(uid, 'w_phone')

        account_subscription = AccountSubscription(uid, name, email,
                                                   organization, phone)

        self._account_subscriptions.insert(uid, account_subscription)

        if meeting.auto_register or accept:
            self._accept_account_subscription(uid)

        email_sender = self.getMeeting().getEmailSender()
        email_sender.send_account_subscription_email(account_subscription)

    security.declareProtected(PERMISSION_ADMIN_MEETING,
                              'update_account_subscription')

    def update_account_subscription(self, uid):
        """ """
        site = self.getSite()
        name = getUserFullName(site, uid)
        email = getUserEmail(site, uid)
        organization = getUserOrganization(site, uid)
        phone = getUserPhoneNumber(site, uid)

        account_subscription = AccountSubscription(uid, name, email,
                                                   organization, phone)

        self._account_subscriptions.update({uid: account_subscription})

    security.declareProtected(view, 'subscribe_accounts')

    def subscribe_accounts(self, REQUEST):
        """ """
        meeting = self.getMeeting()
        if not meeting.allow_register:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                             '/subscription_not_allowed')

        # check Captcha/reCaptcha also for searching users
        if not (self.checkPermissionSkipCaptcha() or
                REQUEST.SESSION.get('captcha_passed')):
            recaptcha_response = REQUEST.form.get('g-recaptcha-response', '')
            captcha_validator = self.validateCaptcha(recaptcha_response,
                                                     REQUEST)
            if captcha_validator:
                return self.getFormsTool().getContent(
                    {'here': self, 'captcha_errors': captcha_validator},
                    'naaya.content.meeting.subscription_signup')
            else:
                REQUEST.SESSION['captcha_passed'] = True

        uids = REQUEST.form.get('uids', [])
        assert isinstance(uids, list)
        for uid in uids:
            self._add_account_subscription(uid)
        return REQUEST.RESPONSE.redirect(
            self.absolute_url() +
            '/subscribe_account_successful?uids='+','.join(uids))

    security.declareProtected(view, 'subscribe_my_account')

    def subscribe_my_account(self, REQUEST):
        """ """
        meeting = self.getMeeting()
        if not meeting.allow_register:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                             '/subscription_not_allowed')

        self._add_account_subscription(REQUEST.AUTHENTICATED_USER.getId())
        if self.survey_required:
            site = self.getSite()
            path = str(self.survey_pointer)
            survey_ob = site.unrestrictedTraverse(path, None)
            if survey_ob is not None and \
                    survey_ob.meta_type == 'Naaya Mega Survey':
                answers = survey_ob.getAnswers()
                respondents = [a.respondent for a in answers]
                current_user = REQUEST.AUTHENTICATED_USER.getUserName()
                if current_user not in respondents:
                    self.setSessionInfoTrans(
                        'Registration successfully sent for approval. '
                        'Please also respond to the following questionaire.')
                    return REQUEST.RESPONSE.redirect(
                        '%s/%s' % (self.getSite().absolute_url(),
                                   self.survey_pointer))
        return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                         '/subscribe_account_successful')

    security.declareProtected(view, 'subscribe_account_successful')

    def subscribe_account_successful(self, REQUEST):
        """ """
        return self.getFormsTool().getContent(
            {'here': self},
            'naaya.content.meeting.subscription_subscribe_successful')

    def getAccountSubscriptions(self):
        """ """
        if not self.checkPermissionParticipateInMeeting():
            raise Unauthorized
        return self._account_subscriptions.itervalues()

    def getSubscriptions(self):
        """ """
        if not self.checkPermissionParticipateInMeeting():
            raise Unauthorized
        subscriptions = (list(self._signups.itervalues()) +
                         list(self._account_subscriptions.itervalues()))
        statuses = {'new': 0,
                    'accepted': 1,
                    'rejected': 2
                    }
        return sorted(subscriptions, key=lambda x: statuses.get(x.accepted))

    security.declareProtected(PERMISSION_ADMIN_MEETING,
                              'getAccountSubscription')

    def getAccountSubscription(self, uid):
        """ """
        return self._account_subscriptions.get(uid, None)

    def _is_account_subscription(self, uid):
        """ """
        return uid in self._account_subscriptions and \
            self._account_subscriptions[uid].accepted == 'accepted'

    def _accept_account_subscription(self, uid):
        """ """
        meeting = self.getMeeting()
        meeting.getParticipants()._set_attendee(uid, PARTICIPANT_ROLE)
        account_subscription = self._account_subscriptions[uid]
        account_subscription.accepted = 'accepted'

        email_sender = meeting.getEmailSender()
        email_sender.send_account_subscription_accepted_email(
            account_subscription)

    def _reject_account_subscription(self, uid):
        """ """
        meeting = self.getMeeting()
        account_subscription = self._account_subscriptions[uid]
        account_subscription.accepted = 'rejected'

        participants = meeting.getParticipants()
        # remove the 'reimbursed' status
        participants.setAttendeeInfo([uid], 'reimbursed', False)
        if uid in participants._get_attendees():
            participants._del_attendee(uid)

        email_sender = meeting.getEmailSender()
        email_sender.send_account_subscription_rejected_email(
            account_subscription)

    def _delete_account_subscription(self, uid):
        """ """
        meeting = self.getMeeting()
        account_subscription = self._account_subscriptions.pop(uid, None)
        if account_subscription is None:
            return

        participants = meeting.getParticipants()
        if uid in participants._get_attendees():
            participants._del_attendee(uid)

        email_sender = meeting.getEmailSender()
        email_sender.send_account_subscription_rejected_email(
            account_subscription)

    security.declareProtected(view, 'subscription_not_allowed')

    def subscription_not_allowed(self, REQUEST):
        """ """
        return self.getFormsTool().getContent(
            {'here': self}, 'naaya.content.meeting.subscription_not_allowed')


InitializeClass(Subscriptions)


class SignUp(Persistent):
    def __init__(self, key, name, email, organization, phone):
        self.key = key
        self.name = name
        self.email = email
        self.organization = organization
        self.phone = phone
        self.accepted = 'new'


class AccountSubscription(Persistent):
    def __init__(self, uid, name, email, organization, phone):
        self.uid = uid
        self.name = name
        self.email = email
        self.organization = organization
        self.phone = phone
        self.accepted = 'new'


class SignupUsersTool(BasicUserFolder):
    def getMeeting(self):
        return self.aq_parent

    def authenticate(self, name, password, REQUEST):
        participants = self.getMeeting().getParticipants()
        subscriptions = participants.getSubscriptions()

        key = REQUEST.SESSION.get('nymt-current-key', None)
        if subscriptions._is_signup(key):
            role = participants._get_attendees()[key]['role']
            return SimpleUser('signup:' + key, '', (role,), [])
        if subscriptions._is_pending_signup(key):
            role = 'Meeting Waiting List'
            return SimpleUser('signup:' + key, '', (role,), [])
        else:
            return None

NaayaPageTemplateFile('zpt/subscription_subscribe', globals(),
                      'naaya.content.meeting.subscription_subscribe')
NaayaPageTemplateFile(
    'zpt/subscription_subscribe_successful', globals(),
    'naaya.content.meeting.subscription_subscribe_successful')
NaayaPageTemplateFile('zpt/subscription_signup', globals(),
                      'naaya.content.meeting.subscription_signup')
NaayaPageTemplateFile('zpt/subscription_signup_successful', globals(),
                      'naaya.content.meeting.subscription_signup_successful')
NaayaPageTemplateFile('zpt/subscription_index', globals(),
                      'naaya.content.meeting.subscription_index')
NaayaPageTemplateFile('zpt/subscription_welcome', globals(),
                      'naaya.content.meeting.subscription_welcome')
NaayaPageTemplateFile('zpt/subscription_not_allowed', globals(),
                      'naaya.content.meeting.subscription_not_allowed')


def random_key():
    """ generate a 120-bit random key, expressed as 20 base64 characters """
    return urlsafe_b64encode(''.join(chr(randrange(256)) for i in xrange(15)))
