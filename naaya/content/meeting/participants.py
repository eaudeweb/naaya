#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import change_permissions, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from persistent.dict import PersistentDict

#Naaya imports
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.content.meeting import PARTICIPANT_ROLE
from utils import schemaHasParam, getUserFullName, getUserEmail, getUserOrganisation, getUserPhoneNumber

class Participants(SimpleItem):
    security = ClassSecurityInfo()

    title = "Meeting participants"

    def __init__(self, id):
        """ """
        self.id = id
        self.attendees = PersistentDict()
        #self.uids = PersistentList()
        #self.administrator_uid = None

    def findUsers(self, search_param, search_term):
        """ """
        def userMatched(uid, cn):
            if search_param == 'uid':
                return search_term in uid
            if search_param == 'cn':
                return search_term in cn
            return False

        auth_tool = self.getAuthenticationTool()
        ret = []

        for user in auth_tool.getUsers():
            uid = auth_tool.getUserAccount(user)
            cn = auth_tool.getUserFullName(user)
            info = 'Local user'
            
            if userMatched(uid, cn):
                ret.append({'uid': uid, 'cn': cn, 'organisation': '', 'info': info})

        for source in auth_tool.getSources():
            acl_folder = source.getUserFolder()
            if schemaHasParam(acl_folder, search_param): 
                users = acl_folder.findUser(search_param=search_param, search_term=search_term)
                for user in users:
                    uid = user.get('uid', '')
                    cn = user.get('cn', '')
                    organisation = user.get('o', '')
                    info = user.get('dn', '')
                    ret.append({'uid': uid, 'cn': cn, 'organisation': organisation, 'info': info})

        return ret

    def findUsersWithRole(self, search_role):
        """ """
        auth_tool = self.getAuthenticationTool()
        ret = []

        for source in auth_tool.getSources():
            acl_folder = source.getUserFolder()
            users = source.getUsersByRole(acl_folder, [(search_role, None)])
            for user in users:
                uid = user.get('uid', '')
                if isinstance(uid, list):
                    uid = uid[0]
                cn = user.get('cn', '')
                if isinstance(cn, list):
                    cn = cn[0]
                organisation = user.get('o', '')
                if isinstance(organisation, list):
                    organisation = organisation[0]
                info = user.get('dn', '')
                ret.append({'uid': uid, 'cn': cn, 'organisation': organisation, 'info': info})

        return ret

    def _set_attendee(self, uid, role):
        if uid in self.attendees and self.attendees[uid] == role:
            return

        assert role in [PARTICIPANT_ROLE, 'Administrator']

        self.aq_parent.manage_setLocalRoles(uid, [role])
        self.attendees[uid] = role

    def setAttendees(self, role, REQUEST):
        """ """
        uids = REQUEST.form.get('uids', [])
        assert isinstance(uids, list)
        for uid in uids:
            self._set_attendee(uid, role)
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def _del_attendee(self, uid):
        self.aq_parent.manage_delLocalRoles([uid])
        del self.attendees[uid]

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
        elif 'send_email' in REQUEST.form:
            if 'uids' in REQUEST.form:
                return self.aq_parent.newsletter_html(REQUEST.form['uids'])

        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def getAttendees(self, sort_on=''):
        """ """
        site = self.getSite()
        key = None
        if sort_on == 'o':
            key = lambda x: getUserOrganisation(site, x)
        elif sort_on == 'name':
            key = lambda x: getUserFullName(site, x)
        elif sort_on == 'email':
            key = lambda x: getUserEmail(site, x)
        elif sort_on == 'uid':
            key = lambda x: x
        elif sort_on == 'role':
            key = lambda x: self.attendees[x]

        if key is None:
            return self.attendees.keys()
        return sorted(self.attendees.keys(), key=key)

    def getAttendeeInfo(self, uid):
        """ """
        site = self.getSite()
        name = getUserFullName(site, uid)
        email = getUserEmail(site, uid)
        organisation = getUserOrganisation(site, uid)
        phone = getUserPhoneNumber(site, uid)
        role = self.attendees[uid]
        return {'uid': uid, 'name': name, 'email': email, 'organisation': organisation, 'phone': phone, 'role': role}

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
        return self.getFormsTool().getContent({'here': self}, 'meeting_participants')

    security.declareProtected(view, 'pickrole_html')
    def pickrole_html(self, REQUEST):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'meeting_participants_pickrole')

NaayaPageTemplateFile('zpt/participants_index', globals(), 'meeting_participants')
NaayaPageTemplateFile('zpt/participants_pickrole', globals(), 'meeting_participants_pickrole')
