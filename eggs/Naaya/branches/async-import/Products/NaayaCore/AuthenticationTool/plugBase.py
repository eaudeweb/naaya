from zope.event import notify
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass

from Products.NaayaCore.constants import *

class PlugBase(SimpleItem):
    """ """

    manage_options = (
        SimpleItem.manage_options
        )

    def __init__(self, id, source_obj, title):
        """ """
        super(PlugBase, self).__init__(id)
        self.id = id
        self.obj_path = source_obj.absolute_url(1)
        self.title = title

    def getUserFolder(self):
        #return the user folder object
        l_obj = self.unrestrictedTraverse('/' + self.obj_path, None)
        if l_obj is None: return None
        else: return l_obj

    def getLocalRoles(self, p_local_roles):
        #returns a list of local roles
        return [role for role in p_local_roles
                        if role not in ['Owner', 'Authenticated']]

    def getUsersRoles(self, p_user_folder, p_meta_types=None):
        #returns a structure with user roles by objects
        _memo = {}
        def get_source(user):
            """ memoize for getUserSource """
            if user not in _memo:
                _memo[user] = self.getUserSource(user)
            return _memo[user]

        if p_meta_types is None: p_meta_types = self.get_containers_metatypes()
        l_users_roles = {}
        l_folders = self.getCatalogedObjects(meta_type=p_meta_types, has_local_role=1)
        l_folders.append(self.getSite())
        for l_item in l_folders:
            for l_roles_tuple in l_item.get_local_roles():
                l_local_roles = self.getLocalRoles(l_roles_tuple[1])
                user = l_roles_tuple[0]
                if get_source(user) == self.title and len(l_local_roles)>0:
                    if l_users_roles.has_key(str(user)):
                        l_users_roles[str(user)].append((l_local_roles, l_item.absolute_url(1)))
                    else:
                        l_users_roles[str(user)] = [(l_local_roles, l_item.absolute_url(1))]
        return l_users_roles

    def revokeUserRoles(self, user, location, REQUEST=None):
        """ """
        if location == '' or location == '/':
            location_ob = self.getSite()
        else:
            location_ob = self.utGetObject(location)
        if location_ob is None:
            raise ValueError("Invalid location")
        auth_tool = self.getAuthenticationTool()
        history = auth_tool.getLocationUserRoles(user, location)
        location_ob.manage_delLocalRoles([user])

        if REQUEST is not None:
            from Products.NaayaCore.AuthenticationTool.events import RoleAssignmentEvent
            manager_id = REQUEST.AUTHENTICATED_USER.getUserName()
            notify(RoleAssignmentEvent(location_ob, manager_id, user, [],
                                       history))
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def addUserRoles(self, name=[], roles=[], location='', user_location='',
                     send_mail='', REQUEST=None):
        """ """
        def on_error(error_str):
            if REQUEST is not None:
                self.setSessionErrorsTrans(error_str)
                return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
            else:
                raise ValueError(error_str)

        if not isinstance(name, list):
            if isinstance(name, str):
                name = [name]
            else:
                return on_error('Username selection error')

        if name == []:
            return on_error('No user selected')
        if roles == []:
            return on_error('No roles selected')

        site = self.getSite()
        auth_tool = site.getAuthenticationTool()
        #process form values
        if location == "/" or location == '':
            loc, location_ob = 'all', site
        else:
            loc, location_ob = 'other', self.utGetObject(location)
        if location_ob is None:
            return on_error('Invalid location path')
        #assing roles
        if not isinstance(roles, list):
            roles = [roles]
        history = {}
        for n in name:
            history[n] = auth_tool.getLocationUserRoles(n, location)
            location_ob.manage_setLocalRoles(n, roles)
            if send_mail:
                try:
                    email = auth_tool.getUsersEmails([n])[0]
                    fullname = auth_tool.getUsersFullNames([n])[0]
                    site.sendAccountModifiedEmail(email, roles, loc,
                                                  location_ob, username=n)
                except:
                    pass
            try:
                self.setUserLocation(n, user_location)
            except:
                pass
        if REQUEST is not None:
            from Products.NaayaCore.AuthenticationTool.events import RoleAssignmentEvent
            manager_id = REQUEST.AUTHENTICATED_USER.getUserName()
            for n in name:
                notify(RoleAssignmentEvent(location_ob, manager_id, n, roles,
                                           history[n]))
            self.setSessionInfoTrans("Role(s) successfully assigned")
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def removeUser(self, name):
        acl = self.getUserFolder()
        roles = self.getUsersRoles(acl)
        if name in roles.keys():
            roles = [(name + '||' + x[1]).encode('utf-8') for x in roles[name]]
            self.revokeUserRoles(roles)
            return True

    def has_user(self, user_id):
        user_ob = self.getUserFolder().getUser(user_id)
        return user_ob is not None

InitializeClass(PlugBase)
