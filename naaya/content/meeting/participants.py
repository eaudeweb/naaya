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
from utils import getUserFullName, getUserEmail, getUserOrganisation, getUserPhoneNumber

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

        def schema_has_param(acl_folder, param):
            for item in acl_folder.getLDAPSchema():
                if item[0] == param:
                    return True
            return False

        auth_tool = self.getAuthenticationTool()
        ret = []

        for user in auth_tool.getUsers():
            uid = auth_tool.getUserAccount(user)
            cn = auth_tool.getUserFullName(user)
            info = 'Local user'
            
            if userMatched(uid, cn):
                ret.append({'uid': uid, 'cn': cn, 'info': info})

        for source in auth_tool.getSources():
            acl_folder = source.getUserFolder()
            if schema_has_param(acl_folder, search_param): 
                users = acl_folder.findUser(search_param=search_param, search_term=search_term)
                for user in users:
                    uid = user['uid']
                    cn = user['cn']
                    info = user['dn']
                    ret.append({'uid': uid, 'cn': cn, 'info': info})

        return ret

    def findUsersWithRole(self, search_role):
        """ """
        auth_tool = self.getAuthenticationTool()
        ret = []

        for source in auth_tool.getSources():
            acl_folder = source.getUserFolder()
            users = source.getUsersByRole(acl_folder, [(search_role, None)])
            for user in users:
                uid = user['uid']
                if isinstance(uid, list):
                    uid = uid[0]
                cn = user['cn']
                if isinstance(cn, list):
                    cn = cn[0]
                info = user['dn']
                ret.append({'uid': uid, 'cn': cn, 'info': info})

        return ret

    def _set_attendee(self, uid, role):
        if uid in self.attendees and self.attendees[uid] == role:
            return

        if role == 'participant':
            zope_role = PARTICIPANT_ROLE
        elif role == 'administrator':
            zope_role = 'Administrator'
        else:
            return

        self.aq_parent.manage_setLocalRoles(uid, [zope_role])
        self.attendees[uid] = role

    def setAttendees(self, role, REQUEST):
        """ """
        uids = REQUEST.form['uids']
        assert isinstance(uids, list)
        for uid in uids:
            self._set_attendee(uid, role)
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def _del_attendee(self, uid):
        self.aq_parent.manage_delLocalRoles([uid])
        del self.attendees[uid]

    def delAttendees(self, REQUEST):
        """ """
        uids = REQUEST.form['uids']
        assert isinstance(uids, list)
        for uid in uids:
            self._del_attendee(uid)
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def onAttendees(self, REQUEST):
        """ """
        if 'del_attendees' in REQUEST.form:
            return self.delAttendees(REQUEST)
        elif 'set_administrators' in REQUEST.form:
            return self.setAttendees('administrator', REQUEST)
        elif 'set_participants' in REQUEST.form:
            return self.setAttendees('participant', REQUEST)
        elif 'send_email' in REQUEST.form:
            assert 'uids' in REQUEST.form
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
