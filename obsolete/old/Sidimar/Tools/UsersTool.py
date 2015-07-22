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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania

import time

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view, manage_users
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Naaya imports
from Products.NaayaCore.AuthenticationTool.AuthenticationTool import AuthenticationTool
from Products.NaayaCore.managers.utils import utils

#product imports
from Products.Sidimar.constants import *
from Products.Sidimar.Tools.SidUser import FakeUser
from Products.Sidimar.Tools.SidUser import SidUser
from Products.Sidimar.Tools.Logger import LogInfo


def manage_addUsersTool(self, REQUEST=None):
    """ """
    ob = UsersTool(USERSTOOL_ID, USERSTOOL_TITLE)
    self._setObject(USERSTOOL_ID, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)


class UsersTool(AuthenticationTool):
    """ """

    meta_type = USERSTOOL_METATYPE
    icon = 'misc_/NaayaCore/AuthenticationTool.gif'


    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.fake_users = []
        AuthenticationTool.__dict__['__init__'](self, id, title)

    security.declarePrivate('_addFakeUser')
    def _addFakeUser(self, id, firstname, lastname, job, organisation, country, 
                street, street_number, zip, city, region, phone, mail, note, download, privacy):
        """ create a fake user """
        u = FakeUser(id, firstname, lastname, job, organisation, country, 
                street, street_number, zip, city, region, phone, mail, note, download, privacy)
        self.fake_users.append(u)
        self._p_changed = 1

    security.declareProtected(manage_users, 'addFakeUser')
    def addFakeUser(self, id, firstname='', lastname='', job='', organisation='', country='', street='', 
        street_number='', zip='', city='', region='', phone='', mail='', note='', download=0, privacy=0):
        """ wrapper """
        if not firstname:
            raise Exception, ERROR100
        if not lastname:
            raise Exception, ERROR101
        if not country:
            raise Exception, ERROR102
        if not street:
            raise Exception, ERROR103
        if not street_number:
            raise Exception, ERROR104
        if not zip:
            raise Exception, ERROR105
        if not city:
            raise Exception, ERROR106
        if not region:
            raise Exception, ERROR107
        if not phone:
            raise Exception, ERROR108
        if not mail:
            raise Exception, ERROR109
        if not int(download):
            raise Exception, ERROR110
        if not int(privacy):
            raise Exception, ERROR111
        self._addFakeUser(id, firstname, lastname, job, organisation, country, 
                street, street_number, zip, city, region, phone, mail, note, download, privacy)

    security.declareProtected(manage_users, 'add_user')
    def add_user(self, name='', password='', roles=[], firstname='', lastname='', job='', organisation='', country='', 
                street='', street_number='', zip='', city='', region='', phone='', mail=''):
        """ add user """
        if not firstname:
            raise Exception, ERROR100
        if not lastname:
            raise Exception, ERROR101
        if not country:
            raise Exception, ERROR102
        if not street:
            raise Exception, ERROR103
        if not street_number:
            raise Exception, ERROR104
        if not zip:
            raise Exception, ERROR105
        if not city:
            raise Exception, ERROR106
        if not region:
            raise Exception, ERROR107
        if not phone:
            raise Exception, ERROR108
        if not mail:
            raise Exception, ERROR109
        if not name:
            raise Exception, ERROR121
        if not password:
            raise Exception, ERROR122
        if self.getUser(name) or (self._emergency_user and name == self._emergency_user.getUserName()):
            raise Exception, ERROR119
        #convert data
        roles = self.utConvertToList(roles)
        self._addUser(name, password, roles, [], firstname, lastname, job, organisation, country, 
                street, street_number, zip, city, region, phone, mail, note='', download=1, privacy=1)

    security.declarePrivate('_addFakeUser')
    def _delFakeUser(self, id):
        [self.fake_users.remove(u) for u in self.fake_users if u.id == id ]
        self._p_changed = 1

    security.declarePublic('getFakeUsers')
    def getFakeUsers(self):
        """ """
        return self.fake_users

    security.declareProtected(manage_users, 'getFakeUser')
    def getFakeUser(self, id):
        """ """
        return [u for u in self.fake_users if u.id == id]

    security.declarePrivate('_doAddUser')
    def _addUser(self, name, password, roles, domains, firstname, lastname, job, organisation, country, 
                street, street_number, zip, city, region, phone, mail, note, download, privacy):
        """Create a new user. The 'password' will be the original input password, unencrypted. """
        self.data[name] = SidUser(name, password, roles, domains, firstname, lastname, job, organisation, country, 
                street, street_number, zip, city, region, phone, mail, note, download, privacy)
        self._p_changed = 1

    security.declarePrivate('_doChangeUser')
    def _doChangeUser(self, name, password, roles, domains, firstname, lastname, job, organisation, country, 
                street, street_number, zip, city, region, phone, mail, lastupdated):
        """Modify an existing user. The 'password' will be the
           original input password, unencrypted. The implementation of this
           method is responsible for performing any needed encryption."""

        user=self.data[name]
        if password is not None:
            if self.encrypt_passwords and not self._isPasswordEncrypted(password):
                assword = self._encryptPassword(password)
            user.__ = password
        user.roles = roles
        user.domains = domains
        user.firstname = firstname
        user.lastname = lastname
        user.job = job
        user.organisation = organisation
        user.country = country
        user.street = street
        user.street_number = street_number
        user.zip = zip
        user.city = city
        user.region = region
        user.phone = phone
        user.email = mail
        user.lastupdated = lastupdated
        self._p_changed = 1

    security.declarePrivate('retrieve_password')
    def retrieve_password(self, email):
        """ retrieve account information """
        if not email:
            raise Exception, ERROR109
        pwd = fname = lname = account = None
        for n in self.getUserNames():
            us = self.getUser(n)
            if email.strip() == us.email:
                pwd = self.getUserPassword(us)
                fname = self.getUserFirstName(us)
                lname = self.getUserLastName(us)
                account = self.getUserAccount(us)
                break
        if pwd is None:
            raise Exception, ERROR112
        return (account, pwd, fname, lname)

    security.declarePrivate('change_user_preferences')
    def change_user_preferences(self, name='', roles='', firstname='', lastname='', job='', organisation='', 
            country='', street='', street_number='', zip='', city='', region='', phone='', mail=''):
        """ change user preferences """
        if not firstname:
            raise Exception, ERROR100
        if not lastname:
            raise Exception, ERROR101
        if not country:
            raise Exception, ERROR102
        if not street:
            raise Exception, ERROR103
        if not street_number:
            raise Exception, ERROR104
        if not zip:
            raise Exception, ERROR105
        if not city:
            raise Exception, ERROR106
        if not city:
            raise Exception, ERROR107
        if not phone:
            raise Exception, ERROR108
        if not mail:
            raise Exception, ERROR109
        user_ob = self.getUser(name)
        roles = self.utConvertToList(roles)
        lastupdated = time.strftime('%d %b %Y %H:%M:%S')
        self._doChangeUser(name, self.getUserPassword(user_ob), roles, [], firstname, lastname, 
            job, organisation, country, street, street_number, zip, city, region, phone, mail, lastupdated)

    security.declareProtected(manage_users, 'user_activate')
    def user_activate(self, username='', passwd='', roles=[], id=''):
        """ activate an user """
        ut = utils()
        roles = ut.utConvertToList(roles)
        if not id:
            raise Exception, ERROR120
        if not username:
            raise Exception, ERROR121
        if not passwd:
            raise Exception, ERROR122
        if self.getUser(username) or (self._emergency_user and
                                  username == self._emergency_user.getUserName()):
            raise Exception, ERROR119
        try:
            u = self.getFakeUser(id)[0]
        except:
            raise Exception, 'Invalid information'
        self._addUser(username, passwd, roles, '', u.firstname, u.lastname, u.job, u.organisation, u.country, 
                u.street, u.street_number, u.zip, u.city, u.region, u.phone, u.mail, u.note, u.download, u.privacy)
        #delete registration
        self._delFakeUser(id)

    def user_deactivate(self, ids=[]):
        ut = utils()
        for id in ids:
            user=self.data[id]
            uid = ut.utGenRandomId(6)
            self.addFakeUser(uid, user.firstname, user.lastname, user.job, user.organisation, user.country, 
                user.street, user.street_number, user.zip, user.city, user.region, user.phone, user.email, note='', 
                download=1, privacy=1)
        self.manage_delUsers(ids)

    security.declarePrivate('change_user_password')
    def change_user_password(self, user='', opass='', npass='', cpass=''):
        """ change user password """
        if not opass:
            raise Exception, ERROR115
        if (npass or cpass) and (npass != cpass):
            raise Exception, ERROR117
        if npass == cpass == '':
            raise Exception, ERROR118
        user_ob = self.getUser(user)
        if opass != self.getUserPassword(user_ob):
            raise Exception, ERROR116
        lastupdated = time.strftime('%d %b %Y %H:%M:%S')
        roles = self.getUserRoles(user_ob)
        firstname = self.getUserFirstName(user_ob)
        lastname = self.getUserLastName(user_ob)
        mail = self.getUserEmail(user_ob)
        job = self.getUserJob(user_ob)
        organisation = self.getUserOrganisation(user_ob)
        country = self.getUserCountry(user_ob)
        street = self.getUserStreet(user_ob)
        street_number = self.getUserStreetNumber(user_ob)
        zip = self.getUserZip(user_ob)
        city = self.getUserCity(user_ob)
        region = self.getUserRegion(user_ob)
        phone = self.getUserPhone(user_ob)
        self._doChangeUser(user, npass, roles, [], firstname, lastname, job, organisation, country, 
                street, street_number, zip, city, region, phone, mail, lastupdated)
        self.credentialsChanged(user, user, npass)

    security.declarePrivate('change_log')
    def change_log(self, user=None, log=None):
        """ append in user's log """
        user.logs.append(log)
        self._p_changed = 1

    security.declareProtected(manage_users, 'get_logs')
    def get_logs(self, user=None):
        """ return the user's logs """
        return user.logs

    security.declareProtected(manage_users, 'get_log_info')
    def get_log_info(self, log=None):
        """ get the log info """
        return log.log

    security.declareProtected(manage_users, 'get_log_date')
    def get_log_date(self, log=None):
        """ get the log date """
        return log.date

    security.declareProtected(manage_users, 'get_downloads')
    def get_downloads(self, user=None):
        """ return the user's downloads number """
        return user.downloads

    security.declarePrivate('change_downloads')
    def change_downloads(self, user, region, campaign, year, monitor):
        """ """
        for d in user.downloads:
            if d.region == region and d.campaign == campaign and d.year == year and d.monitor == monitor:
                d.downloads += 1
                user._p_changed = 1
                return
        l = LogInfo(region, campaign, year, 1, monitor)
        user.downloads.append(l)
        user._p_changed = 1

    security.declareProtected(manage_users, 'get_log_region')
    def get_log_region(self, down=None):
        """ get the region from the log """
        return down.region

    security.declareProtected(manage_users, 'get_log_campaign')
    def get_log_campaign(self, down=None):
        """ get the region from the log """
        return down.campaign

    security.declareProtected(manage_users, 'get_log_year')
    def get_log_year(self, down=None):
        """ get the region from the log """
        return down.year

    security.declareProtected(manage_users, 'get_log_monitor')
    def get_log_monitor(self, down=None):
        """ get the region from the log """
        return down.monitor

    security.declareProtected(manage_users, 'get_log_downloads')
    def get_log_downloads(self, down=None):
        """ get the region from the log """
        return down.downloads

    security.declareProtected(manage_users, 'del_pending_users')
    def del_pending_users(self, ids=[]):
        """ delete a list of pending users """
        ut = utils()
        ids = ut.utConvertToList(ids)
        [self._delFakeUser(id) for id in ids]

    def getUserJob(self, user):
        return user.job

    def getUserOrganisation(self, user):
        return user.organisation

    def getUserCountry(self, user):
        return user.country

    def getUserStreet(self, user):
        return user.street

    def getUserStreetNumber(self, user):
        return user.street_number

    def getUserZip(self, user):
        return user.zip

    def getUserCity(self, user):
        return user.zip

    def getUserRegion(self, user):
        return user.region

    def getUserPhone(self, user):
        return user.phone

    def getUserNote(self, user):
        return user.note

    manage_users_html = PageTemplateFile('zpt/manage_active', globals())

    manage_pending_html = PageTemplateFile('zpt/manage_pending', globals())
    manage_puser_html = PageTemplateFile('zpt/manage_pendinguser', globals())

    pending_html = PageTemplateFile('zpt/pending', globals())
    userpending_html = PageTemplateFile('zpt/pendinguser', globals())

    manage_addUser_html = PageTemplateFile('zpt/manage_adduser', globals())
    adduser_html = PageTemplateFile('zpt/adduser', globals())

    manage_editUser_html = PageTemplateFile('zpt/manage_edituser', globals())
    edituser_html = PageTemplateFile('zpt/edituser', globals())

    manage_viewuser_html = PageTemplateFile('zpt/manage_overview', globals())
    viewuser_html = PageTemplateFile('zpt/overview', globals())

InitializeClass(UsersTool)
