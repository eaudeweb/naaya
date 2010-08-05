# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

#Python imports
from urlparse import urlparse

#Zope imports
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from DateTime import DateTime

#Product imports
from Products.NaayaBase.NyItem import NyItem
from constants import *

def getSiteDomainName(site):
    portal_url = site.portal_url
    if portal_url:
        if not portal_url.startswith('http://'):
            portal_url = 'http://' + portal_url
        return urlparse(portal_url)[1]
    else:
        return site.REQUEST.SERVER_NAME

manage_addNotificationList_html = PageTemplateFile('zpt/notificationList_add', globals())
def manage_addNotificationList(self, REQUEST=None):
    """ """
    ob = NotificationList()
    id = ob.id
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.checkNotificationListPermissions()

    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return ob

class NotificationList(NyItem):
    """ """

    meta_type = METATYPE_NOTIFICATION_LIST

    manage_options = (
                        { 'label' : 'Contents', 'action' : 'manage_main' },
                        { 'label' : 'View', 'action' : 'index_html' },
                        { 'label' : 'Admin', 'action' : 'admin_html' },
                     ) + NyItem.manage_options

    security = ClassSecurityInfo()

    def __init__(self, id=NOTIFICATION_LIST_DEFAULT_ID, title="Notification list"):
        NyItem.__init__(self)

        self.id = id
        self.title = title
        self.users = []

    def checkNotificationListPermissions(self):
        admin_permissions = self.permissionsOfRole('Administrator')
        site = self.getSite()
        if PERMISSION_MANAGE_NOTIFICATION_LIST not in admin_permissions:
            site.manage_permission(PERMISSION_MANAGE_NOTIFICATION_LIST , ('Administrator', ), acquire=1)

    security.declarePrivate('get_user_info')
    def get_user_info(self, user_name, ldap_user_data=None):
        auth_tool = self.getAuthenticationTool()
        parent_acl_users = self.restrictedTraverse('/').acl_users

        user_obj = auth_tool.getUser(user_name)
        if user_obj is not None:
            return {
                'user_name': user_name,
                'full_name': '%s %s' % (
                        auth_tool.getUserFirstName(user_obj),
                        auth_tool.getUserLastName(user_obj)),
                'email': auth_tool.getUserEmail(user_obj),
            }

        # The user is not in Naaya's acl_users, so let's look deeper
        if parent_acl_users.meta_type == 'LDAPUserFolder':
            # TODO: what if parent_acl_users is not an LDAPUserFolder?
            # Note: EIONET LDAP data is encoded with latin-1
            if ldap_user_data:
                return {
                    'user_name': ldap_user_data['uid'],
                    'full_name': ldap_user_data['cn'].decode('latin-1'),
                    'email': ldap_user_data.get('mail', ''),
                }
            else:
                ldap_user_data = parent_acl_users.getUserById(user_name)
                if ldap_user_data:
                    return {
                        'user_name': ldap_user_data.uid,
                        'full_name': ldap_user_data.cn, # taken from DAPUserFolder's cache, already utf-8
                        'email': ldap_user_data.mail,
                    }

        # Didn't find the user anywhere; return a placeholder
        return {
            'user_name': user_name,
            'full_name': '[missing user]',
            'email': None,
        }

    security.declareProtected(view, 'get_current_user')
    def get_current_user(self, REQUEST):
        current_user = REQUEST.AUTHENTICATED_USER.getId()
        if current_user is None:
            # this user is the anonymous user
            return None

        user_data = self.get_user_info(current_user)
        is_subscribed = user_data['user_name'] in self.users
        can_admin = self.checkPermission(PERMISSION_MANAGE_NOTIFICATION_LIST)

        return dict(user_data, subscribed=is_subscribed, can_admin=can_admin)

    security.declareProtected(PERMISSION_MANAGE_NOTIFICATION_LIST, 'list_subscribers')
    def list_subscribers(self):
        """ Returns a list of people subscribed to this list """
        output = []
        for user_name in self.users:
            output.append(self.get_user_info(user_name))
        return output

    security.declareProtected(view, 'subscribe_self')
    def subscribe_self(self, REQUEST):
        """ Subscribe the user currently logged in """
        current_user = REQUEST.AUTHENTICATED_USER.getId()
        if current_user:
            self.subscribe_user_list([current_user])

        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(view, 'unsubscribe_self')
    def unsubscribe_self(self, REQUEST):
        """ Unsubscribe the user currently logged in """
        current_user = REQUEST.AUTHENTICATED_USER.getId()
        if current_user:
            self.unsubscribe_user_list([current_user])

        return REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(PERMISSION_MANAGE_NOTIFICATION_LIST, 'subscribe_user_list')
    def subscribe_user_list(self, user_names=[], REQUEST=None):
        """ Subscribe a list of users to this notification list """
        if isinstance(user_names, basestring):
            user_names = [user_names]

        for user_name in user_names:
            if user_name not in self.users:
                self.users.append(user_name)
                self._p_changed = 1

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declareProtected(PERMISSION_MANAGE_NOTIFICATION_LIST, 'unsubscribe_user_list')
    def unsubscribe_user_list(self, user_names=[], REQUEST=None):
        """ Unsubscribe a list of users from this notification list """
        if isinstance(user_names, basestring):
            user_names = [user_names]

        for user_name in user_names:
            if user_name in self.users:
                self.users.remove(user_name)
                self._p_changed = 1

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declareProtected(PERMISSION_MANAGE_NOTIFICATION_LIST, 'get_potential_users')
    def get_potential_users(self, search_string):
        if not search_string:
            # don't return anything if there is no search term
            return []

        search_string = search_string.lower()
        potential_users = {}

        # go through site's acl_users
        parent_acl_users = self.restrictedTraverse('/').acl_users
        if parent_acl_users.meta_type == 'LDAPUserFolder':
            # LDAP search is case-insensitive, but we must
            # search each attribute individually.
            for key in ['uid', 'sn', 'mail', 'givenName', 'cn']:
                for ldap_user in parent_acl_users.searchUsers(**{key: search_string}):
                    if ldap_user['uid'] not in potential_users:
                        potential_users[ldap_user['uid']] = self.get_user_info(ldap_user['uid'], ldap_user_data=ldap_user)

            # TODO: what if parent_acl_users is not an LDAPUserFolder?

        # go through Naaya's acl_users
        for user_name in self.getAuthenticationTool().user_names():
            user = self.get_user_info(user_name)

            if search_string in ' '.join(user.values()).lower():
                potential_users[user['user_name']] = user

        output = []
        for user in potential_users.itervalues():
            if user['user_name'] not in self.users:
                output.append(user)
        return output

    security.declarePrivate('notify_subscribers')
    def notify_subscribers(self, event):
        """ Notify our subscribers that an item has been uploaded """

        upload_user = event['user']
        auth_tool = self.getAuthenticationTool()
        try:
            upload_user_mail = auth_tool.getUserEmail(upload_user)
        except:
            upload_user_mail = ''

        from_address = 'notifications@' + getSiteDomainName(self.getSite())
        upload_time = str(self.utShowFullDateTime(self.utGetTodayDate()))
        container_title = self.getParentNode().title_or_id()

        if event['type'] == 'forum message':
            mail_subject = NOTIFICATION_LIST_MAIL_SUBJECT_TEMPLATE_FORUM_MESSAGE % container_title
            mail_template = NOTIFICATION_LIST_MAIL_BODY_TEMPLATE_FORUM_MESSAGE
            mail_template = mail_template.replace('@@GROUPTITLE@@', container_title)
            mail_template = mail_template.replace('@@ITEMURL@@', event['object'].absolute_url())

        elif event['type'] == 'file upload':
            mail_subject = NOTIFICATION_LIST_MAIL_SUBJECT_TEMPLATE_UPLOAD % container_title
            mail_template = NOTIFICATION_LIST_MAIL_BODY_TEMPLATE_UPLOAD
            mail_template = mail_template.replace('@@ITEM@@', event['object'].title_or_id())
            mail_template = mail_template.replace('@@GROUPTITLE@@', container_title)
            mail_template = mail_template.replace('@@ITEMURL@@', event['object'].absolute_url())

        else:
            raise ValueError('Unknown event type %s' % event['type'])

        mail_template = mail_template.replace('@@USERNAME@@', upload_user.getUserName())
        mail_template = mail_template.replace('@@USEREMAIL@@', upload_user_mail)
        mail_template = mail_template.replace('@@UPLOADTIME@@', upload_time)


        for user in self.list_subscribers():
            if user['email'] is None:
                # this is a broken user object; skip it
                continue

            self.getEmailTool().sendEmail(mail_template, user['email'], from_address, mail_subject)

    security.declareProtected(PERMISSION_MANAGE_NOTIFICATION_LIST, 'manage_main')
    manage_main = PageTemplateFile('zpt/notificationList_manage', globals())

    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/notificationList_index', globals())

    security.declareProtected(PERMISSION_MANAGE_NOTIFICATION_LIST, 'admin_html')
    admin_html = PageTemplateFile('zpt/notificationList_admin', globals())

    security.declareProtected(PERMISSION_MANAGE_NOTIFICATION_LIST, 'user_table_zpt')
    user_table_zpt = PageTemplateFile('zpt/notificationList_userTable', globals())

InitializeClass(NotificationList)
