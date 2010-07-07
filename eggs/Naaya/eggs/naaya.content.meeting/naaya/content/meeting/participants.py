#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import change_permissions, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass

#Naaya imports
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

#Meeting imports
from naaya.content.meeting import WAITING_ROLE, PARTICIPANT_ROLE, ADMINISTRATOR_ROLE
from utils import getUserFullName, getUserEmail, getUserOrganization, getUserPhoneNumber
from utils import findUsers, findUsersWithRole
from subscriptions import Subscriptions

class Participants(SimpleItem):
    security = ClassSecurityInfo()

    title = "Meeting participants"

    def __init__(self, id):
        """ """
        self.id = id
        self.subscriptions = Subscriptions('subscriptions')

    def getMeeting(self):
        return self.aq_parent

    def getSubscriptions(self):
        return self.subscriptions

    def resetSubscriptions(self):
        """ """
        self.subscriptions = Subscriptions('subscriptions')

    def findUsers(self, search_param, search_term):
        """ """
        return findUsers(self.getSite(), search_param, search_term)

    def findUsersWithRole(self, search_role):
        """ """
        return findUsersWithRole(self.getSite(), search_role)

    def getParticipants(self):
        """ """
        meeting = self.getMeeting()
        participants = meeting.users_with_local_role(PARTICIPANT_ROLE)
        administrators = meeting.users_with_local_role(ADMINISTRATOR_ROLE)
        return administrators + participants

    def participantsCount(self):
        """ """
        return len(self.getParticipants())

    def _set_attendee(self, uid, role):
        def can_set_role():
            participants_count = self.participantsCount()
            if meeting.max_participants > participants_count:
                return True
            # can also change rights even if meeting is full
            if meeting.max_participants == participants_count:
                if uid in self.getParticipants():
                    return True
            return False

        meeting = self.getMeeting()
        assert role in [WAITING_ROLE, PARTICIPANT_ROLE, ADMINISTRATOR_ROLE]

        if uid in meeting.users_with_local_role(role):
            return

        if can_set_role():
            meeting.manage_setLocalRoles(uid, [role])
        else:
            meeting.manage_setLocalRoles(uid, [WAITING_ROLE])

    def setAttendees(self, role, REQUEST):
        """ """
        uids = REQUEST.form.get('uids', [])
        assert isinstance(uids, list)
        for uid in uids:
            self._set_attendee(uid, role)
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def _del_attendee(self, uid):
        self.getMeeting().manage_delLocalRoles([uid])

        subscriptions = self.getSubscriptions()
        if subscriptions._is_signup(uid):
            subscriptions._reject_signup(uid)

    def delAttendees(self, REQUEST):
        """ """
        uids = REQUEST.form.get('uids', [])
        assert isinstance(uids, list)
        for uid in uids:
            self._del_attendee(uid)
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def onAttendees(self, REQUEST):
        """ """
        if 'del_attendees' in REQUEST.form:
            return self.delAttendees(REQUEST)
        elif 'set_administrators' in REQUEST.form:
            return self.setAttendees('Administrator', REQUEST)
        elif 'set_participants' in REQUEST.form:
            return self.setAttendees(PARTICIPANT_ROLE, REQUEST)

        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def _get_attendees(self):
        """ """
        meeting = self.getMeeting()
        attendees = {}
        for uid in meeting.users_with_local_role(WAITING_ROLE):
            attendees[uid] = WAITING_ROLE
        for uid in meeting.users_with_local_role(PARTICIPANT_ROLE):
            attendees[uid] = PARTICIPANT_ROLE
        for uid in meeting.users_with_local_role(ADMINISTRATOR_ROLE):
            attendees[uid] = ADMINISTRATOR_ROLE
        return attendees

    def getAttendees(self, sort_on=''):
        """ """
        attendees = self._get_attendees()
        site = self.getSite()
        key = None
        if sort_on == 'o':
            key = lambda x: getUserOrganization(site, x)
        elif sort_on == 'name':
            key = lambda x: getUserFullName(site, x)
        elif sort_on == 'email':
            key = lambda x: getUserEmail(site, x)
        elif sort_on == 'uid':
            key = lambda x: x
        elif sort_on == 'role':
            key = lambda x: attendees[x]

        if key is None:
            return attendees.keys()
        return sorted(attendees.keys(), key=key)

    def getAttendeeInfo(self, uid):
        """ """
        subscriptions = self.getSubscriptions()
        if subscriptions._is_signup(uid):
            user = subscriptions.getSignup(uid)
            name = user.name
            email = user.email
            organization = user.organization
            phone = user.phone
        else:
            site = self.getSite()
            name = getUserFullName(site, uid)
            email = getUserEmail(site, uid)
            organization = getUserOrganization(site, uid)
            phone = getUserPhoneNumber(site, uid)
        attendees = self._get_attendees()
        role = attendees[uid]
        return {'uid': uid, 'name': name, 'email': email,
                 'organization': organization, 'phone': phone, 'role': role}

    def getParticipantRole(self):
        """ """
        return PARTICIPANT_ROLE

    security.declareProtected(view, 'userCanChangePermissions')
    def userCanChangePermissions(self):
        """ """
        return self.checkPermission(change_permissions)

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST):
        """ """
        return self.getFormsTool().getContent({'here': self},
                        'naaya.content.meeting.participants_index')

    security.declareProtected(view, 'pickrole_html')
    def pickrole_html(self, REQUEST):
        """ """
        return self.getFormsTool().getContent({'here': self},
                        'naaya.content.meeting.participants_pickrole')

    security.declareProtected(view, 'participants_table')
    def participants_table(self, form_name, input_name):
        """ """
        return self.getFormsTool().getContent({'here': self,
                                                'form_name': form_name,
                                                'input_name': input_name},
                         'naaya.content.meeting.participants_table')

InitializeClass(Participants)

NaayaPageTemplateFile('zpt/participants_index', globals(),
        'naaya.content.meeting.participants_index')
NaayaPageTemplateFile('zpt/participants_pickrole', globals(),
        'naaya.content.meeting.participants_pickrole')
NaayaPageTemplateFile('zpt/participants_table', globals(),
        'naaya.content.meeting.participants_table')

