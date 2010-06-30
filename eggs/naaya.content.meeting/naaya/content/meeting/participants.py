#Python imports

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import change_permissions, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from persistent.list import PersistentList

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
        self.uids = PersistentList()
        self.administrator_uid = None

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

    def _add_user(self, uid):
        if uid in self.uids:
            return

        self.aq_parent.manage_setLocalRoles(uid, [PARTICIPANT_ROLE])
        self.uids.append(uid)

    def addUsers(self, REQUEST):
        """ """
        uids = REQUEST.form['uids']
        assert isinstance(uids, list)
        for uid in uids:
            self._add_user(uid)
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def _remove_user(self, uid):
        self.aq_parent.manage_delLocalRoles([uid])
        self.uids.remove(uid)

    def removeUsers(self, REQUEST):
        """ """
        uids = REQUEST.form['uids']
        assert isinstance(uids, list)
        for uid in uids:
            self._remove_user(uid)
        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(change_permissions, 'setAdministrator')
    def setAdministrator(self, uid, REQUEST=None):
        """ """
        old_admin = self.administrator_uid
        if uid:
            self.aq_parent.manage_delLocalRoles([uid])
            self.aq_parent.manage_setLocalRoles(uid, ['Administrator'])
            self.administrator_uid = uid
        else:
            self.administrator_uid = None

        if old_admin:
            self.aq_parent.manage_delLocalRoles([old_admin])
            if old_admin in self.uids:
                self.aq_parent.manage_setLocalRoles(old_admin, [PARTICIPANT_ROLE])

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url())

    def getParticipants(self, sort_on=''):
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

        if key is None:
            return self.uids
        return sorted(self.uids, key=key)

    def getParticipantInfo(self, uid):
        """ """
        site = self.getSite()
        name = getUserFullName(site, uid)
        email = getUserEmail(site, uid)
        organisation = getUserOrganisation(site, uid)
        phone = getUserPhoneNumber(site, uid)
        return {'uid': uid, 'name': name, 'email': email, 'organisation': organisation, 'phone': phone}

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
