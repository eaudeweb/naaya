# Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.unauthorized import Unauthorized
from AccessControl.Permissions import view
from Globals import InitializeClass
from AccessControl.requestmethod import postonly
from datetime import datetime

# Naaya imports
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.managers.import_export import (generate_excel,
                                                       generate_csv)

# Meeting imports
from naaya.content.meeting import (WAITING_ROLE, PARTICIPANT_ROLE,
                                   ADMINISTRATOR_ROLE, OWNER_ROLE)
from permissions import PERMISSION_ADMIN_MEETING
from Products.NaayaCore.AuthenticationTool.utils import (
    getUserFullName, getUserEmail, getUserOrganization, getUserPhoneNumber,
    findUsers, listUsersInGroup)
from subscriptions import Subscriptions
from countries import country_from_country_code


class Participants(SimpleItem):
    security = ClassSecurityInfo()

    title = "Participants"

    def __init__(self, id):
        """ """
        self.id = id
        self.subscriptions = Subscriptions('subscriptions')

    def getMeeting(self):
        return self.aq_parent

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'getSubscriptions')

    def getSubscriptions(self):
        return self.subscriptions

    security.declareProtected(view, 'findUsers')

    def findUsers(self, search_param, search_term):
        """ """
        if len(search_term) == 0:
            return []
        return findUsers(self.getSite(), search_param, search_term)

    security.declareProtected(view, 'listUsersInGroup')

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

        return userid in self._get_participants()

    def _get_participants(self):
        """ """
        meeting = self.getMeeting()
        participants = meeting.users_with_local_role(PARTICIPANT_ROLE)
        administrators = meeting.users_with_local_role(ADMINISTRATOR_ROLE)
        return administrators + participants

    def get_participants(self):
        """ """
        if not self.checkPermissionParticipateInMeeting():
            raise Unauthorized
        return self._get_participants()

    def participantsCount(self):
        """ """
        return len(self._get_participants())

    def _set_attendee(self, uid, role):
        def can_set_role():
            participants_count = self.participantsCount()
            if (meeting.max_participants > participants_count
                    or meeting.max_participants == 0):
                return True
            # can also change rights even if meeting is full
            if meeting.max_participants == participants_count:
                if uid in self.get_participants():
                    return True
            return False

        meeting = self.getMeeting()
        assert role in [WAITING_ROLE, PARTICIPANT_ROLE, ADMINISTRATOR_ROLE]

        if uid in meeting.users_with_local_role(role):
            return

        if can_set_role():
            new_roles = [role]
        else:
            new_roles = [WAITING_ROLE]

        # special case - don't lose ownership
        sources, owner = meeting.getOwnerTuple() or (None, None)
        if owner == uid:
            new_roles.append(OWNER_ROLE)

        meeting.manage_setLocalRoles(uid, new_roles)

    @postonly
    def setAttendees(self, role, REQUEST):
        """ """
        if not (self.checkPermissionAdminMeeting() or self.nfp_for_country()):
            raise Unauthorized
        uids = REQUEST.form.get('uids', [])
        assert isinstance(uids, list)
        for uid in uids:
            self.getSubscriptions()._add_account_subscription(uid, accept=True)
            self._set_attendee(uid, role)
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    @postonly
    def setRepresentatives(self, REQUEST, remove=False):
        """ """
        if not self.nfp_for_country():
            raise Unauthorized
        uids = REQUEST.form.get('uids', [])
        assert isinstance(uids, list)
        keys = REQUEST.form.get('keys', [])
        assert isinstance(keys, list)
        ids = uids + keys
        if remove:
            nfp_country_code = None
        else:
            nfp_country_code = self.nfp_for_country()
        self.setAttendeeInfo(ids, 'country', nfp_country_code)
        self.setAttendeeInfo(ids, 'justification', '')
        self.setAttendeeInfo(ids, 'saved_by',
                             REQUEST.AUTHENTICATED_USER.getUserName())
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    @postonly
    def setReimbursement(self, REQUEST, remove=False):
        """ """
        if not self.nfp_for_country():
            raise Unauthorized
        uids = REQUEST.form.get('uids', [])
        assert isinstance(uids, list)
        keys = REQUEST.form.get('keys', [])
        assert isinstance(keys, list)
        ids = uids + keys
        self.setAttendeeInfo(ids, 'reimbursed', not remove)
        self.setAttendeeInfo(ids, 'justification', '')
        self.setAttendeeInfo(ids, 'saved_by',
                             REQUEST.AUTHENTICATED_USER.getUserName())
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

    @postonly
    def save_changes(self, REQUEST):
        """ """
        uids = REQUEST.form.get('uids', []) + REQUEST.form.get('keys', [])
        representers = {}
        form_representers = REQUEST.form.get('represents', [])
        if not isinstance(form_representers, list):
            form_representers = [form_representers]
        reimbursed = REQUEST.form.get('reimbursed', [])
        if not isinstance(reimbursed, list):
            reimbursed = [reimbursed]
        justifications = {}
        form_justifications = REQUEST.form.get('justification', [])
        if not isinstance(form_justifications, list):
            form_justifications = [form_justifications]
        for uid in uids:
            idx = uids.index(uid)
            representers[uid] = form_representers[idx] or None
            justifications[uid] = form_justifications[idx]
        errors = []
        for uid in uids:
            if not justifications[uid]:
                user_name = self.getAuthenticationTool().name_from_userid(uid)
                errors.append('Changes to %s not saved: mandatory field '
                              '"Justification" field missing' % user_name)
                pass
            else:
                self.setAttendeeInfo([uid], 'country', representers[uid])
                self.setAttendeeInfo([uid], 'reimbursed', uid in reimbursed)
                self.setAttendeeInfo([uid], 'justification',
                                     justifications[uid])
                self.setAttendeeInfo([uid], 'saved_by',
                                     REQUEST.AUTHENTICATED_USER.getUserName())
        if errors:
            self.setSessionErrorsTrans(errors)
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    @postonly
    def onAttendees(self, REQUEST):
        """ """
        if not (self.checkPermissionAdminMeeting() or self.nfp_for_country()):
            raise Unauthorized
        if 'del_attendees' in REQUEST.form:
            return self.delAttendees(REQUEST)
        elif 'set_administrators' in REQUEST.form:
            return self.setAttendees(ADMINISTRATOR_ROLE, REQUEST)
        elif 'set_participants' in REQUEST.form:
            return self.setAttendees(PARTICIPANT_ROLE, REQUEST)
        elif 'set_representative' in REQUEST.form:
            return self.setRepresentatives(REQUEST)
        elif 'set_reimbursement' in REQUEST.form:
            return self.setReimbursement(REQUEST)
        elif 'unset_representative' in REQUEST.form:
            return self.setRepresentatives(REQUEST, remove=True)
        elif 'unset_reimbursement' in REQUEST.form:
            return self.setReimbursement(REQUEST, remove=True)
        elif 'save_changes' in REQUEST.form:
            return self.save_changes(REQUEST)
        elif 'resend_emails' in REQUEST.form:
            return self.resend_emails(REQUEST)

        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(PERMISSION_ADMIN_MEETING, 'resend_emails')

    @postonly
    def resend_emails(self, REQUEST):
        """ """
        uids = REQUEST.form.get('uids', [])
        assert isinstance(uids, list)
        subscriptions = self.getSubscriptions()
        email_sender = self.getMeeting().getEmailSender()
        for uid in uids:
            signup = subscriptions._signups.get(uid)
            if signup:
                email_sender.send_signup_accepted_email(
                    signup, resend=not self.check_survey_response(uid))
            else:
                subscription = subscriptions._account_subscriptions.get(uid)
                email_sender.send_account_subscription_accepted_email(
                    subscription, resend=not self.check_survey_response(uid))
            self.setSessionInfoTrans(
                'Confirmation emails sent to %s participants' % len(uids))

        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def _get_attendees(self):
        """ """
        meeting = self.getMeeting()
        attendees = {}
        for uid in meeting.users_with_local_role(WAITING_ROLE):
            attendees[uid] = {'role': WAITING_ROLE}
        for uid in meeting.users_with_local_role(PARTICIPANT_ROLE):
            attendees[uid] = {'role': PARTICIPANT_ROLE}
        for uid in meeting.users_with_local_role(ADMINISTRATOR_ROLE):
            attendees[uid] = {'role': ADMINISTRATOR_ROLE}
        subscriptions = self.getSubscriptions()
        for uid in attendees.keys():
            if subscriptions._is_signup(uid):
                attendee = subscriptions.getSignup(uid)
            else:
                attendee = subscriptions.getAccountSubscription(uid)
            attendees[uid]['country'] = getattr(
                attendee, 'country', '-') or '-'
            if getattr(attendee, 'reimbursed', False):
                attendees[uid]['reimbursed'] = 'Yes'
            else:
                attendees[uid]['reimbursed'] = 'No'
            try:
                attendees[uid]['saved_by'] = self.getAuthenticationTool()\
                    .name_from_userid(attendee.saved_by)
            except AttributeError:
                attendees[uid]['saved_by'] = ''
            try:
                attendees[uid]['justification'] = attendee.justification
            except AttributeError:
                attendees[uid]['justification'] = ''
        return attendees

    def getAttendees(self, sort_on=''):
        """ """
        if not self.checkPermissionParticipateInMeeting():
            raise Unauthorized
        attendees = self._get_attendees()

        if sort_on == 'o':
            key = lambda x: self.getAttendeeInfo(x)['organization'].lower()
        elif sort_on == 'name':
            key = lambda x: self.getAttendeeInfo(x)['name'].lower()
        elif sort_on == 'email':
            key = lambda x: self.getAttendeeInfo(x)['email'].lower()
        elif sort_on == 'uid':
            key = lambda x: x.lower()
        elif sort_on == 'role':
            key = lambda x: attendees[x]['role'].lower()
        elif sort_on == 'country':
            key = lambda x: attendees[x]['country']
        elif sort_on == 'reimbursed':
            key = lambda x: attendees[x]['reimbursed']
        elif sort_on == 'survey_answered':
            key = lambda x: self.check_survey_response(x)
        else:
            key = None

        attendee_uids = attendees.keys()

        if key is not None:
            attendee_uids.sort(key=key)

        return attendee_uids

    security.declareProtected(view, 'check_survey_response')

    def check_survey_response(self, uid):
        """ """
        if not self.getMeeting().survey_required:
            return
        survey = self.get_survey()
        if survey:
            for answer in survey.objectValues('Naaya Survey Answer'):
                if answer.respondent in [uid, 'signup:'+uid]:
                    return True
        return False

    security.declareProtected(view, 'getAttendeeInfo')

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
        attendee = self._get_attendees()[uid]
        role = attendee['role']
        country = attendee['country']
        reimbursed = attendee['reimbursed']
        saved_by = attendee['saved_by']
        justification = attendee['justification']
        ret = {'uid': uid, 'name': name, 'email': email,
               'organization': organization, 'phone': phone, 'role': role,
               'country': country, 'reimbursed': reimbursed,
               'saved_by': saved_by, 'justification': justification}
        for k, v in ret.items():
            if not isinstance(v, basestring):
                ret[k] = u''
        return ret

    def setAttendeeInfo(self, ids, prop, val):
        """ """
        if not self.checkPermissionParticipateInMeeting():
            raise Unauthorized
        subscriptions = self.getSubscriptions()
        for attendee_id in ids:
            user = subscriptions.getSignup(attendee_id)
            if user is None:
                user = subscriptions.getAccountSubscription(attendee_id)
            setattr(user, prop, val)

    security.declareProtected(view, 'getParticipantRole')

    def getParticipantRole(self):
        """ """
        return PARTICIPANT_ROLE

    def index_html(self, REQUEST):
        """ """
        if not self.checkPermissionParticipateInMeeting():
            raise Unauthorized
        return self.getFormsTool().getContent(
            {'here': self},
            'naaya.content.meeting.participants_index')

    security.declareProtected(view, 'pickrole_html')

    def pickrole_html(self, REQUEST):
        """ """
        sources = self.getAuthenticationTool().getSources()
        return self.getFormsTool().getContent(
            {'here': self, 'sources': sources},
            'naaya.content.meeting.participants_pickrole')

    def participants_table(self, form_name, input_name):
        """ """
        if not self.checkPermissionParticipateInMeeting():
            raise Unauthorized
        return self.getFormsTool().getContent(
            {'here': self,
             'form_name': form_name,
             'input_name': input_name},
            'naaya.content.meeting.participants_table')

    security.declareProtected(view, 'download')

    def download(self, REQUEST=None, RESPONSE=None):
        """exports the participants listing in an excel file"""
        assert self.rstk.we_provide('Excel export')

        header = ['Name', 'User ID', 'Email', 'Organisation',
                  'Represented country', 'Reimbursed participation', 'Phone',
                  'Status', 'Last modified by',
                  'Reason for modification (when saved by an administrator)']
        meeting = self.getMeeting()
        survey = self.get_survey()
        if meeting.survey_required and survey:
            survey_questions = []
            for question in self.get_survey_questions():
                survey_question = getattr(survey, question[0])
                if survey_question.meta_type == 'Naaya Radio Matrix Widget':
                    survey_questions.extend(survey_question.rows)
                else:
                    survey_questions.append(question[1])
            header.extend(survey_questions)
        rows = []
        participants = self.getAttendees()
        for participant in participants:
            part_info = self.getAttendeeInfo(participant)
            participant_info = [
                part_info['name'], part_info['uid'], part_info['email'],
                part_info['organization'],
                country_from_country_code.get(part_info['country'], ''),
                part_info['reimbursed'], part_info['phone'], part_info['role'],
                part_info['saved_by'], part_info['justification']]
            if meeting.survey_required and survey:
                survey_answers = []
                for question in self.get_survey_questions():
                    survey_question = getattr(survey, question[0])
                    survey_answer = self.get_survey_answer(part_info['uid'],
                                                           question[0])
                    if survey_answer is None:
                        survey_answer = '-'
                    if isinstance(survey_answer, basestring):
                        survey_answers.append(survey_answer)
                    else:
                        survey_answers.extend(survey_answer)
                participant_info.extend(survey_answers)
            rows.append(participant_info)

        filename = '%s_%s_%s.xls' % (self.getMeeting().getId(), self.id,
                                     datetime.now().strftime(
                                     "%Y-%m-%d_%H-%M-%S"))
        RESPONSE.setHeader('Content-Type', 'application/vnd.ms-excel')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s'
                           % filename)
        return generate_excel(header, rows)

    security.declareProtected(view, 'download_webex')

    def download_webex(self, REQUEST=None, RESPONSE=None):
        """exports the participants listing in a Webex-compatible CSV file"""

        # This will be refactored to export to Skype, Webex will be shut
        # down. Right now this method is not used.

        header = ['UUID', 'Name', 'Email', 'Company', 'JobTitle', 'URL',
                  'OffCntry', 'OffLocal', 'CellCntry', 'CellLocal', 'FaxCntry',
                  'FaxLocal', 'Address1', 'Address2', 'City', 'State/Province',
                  'Zip/Postal', 'Country', 'Time Zone', 'Language', 'Locale',
                  'UserName', 'Notes']
        rows = []
        participants = self.getAttendees()
        for participant in participants:
            part_info = self.getAttendeeInfo(participant)
            participant_info = [
                part_info['uid'], part_info['name'], part_info['email'],
                part_info['organization'], part_info['role'],
                '', part_info['phone'], '', '', '', '', '', '', '', '', '', '',
                country_from_country_code.get(part_info['country'], ''),
                '', '', '', part_info['uid'], '']
            rows.append(participant_info)

        filename = '%s_%s_%s.csv' % (self.getMeeting().getId(), self.id,
                                     datetime.now().strftime(
                                     "%Y-%m-%d_%H-%M-%S"))
        RESPONSE.setHeader('Content-Type', 'text/csv')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename=%s'
                           % filename)
        return generate_csv(header, rows)

InitializeClass(Participants)

NaayaPageTemplateFile('zpt/participants_index', globals(),
                      'naaya.content.meeting.participants_index')
NaayaPageTemplateFile('zpt/participants_pickrole', globals(),
                      'naaya.content.meeting.participants_pickrole')
NaayaPageTemplateFile('zpt/participants_table', globals(),
                      'naaya.content.meeting.participants_table')
