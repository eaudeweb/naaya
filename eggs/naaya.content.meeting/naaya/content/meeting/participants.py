#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import change_permissions, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl.requestmethod import postonly

#Naaya imports
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.managers.import_export import generate_excel

#Meeting imports
from naaya.content.meeting import WAITING_ROLE, PARTICIPANT_ROLE, ADMINISTRATOR_ROLE
from permissions import PERMISSION_PARTICIPATE_IN_MEETING, PERMISSION_ADMIN_MEETING
from utils import getUserFullName, getUserEmail, getUserOrganization, getUserPhoneNumber
from utils import findUsers, listUsersInGroup
from subscriptions import Subscriptions

class Participants(SimpleItem):
    security = ClassSecurityInfo()

    title = "Participants"

    def __init__(self, id):
        """ """
        self.id = id
        self.subscriptions = Subscriptions('subscriptions')

    security.declareProtected(PERMISSION_PARTICIPATE_IN_MEETING, 'getMeeting')
    def getMeeting(self):
        return self.aq_parent

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'getSubscriptions')
    def getSubscriptions(self):
        return self.subscriptions

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'findUsers')
    def findUsers(self, search_param, search_term):
        """ """
        if len(search_term) == 0:
            return []
        return findUsers(self.getSite(), search_param, search_term)

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'listUsersInGroup')
    def listUsersInGroup(self, search_role):
        """ """
        if len(search_role) == 0:
            return []
        return listUsersInGroup(self.getSite(), search_role)

    security.declareProtected(view, 'isParticipant')
    def isParticipant(self, userid=None):
        """ """
        if userid is None:
            userid = self.REQUEST.AUTHENTICATED_USER.getUserName()
            # fix for signup users
            if userid.startswith('signup:'):
                userid = userid[len('signup:'):]

        return userid in self.getParticipants()

    security.declareProtected(PERMISSION_PARTICIPATE_IN_MEETING, 'getParticipants')
    def getParticipants(self):
        """ """
        meeting = self.getMeeting()
        participants = meeting.users_with_local_role(PARTICIPANT_ROLE)
        administrators = meeting.users_with_local_role(ADMINISTRATOR_ROLE)
        return administrators + participants

    security.declareProtected(PERMISSION_PARTICIPATE_IN_MEETING, 'participantsCount')
    def participantsCount(self):
        """ """
        return len(self.getParticipants())

    def _set_attendee(self, uid, role):
        def can_set_role():
            participants_count = self.participantsCount()
            if (meeting.max_participants > participants_count
                    or meeting.max_participants == 0):
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

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'setAttendees')
    @postonly
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
        if subscriptions._is_account_subscription(uid):
            subscriptions._reject_account_subscription(uid)

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'delAttendees')
    @postonly
    def delAttendees(self, REQUEST):
        """ """
        uids = REQUEST.form.get('uids', [])
        assert isinstance(uids, list)
        for uid in uids:
            self._del_attendee(uid)
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'onAttendees')
    @postonly
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

    security.declareProtected(PERMISSION_PARTICIPATE_IN_MEETING, 'getAttendees')
    def getAttendees(self, sort_on=''):
        """ """
        attendees = self._get_attendees()
        site = self.getSite()

        if sort_on == 'o':
            key = lambda x: self.getAttendeeInfo(x)['organization'].lower()
        elif sort_on == 'name':
            key = lambda x: self.getAttendeeInfo(x)['name'].lower()
        elif sort_on == 'email':
            key = lambda x: self.getAttendeeInfo(x)['email'].lower()
        elif sort_on == 'uid':
            key = lambda x: x.lower()
        elif sort_on == 'role':
            key = lambda x: attendees[x].lower()
        else:
            key = None

        attendee_uids = attendees.keys()

        if key is not None:
            attendee_uids.sort(key=key)

        return attendee_uids

    security.declareProtected(PERMISSION_PARTICIPATE_IN_MEETING, 'getAttendeeInfo')
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
        if not organization:
            organization = self.get_survey_answer(uid, 'w_organization')
        if not organization:
            organization = self.get_survey_answer(uid, 'w_organisation')
        if not phone:
            phone = self.get_survey_answer(uid, 'w_telephone')
        if not phone:
            phone = self.get_survey_answer(uid, 'w_phone')
        attendees = self._get_attendees()
        role = attendees[uid]
        ret = {'uid': uid, 'name': name, 'email': email,
                 'organization': organization, 'phone': phone, 'role': role}
        for k, v in ret.items():
            if not isinstance(v, basestring):
                ret[k] = u''
        return ret

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'onAttendees')
    def getParticipantRole(self):
        """ """
        return PARTICIPANT_ROLE

    security.declareProtected(PERMISSION_PARTICIPATE_IN_MEETING, 'index_html')
    def index_html(self, REQUEST):
        """ """
        return self.getFormsTool().getContent({'here': self},
                        'naaya.content.meeting.participants_index')

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'pickrole_html')
    def pickrole_html(self, REQUEST):
        """ """
        sources = self.getAuthenticationTool().getSources()
        return self.getFormsTool().getContent({'here': self, 'sources': sources},
                        'naaya.content.meeting.participants_pickrole')

    security.declareProtected(PERMISSION_PARTICIPATE_IN_MEETING, 'participants_table')
    def participants_table(self, form_name, input_name):
        """ """
        return self.getFormsTool().getContent({'here': self,
                                                'form_name': form_name,
                                                'input_name': input_name},
                         'naaya.content.meeting.participants_table')

    security.declareProtected(view, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """exports the participants listing in an excel file"""
        assert self.rstk.we_provide('Excel export')

        header = ['Name', 'User ID', 'Email', 'Organisation', 'Phone', 'Status']
        rows = []
        participants = self.getAttendees()
        for participant in participants:
            part_info = self.getAttendeeInfo(participant)
            rows.append([part_info['name'], part_info['uid'], part_info['email'], part_info['organization'], part_info['phone'], part_info['role']])

        RESPONSE.setHeader('Content-Type', 'application/vnd.ms-excel')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s.xls' % self.id)
        return generate_excel(header, rows)

InitializeClass(Participants)

NaayaPageTemplateFile('zpt/participants_index', globals(),
        'naaya.content.meeting.participants_index')
NaayaPageTemplateFile('zpt/participants_pickrole', globals(),
        'naaya.content.meeting.participants_pickrole')
NaayaPageTemplateFile('zpt/participants_table', globals(),
        'naaya.content.meeting.participants_table')

