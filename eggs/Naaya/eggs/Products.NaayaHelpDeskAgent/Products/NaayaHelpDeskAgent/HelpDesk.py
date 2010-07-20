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
# The Original Code is HelpDeskAgent version 1.0.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania for EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Dragos Chirila, Finsiel Romania

#Python imports
import operator
from os.path import join

#Zope imports
import Products
from OFS.Folder import Folder
from Globals import InitializeClass, MessageDialog
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens,view
from Products.ZCatalog.ZCatalog import ZCatalog
from DateTime import DateTime

#Product imports
from Objects import *
from Toolz import *
from Constants import *
import Issue
from EmailSender import EmailSender

manage_addHelpDeskForm = PageTemplateFile('zpt/HelpDesk_addForm', globals())
def manage_addHelpDesk(self, id, title, user_folder,
        mail_server_name='localhost', mail_server_port=25, notify_add='', notify_modify='',
        mail_from_address='IssueTracker@localhost',
        add_issue_email_subject='HelpDesk Agent: new issue posted',
        update_issue_email_subject='HelpDesk Agent: issue modification',
        delete_issue_email_subject='HelpDesk Agent: issue deleted',
        add_issue_comment_email_subject='HelpDesk Agent: new comment to issue posted',
        update_issue_comment_email_subject='HelpDesk Agent: comment modification',
        delete_issue_comment_email_subject='HelpDesk Agent: comment deleted',
        issue_ticket_length=15, security='private', default_priority='1', REQUEST=None):
    """Add a HelpDesk"""
    if title == '':
        title = HELPDESK_DEFAULT_TITLE
    if notify_add:
        notify_add = NOTIFY_ADD_ISSUE
    else:
        notify_add = 0
    if notify_modify:
        notify_modify = NOTIFY_MODIFY_ISSUE
    else:
        notify_modify = 0
    notify = notify_add | notify_modify
    ss = HelpDesk(id, title, user_folder,
            mail_server_name, mail_server_port, notify, mail_from_address,
            add_issue_email_subject, update_issue_email_subject,
            delete_issue_email_subject, add_issue_comment_email_subject,
            update_issue_comment_email_subject,
            delete_issue_comment_email_subject,
            issue_ticket_length, security, default_priority)
    #create roles:
    # - Issue Administrator
    # - Issue Resolver
    ss._addRole(HELPDESK_ROLE_ADMINISTRATOR)
    ss._addRole(HELPDESK_ROLE_CONSULTANT)
    # The HELPDESK_ROLE_AUTHENTICATED is for people allowed
    # to add attachments to comments and issues
    # It is usually the same as the existing "Authenticated"
    # But could have been changed.
    if HELPDESK_ROLE_AUTHENTICATED != 'Authenticated':
        ss._addRole(HELPDESK_ROLE_AUTHENTICATED)
    ss.InitHelpDesk()
    self._setObject(id, ss)
    if REQUEST:
        return self.manage_main(self,REQUEST)

class HelpDesk(Folder, EmailSender):
    """HelpDesk object"""

    #security stuff
    security = ClassSecurityInfo()
    security.setDefaultAccess("allow")

    security.setPermissionDefault(PERMISSION_ATTACH_FILES,
        (HELPDESK_ROLE_AUTHENTICATED, HELPDESK_ROLE_ADMINISTRATOR,
         HELPDESK_ROLE_CONSULTANT, 'Manager'))

    product_name = NAAYAHELPDESKAGENT_PRODUCT_NAME
    meta_type = HELPDESK_META_TYPE_LABEL

    manage_options = (
        Folder.manage_options
        +
        (
            {'label' : HELPDESK_MANAGE_OPTION_ADMINISTRATION, 'action' : 'admin_html'},
            {'label' : HELPDESK_MANAGE_OPTION_REPORTS, 'action' : 'reports_manage_html'},
        )
    )

    meta_types = (
            {'name': ISSUE_META_TYPE_LABEL, 'action': 'manage_addIssueForm'},
    )
    all_meta_types = meta_types

    #constructors
    manage_addIssueForm = Issue.manage_addIssueForm
    manage_addIssue = Issue.manage_addIssue

    security.declareProtected(PERMISSION_POST_ISSUES, 'HDAddIssue')
    HDAddIssue = Issue.AddIssue
    security.declareProtected(PERMISSION_POST_ISSUES, 'HDAddIssueQuick')
    HDAddIssueQuick = Issue.AddIssueQuick

    def __init__(self, id, title, user_folder,
            mail_server_name, mail_server_port, notify, mail_from_address,
            add_issue_email_subject, update_issue_email_subject,
            delete_issue_email_subject, add_issue_comment_email_subject,
            update_issue_comment_email_subject,
            delete_issue_comment_email_subject,
            issue_ticket_length, default_security_flag, default_priority):
        """Initialize a new instance of HelpDesk"""
        self.id = id
        self.title = title
        self.updateHelpDeskProperties(user_folder,
                mail_server_name, mail_server_port, notify, mail_from_address,
                add_issue_email_subject, update_issue_email_subject,
                delete_issue_email_subject, add_issue_comment_email_subject,
                update_issue_comment_email_subject,
                delete_issue_comment_email_subject,
                issue_ticket_length, default_security_flag, default_priority)
        self.__issuepriority = {}
        self.__issuestatus = {}
        self.__issuesendtype = {}
        self.__issuecategory = {}
        self.__user = {}
        #catalog stuff
        self.__CreateCatalog()
        #presentation
        self.date_format = _DEFAULT_DATE_FORMAT
        self.show_time = 0
        self.issues_perpage = _DEFAULT_ISSUES_PERPAGE
        EmailSender.__dict__['__init__'](self)

    def manage_delObjects(self, ids=[], REQUEST=None):
        """Delete a subordinate object."""
        #-> some checks before delete
        ids = ConvertToList(ids)
        if not ids:
            return MessageDialog(title='No items specified',
                message='No items were specified!', action ='./manage_main',)
        try:
            p=self._reserved_names
        except:
            p=()
        for n in ids:
            if n in p:
                return MessageDialog(title='Not Deletable',
                    message='<EM>%s</EM> cannot be deleted.' % n,
                    action ='./manage_main',)
        #-> start delete items
        while ids:
            id=ids[-1]
            v=self._getOb(id, self)
            if v is self:
                raise 'BadRequest', '%s does not exist' % ids[-1]
            # uncatalog issue
            self.UncatalogIssue(v)
            self._delObject(id)
            del ids[-1]
        if REQUEST is not None:
            return self.manage_main(self, REQUEST, update_menu=1)

    def updateHelpDeskProperties(self, user_folder,
            mail_server_name, mail_server_port, notify, mail_from_address,
            add_issue_email_subject, update_issue_email_subject,
            delete_issue_email_subject, add_issue_comment_email_subject,
            update_issue_comment_email_subject,
            delete_issue_comment_email_subject,
            issue_ticket_length, default_security_flag, default_priority):
        """Set/update properties"""
        self.user_folder = user_folder
        self.mail_server_name = mail_server_name
        self.mail_server_port = int(mail_server_port)
        self.notify = notify
        self.mail_from_address = mail_from_address
        self.add_issue_email_subject = add_issue_email_subject
        self.update_issue_email_subject = update_issue_email_subject
        self.delete_issue_email_subject = delete_issue_email_subject
        self.add_issue_comment_email_subject = add_issue_comment_email_subject
        self.update_issue_comment_email_subject = update_issue_comment_email_subject
        self.delete_issue_comment_email_subject = delete_issue_comment_email_subject
        self.issue_ticket_length = int(issue_ticket_length)
        self.default_security_flag = default_security_flag
        self.default_priority = int(default_priority)

    def updateHelpDeskPresentation(self, date_format, show_time, issues_perpage):
        """Set/update presentation stuff"""
        self.date_format = date_format
        self.show_time = show_time
        self.issues_perpage = int(issues_perpage)
        self._p_changed = 1

    def getUserFoldersList(self):
        """ Returns all the acl_users objects """
        output = []
        for ob in self.superValues(['User Folder', 'LDAPUserFolder', 'Naaya User Folder']):
            output.append(('/'.join(ob.getPhysicalPath()), ob.meta_type))
        return output

    def getHelpDeskAgent(self): return self

    def getUserFolderPath(self):
        """Gets user folder path"""
        return self.user_folder

    def getUserFolder(self):
        """Gets user folder if there is one, None otherwise"""
        return self.unrestrictedTraverse(self.user_folder)

    def isUserFolderZope(self):
        """Is helpdesk users folder a zope acl_users?"""
        return (self.getUserFolder().meta_type == 'User Folder')

    def isUserFolderLdap(self):
        """Is helpdesk users folder a ldap acl_users?"""
        return (self.getUserFolder().meta_type == 'LDAPUserFolder')

    def isUserFolderNaaya(self):
        """Is helpdesk users folder a Naaya acl_users?"""
        return (self.getUserFolder().meta_type == 'Naaya User Folder')

    def getUserDataZope(self, p_user=''):
        """returns data required to display the form for Zope users"""
        r = {}
        l_user = self.getUser(p_user)
        if l_user:
            r['var_mode'] = 'update'
            r['var_form_name'] = 'frmupdate'
            r['var_form_submit_name'] = 'update'
            r['var_form_submit_value'] = 'Update'
            r['var_zope_user'] = l_user.zope_user
            r['var_first_name'] = l_user.first_name
            r['var_last_name'] = l_user.last_name
            r['var_email'] = l_user.email
            r['var_role'] = l_user.role
        else:
            r['var_mode'] = 'add'
            r['var_form_name'] = 'frmadd'
            r['var_form_submit_name'] = 'add'
            r['var_form_submit_value'] = 'Add'
            r['var_zope_user'] = ''
            r['var_first_name'] = ''
            r['var_last_name'] = ''
            r['var_email'] = ''
            r['var_role'] = []
        return r

    def getUserDataNaaya(self, p_user=''):
        """returns data required to display the form for Naaya users"""
        r = {}
        l_user = self.getUser(p_user)
        if l_user:
            r['var_mode'] = 'update'
            r['var_form_name'] = 'frmupdate'
            r['var_form_submit_name'] = 'update'
            r['var_form_submit_value'] = 'Update'
            r['var_zope_user'] = l_user.zope_user
            r['var_role'] = l_user.role
        else:
            r['var_mode'] = 'add'
            r['var_form_name'] = 'frmadd'
            r['var_form_submit_name'] = 'add'
            r['var_form_submit_value'] = 'Add'
            r['var_zope_user'] = ''
            r['var_role'] = []
        return r


    ###########
    # CATALOG #
    ###########

    def __CreateCatalog(self):
        """Create ZCatalog object"""
        self.__catalog = ZCatalog('HelpDeskCatalog')
        self.__CreateCatalogIndexes()

    def __CreateCatalogIndexes(self):
        """Create some text indexes"""
        # text indexes
        self.__catalog.addIndex('subject', 'TextIndex')
        self.__catalog.addIndex('description', 'TextIndex')
        self.__catalog.addIndex('issuecomments', 'TextIndex')
        self.__catalog.addIndex('user_name', 'TextIndex')
        #field indexes
        self.__catalog.addIndex('security', 'FieldIndex')
        self.__catalog.addIndex('category', 'FieldIndex')
        self.__catalog.addIndex('priority', 'FieldIndex')
        self.__catalog.addIndex('status', 'FieldIndex')
        self.__catalog.addIndex('consultant', 'FieldIndex')

    def __ClearCatalog(self):
        """Clear catalog"""
        self.__catalog.manage_catalogClear()

    def __BuildCatalogPath(self, oIssue):
        """Build a path for Issue objects"""
        return oIssue.id

    def __ElimintateDuplicates(self, issues):
        """Eliminate duplicates from a list of objects (with ids)"""
        dict = {}
        for issue in issues:
            dict[issue.id] = issue
        return dict.values()

    def SearchCatalog(self, query, filter):
        """Search Catalog defined indexes"""
        results = []
        criteria = filter.copy()
        criteria['subject'] = query
        results.extend(self.__catalog(criteria))
        criteria = filter.copy()
        criteria['description'] = query
        results.extend(self.__catalog(criteria))
        criteria = filter.copy()
        criteria['issuecomments'] = query
        results.extend(self.__catalog(criteria))
        #get issue objects
        results = map(self.__catalog.getobject,
                map(getattr, results, ('data_record_id_',)*len(results)))
        #eliminate duplicates
        return self.__ElimintateDuplicates(results)

    def CatalogIssue(self, oIssue):
        """Catalog Issue objects"""
        self.__catalog.catalog_object(oIssue, self.__BuildCatalogPath(oIssue))

    def UncatalogIssue(self, oIssue):
        """Uncatalog Issue objects"""
        self.__catalog.uncatalog_object(self.__BuildCatalogPath(oIssue))

    def RecatalogIssue(self, oIssue):
        """Recatalog Issue objects"""
        self.UncatalogIssue(oIssue)
        self.CatalogIssue(oIssue)

    def valideIssueProperty(self, param):
        """Check if exists a property with given value"""
        return param in ['date_open', 'date_modify', 'consultant',
                'user_name', 'subject', 'category', 'priority', 'status']


    #############
    # PRIORITY  #
    #############

    def getIssuePriority(self, oId):
        """Get a IssuePriority object by id"""
        try: return self.__issuepriority[oId]
        except: return None

    def getIssuePriorityTitle(self, oId):
        """Get the title of a IssuePriority object by id"""
        try:
            return self.getIssuePriority(oId).title
        except:
            return ''

    def getListIssuePriority(self):
        """Get the list of IssuePriority objects"""
        return self.__issuepriority.values()

    def addIssuePriority(self, oId, obj):
        """Add a new IssuePriority object"""
        self.__issuepriority[oId] = obj
        self._p_changed = 1

    def updateIssuePriority(self, oId, oTitle, oDescription, oValue):
        """Update a IssuePriority object"""
        try:
            obj = self.__issuepriority[oId]
        except:
            pass
        else:
            obj.title = oTitle
            obj.description = oDescription
            obj.value = int(oValue)
            self.__issuepriority[oId] = obj
            self._p_changed = 1

    def deleteIssuePriority(self, oIds):
        """Delete IssuePriority objects"""
        for oId in ConvertToList(oIds):
            try:
                del(self.__issuepriority[oId])
            except:
                pass
        self._p_changed = 1


    ###########
    # STATUS  #
    ###########

    def getIssueStatus(self, oId):
        """Get a IssueStatus object by id"""
        try: return self.__issuestatus[oId]
        except: return None

    def getIssueStatusByOrder(self):
        """Get the IssueStatus object with lower order"""
        theobj = None
        theorder = 10000
        for obj in self.getListIssueStatus():
            if obj.order < theorder:
                theobj = obj
                theorder = obj.order
        return theobj

    def getIssueStatusTitle(self, oId):
        """Get the title of a IssueStatus object by id"""
        try:
            return self.getIssueStatus(oId).title
        except:
            return ''

    def getIssueStatusInit(self):
        """Get default status for a new issue:
           - this will be the status with the lower status value"""
        try:
            return self.getIssueStatusByOrder().id
        except:
            return ''

    def getIssueStatusFinal(self):
        """Get the id of the final(closed) state for an issue:
            - this iwll be the status with the higher status value"""
        try:
            return self.SortObjsListByAttr(self.getListIssueStatus(), 'order', 1)[0].id
        except:
            return None

    def getListIssueStatus(self):
        """Get the list of IssueStatus objects"""
        try: return self.__issuestatus.values()
        except: return None

    def addIssueStatus(self, oId, obj):
        """Add a new IssueStatus object"""
        self.__issuestatus[oId] = obj
        self._p_changed = 1

    def updateIssueStatus(self, oId, oTitle, oDescription, oOrder):
        """Update a IssueStatus object"""
        try:
            obj = self.__issuestatus[oId]
        except:
            pass
        else:
            obj.title = oTitle
            obj.description = oDescription
            obj.order = int(oOrder)
            self.__issuestatus[oId] = obj
            self._p_changed = 1

    def deleteIssueStatus(self, oIds):
        """Delete IssueStatus objects"""
        for oId in ConvertToList(oIds):
            try:
                del(self.__issuestatus[oId])
            except:
                pass
        self._p_changed = 1


    #############
    # SEND TYPE #
    #############

    def getIssueSendType(self, oId):
        """Get a IssueSendType object by id"""
        try: return self.__issuesendtype[oId]
        except: return None

    def getIssueSendTypeTitle(self, oId):
        """Get the title of a IssueSendType object by id"""
        try:
            return self.getIssueSendType(oId).title
        except:
            return ''

    def getListIssueSendType(self):
        """Get the list of IssueSendType objects"""
        try: return self.__issuesendtype.values()
        except: return None

    def addIssueSendType(self, oId, obj):
        """Add a new IssueSendType object"""
        self.__issuesendtype[oId] = obj
        self._p_changed = 1

    def updateIssueSendType(self, oId, oTitle, oDescription):
        """Update a IssueSendType object"""
        try:
            obj = self.__issuesendtype[oId]
        except:
            pass
        else:
            obj.title = oTitle
            obj.description = oDescription
            self.__issuesendtype[oId] = obj
            self._p_changed = 1

    def deleteIssueSendType(self, oIds):
        """Delete IssueSendType objects"""
        for oId in ConvertToList(oIds):
            try:
                del(self.__issuesendtype[oId])
            except:
                pass
        self._p_changed = 1


    #############
    # CATEGORY  #
    #############

    def getIssueCategory(self, oId):
        """Get a IssueCategory object by id"""
        try: return self.__issuecategory[oId]
        except: return None

    def getIssueCategoryTitle(self, oId):
        """Get the title of a IssueCategory object by id"""
        try:
            return self.getIssueCategory(oId).title
        except:
            return ''

    def getIssueCategoryPriority(self, oId):
        """Get the priority of a IssueCategory object by id"""
        try:
            return self.getIssueCategory(oId).priority
        except:
            return ''

    def getIssueCategoryConsultant(self, oId):
        """Get the default consultant of an IssueCategory object"""
        try:
            return self.getIssueCategory(oId).issuesconsultant
        except:
            return ''

    def getListIssueCategory(self):
        """Get the list of IssueCategory objects"""
        try: return self.__issuecategory.values()
        except: return None

    def addIssueCategory(self, oId, obj):
        """Add a new IssueCategory object"""
        self.__issuecategory[oId] = obj
        self._p_changed = 1

    def updateIssueCategory(self, oId, oTitle, oDescription, oPriority, oAdvice, oAdvicelink, oIssuesConsultant):
        """Update a IssueCategory object"""
        try:
            obj = self.__issuecategory[oId]
        except:
            pass
        else:
            obj.title = oTitle
            obj.description = oDescription
            obj.priority = oPriority
            obj.advice = oAdvice
            obj.advicelink = oAdvicelink
            obj.issuesconsultant = oIssuesConsultant
            self.__issuecategory[oId] = obj
            self._p_changed = 1

    def deleteIssueCategory(self, oIds):
        """Delete IssueCategory objects"""
        for oId in ConvertToList(oIds):
            try:
                del(self.__issuecategory[oId])
            except:
                pass
        self._p_changed = 1


    #####################
    #   PRESENTATION    #
    #####################

    def getDateFormatsList(self):
        """Default there are some date formats. The manager can choose from one of them."""
        return _DATE_FORMATS.keys()

    def getDateFormat(self, id):
        """Returns a date format"""
        return _DATE_FORMATS[id]

    def getDateFormatModel(self):
        """Returns a format model for the date object"""
        model = ''
        model += _DATE_MODELS[self.date_format]
        if self.show_time:
            model += ' ' + _TIME_MODEL
        return model

    #############
    #   USERS   #
    #############

    def getUser(self, oId):
        """Get a User object by id"""
        try: return self.__user[oId]
        except: return None

    def getUserName(self, oId):
        """ Get the name of a User object by id.
            If is a ldap user we get the canonical name from ldap.
            If is a zope user we get the full name (first name & last name)
            from User object
        """
        if self.isUserFolderLdap():
            return self.__getLdapUserName(oId)
        if self.isUserFolderZope():
            return self.__getZopeUserName(oId)
        if self.isUserFolderNaaya():
            return self.__getNaayaUserName(oId)
        return oId

    def __getZopeUserName(self, oId):
        """Returns the full name of a 'zope user'"""
        res = oId
        oUser = self.getUser(oId)
        if oUser:
            res = oUser.first_name + ' ' + oUser.last_name
        return res

    def __getLdapUserName(self, oId):
        """Returns the canonical name of a 'ldap user'"""
        res = oId
        oUser = self.getUserFolder().getUser(oId)
        if oUser:
            try:
                res = oUser.cn
            except:
                pass
        return res

    def __getNaayaUserName(self, oId):
        """Returns the full name of a 'Naaya user'"""
        res = oId
        oUser = self.getUserFolder().getUser(oId)
        if oUser:
            res = oUser.firstname + ' ' + oUser.lastname
        return res

    def getUserEmail(self, oId):
        """ Get the email of an User object by id.
            If is a ldap user we get the email address from ldap.
            If is a zope user we get the email from User object
        """
        if self.isUserFolderLdap():
            return self.__getLdapUserEmail(oId)
        if self.isUserFolderZope():
            return self.__getZopeUserEmail(oId)
        if self.isUserFolderNaaya():
            return self.__getNaayaUserEmail(oId)
        return ''

    def __getZopeUserEmail(self, oId):
        """Returns the email of a 'zope user'"""
        res = ''
        oUser = self.getUser(oId)
        if oUser:
            res = oUser.email
        return res

    def __getLdapUserEmail(self, oId):
        """Returns the email of a 'ldap user'"""
        res = ''
        oUser = self.getUserFolder().getUser(oId)
        if oUser:
            try:
                res = oUser.mail
            except:
                pass
        return res

    def __getNaayaUserEmail(self, oId):
        """Returns the email of a 'Naaya user'"""
        res = ''
        oUser = self.getUserFolder().getUser(oId)
        if oUser:
            res = oUser.email
        return res

    def getListUser(self):
        """Get the list of User objects"""
        try: return self.__user.values()
        except: return None

    def getListUserAdministrator(self):
        """Get a list of User objects with Issue Administrator role"""
        try:
            users = self.__user.values()
            administrators = []
            for user in users:
                if self.getHDRoleAdministrator() in user.role:
                    administrators.append(user)
            return administrators
        except: return None

    def getEmailUserAdministrator(self):
        """Get a list of User emails with Issue Administrator role"""
        try:
            users = self.__user.values()
            dictemails = {}
            for user in users:
                if self.getHDRoleAdministrator() in user.role:
                    email = self.getUserEmail(user.id)
                    if email != '':
                        dictemails[email] = ''
            return dictemails
        except: return {}

    def getEmailUserConsultant(self):
        """Get a list of User emails with Issue Resolver role"""
        try:
            users = self.__user.values()
            dictemails = {}
            for user in users:
                if self.getHDRoleConsultant() in user.role:
                    email = self.getUserEmail(user.id)
                    if email != '':
                        dictemails[email] = ''
            return dictemails
        except: return {}

    def getListUserConsultant(self):
        """Get a list of User objects with Issue Resolver role"""
        try:
            users = self.__user.values()
            consultants = []
            for user in users:
                if self.getHDRoleConsultant() in user.role:
                    consultants.append(user)
            return consultants
        except: return None

    def addUser(self, oId, obj):
        """Add a new User object"""
        self.__user[oId] = obj
        self.manage_setLocalRoles(oId, ConvertToList(obj.role))
        self._p_changed = 1

    def updateUser(self, oId, oFirstname, oLastname, oEmail, oRole):
        """Update a User object"""
        try:
            obj = self.__user[oId]
        except:
            pass
        else:
            obj.first_name = oFirstname
            obj.last_name = oLastname
            obj.email = oEmail
            obj.role = ConvertToList(oRole)
            self.__user[oId] = obj
            self.manage_setLocalRoles(oId, ConvertToList(obj.role))
            self._p_changed = 1

    def deleteUser(self, oIds):
        """Delete User objects"""
        for oId in ConvertToList(oIds):
            try:
                del(self.__user[oId])
                self.manage_delLocalRoles(ConvertToList(oId))
            except:
                pass
        self._p_changed = 1

    security.declareProtected(view_management_screens, 'manageHelpDeskProperties')
    def manageHelpDeskProperties(self, REQUEST=None):
        """Set HelpDesk properties"""
        if updateObjectAction(REQUEST):
            #update properties
            user_folder = REQUEST.get('user_folder' , '')
            mail_server_name = REQUEST.get('mail_server_name', '')
            mail_server_port = REQUEST.get('mail_server_port', HELPDESK_DEFAULT_MAIL_SERVER_NAME)
            if REQUEST.has_key('notify_add'):
                notify_add = NOTIFY_ADD_ISSUE
            else:
                notify_add = 0
            if REQUEST.has_key('notify_modify'):
                notify_modify = NOTIFY_MODIFY_ISSUE
            else:
                notify_modify = 0
            notify = notify_add | notify_modify
            mail_from_address = REQUEST.get('mail_from_address', HELPDESK_DEFAULT_MAIL_FROM_ADDRESS)
            add_issue_email_subject = REQUEST.get('add_issue_email_subject', '')
            update_issue_email_subject = REQUEST.get('update_issue_email_subject', '')
            delete_issue_email_subject = REQUEST.get('delete_issue_email_subject', '')
            add_issue_comment_email_subject = REQUEST.get('add_issue_comment_email_subject', '')
            update_issue_comment_email_subject = REQUEST.get('update_issue_comment_email_subject', '')
            delete_issue_comment_email_subject = REQUEST.get('delete_issue_comment_email_subject', '')
            issue_ticket_length = int(REQUEST.get('issue_ticket_length', HELPDESK_DEFAULT_ISSUE_TICKET_LENGTH))
            default_security_flag = REQUEST.get('security', _DEFAULT_ISSUE_SECURITY)
            default_priority = REQUEST.get('default_priority', 1)
            self.updateHelpDeskProperties(user_folder,
                    mail_server_name, mail_server_port, notify, mail_from_address,
                    add_issue_email_subject, update_issue_email_subject,
                    delete_issue_email_subject, add_issue_comment_email_subject,
                    update_issue_comment_email_subject,
                    delete_issue_comment_email_subject,
                    issue_ticket_length, default_security_flag, default_priority)
        REQUEST.RESPONSE.redirect('admin_html')

    security.declareProtected(view_management_screens, 'manageHelpDeskCatalog')
    def manageHelpDeskCatalog(self, REQUEST=None):
        """Update HelpDesk Catalog"""
        self.__ClearCatalog()
        for issue in self.getAllIssues():
            self.CatalogIssue(issue)
        REQUEST.RESPONSE.redirect('admin_html?pagetab=1')

    security.declareProtected(view_management_screens, 'manageIssuePriority')
    def manageIssuePriority(self, REQUEST=None):
        """Manage IssuePriority objects"""
        if addObjectAction(REQUEST):
            #add a new IssuePriority object
            oId = GenRandomKey()
            oTitle = REQUEST.get('title', '')
            oDescription = REQUEST.get('description', '')
            oValue = REQUEST.get('value', '')
            obj = IssuePriority(oId, oTitle, oDescription, oValue)
            self.addIssuePriority(oId, obj)
        elif updateObjectAction(REQUEST):
            #update a IssuePriority object
            oId = REQUEST.get('id', '')
            oTitle = REQUEST.get('title', '')
            oDescription = REQUEST.get('description', '')
            oValue = REQUEST.get('value', '')
            self.updateIssuePriority(oId, oTitle, oDescription, oValue)
        elif deleteObjectAction(REQUEST):
            #delete IssuePriority objects
            oIds = REQUEST.get('ids', [])
            self.deleteIssuePriority(oIds)
        REQUEST.RESPONSE.redirect('admin_html?pagetab=2')

    security.declareProtected(view_management_screens, 'manageIssueStatus')
    def manageIssueStatus(self, REQUEST=None):
        """Manage IssueStatus objects"""
        if addObjectAction(REQUEST):
            #add a new IssueStatus object
            oId = GenRandomKey()
            oTitle = REQUEST.get('title', '')
            oDescription = REQUEST.get('description', '')
            oOrder = REQUEST.get('order', '')
            obj = IssueStatus(oId, oTitle, oDescription, oOrder)
            self.addIssueStatus(oId, obj)
        elif updateObjectAction(REQUEST):
            #update a IssueStatus object
            oId = REQUEST.get('id', '')
            oTitle = REQUEST.get('title', '')
            oDescription = REQUEST.get('description', '')
            oOrder = REQUEST.get('order', '')
            self.updateIssueStatus(oId, oTitle, oDescription, oOrder)
        elif deleteObjectAction(REQUEST):
            #delete IssueStatus objects
            oIds = REQUEST.get('ids', [])
            self.deleteIssueStatus(oIds)
        REQUEST.RESPONSE.redirect('admin_html?pagetab=3')

    security.declareProtected(view_management_screens, 'manageIssueSendType')
    def manageIssueSendType(self, REQUEST=None):
        """Manage IssueSendType objects"""
        if addObjectAction(REQUEST):
            #add a new IssueSendType object
            oId = GenRandomKey()
            oTitle = REQUEST.get('title', '')
            oDescription = REQUEST.get('description', '')
            obj = IssueSendType(oId, oTitle, oDescription)
            self.addIssueSendType(oId, obj)
        elif updateObjectAction(REQUEST):
            #update a IssueSendType object
            oId = REQUEST.get('id', '')
            oTitle = REQUEST.get('title', '')
            oDescription = REQUEST.get('description', '')
            self.updateIssueSendType(oId, oTitle, oDescription)
        elif deleteObjectAction(REQUEST):
            #delete IssueSendType objects
            oIds = REQUEST.get('ids', [])
            self.deleteIssueSendType(oIds)
        REQUEST.RESPONSE.redirect('admin_html?pagetab=4')

    security.declareProtected(view_management_screens, 'manageIssueCategory')
    def manageIssueCategory(self, REQUEST=None):
        """Manage IssueCategory objects"""
        if addObjectAction(REQUEST):
            #add a new IssueCategory object
            oId = GenRandomKey()
            oTitle = REQUEST.get('title', '')
            oDescription = REQUEST.get('description', '')
            oPriority = REQUEST.get('priority', '')
            oAdvice = REQUEST.get('advice', '')
            oAdvicelink = REQUEST.get('advicelink', '')
            oIssuesConsultant = REQUEST.get('issuesconsultant', '')
            obj = IssueCategory(oId, oTitle, oDescription, oPriority, oAdvice, oAdvicelink, oIssuesConsultant)
            self.addIssueCategory(oId, obj)
        elif updateObjectAction(REQUEST):
            #update a IssueCategory object
            oId = REQUEST.get('id', '')
            oTitle = REQUEST.get('title', '')
            oDescription = REQUEST.get('description', '')
            oPriority = REQUEST.get('priority', '')
            oAdvice = REQUEST.get('advice', '')
            oAdvicelink = REQUEST.get('advicelink', '')
            oIssuesConsultant = REQUEST.get('issuesconsultant', '')
            self.updateIssueCategory(oId, oTitle, oDescription, oPriority, oAdvice, oAdvicelink, oIssuesConsultant)
        elif deleteObjectAction(REQUEST):
            #delete IssueCategory objects
            oIds = REQUEST.get('ids', [])
            self.deleteIssueCategory(oIds)
        REQUEST.RESPONSE.redirect('admin_html?pagetab=5')

    security.declareProtected(view_management_screens, 'manageUser')
    def manageUser(self, REQUEST=None):
        """Manage User objects"""
        if addObjectAction(REQUEST):
            #add a new User object
            oZopeuser = REQUEST.get('zope_user', '')
            if oZopeuser == '':
                return MessageDialog(title='Missing value',
                    message='You must specify an user!',
                    action ='admin_users_html')
            oFirstname = REQUEST.get('first_name', '')
            oLastname = REQUEST.get('last_name', '')
            oEmail = REQUEST.get('email', '')
            oRole = REQUEST.get('role', [])
            obj = User(oZopeuser, oZopeuser, oFirstname, oLastname, oEmail, oRole)
            self.addUser(oZopeuser, obj)
        elif updateObjectAction(REQUEST):
            #update a User object
            oZopeuser = REQUEST.get('zope_user', '')
            if oZopeuser == '':
                return MessageDialog(title='Missing value',
                    message='You must specify an user!',
                    action ='admin_users_html')
            oFirstname = REQUEST.get('first_name', '')
            oLastname = REQUEST.get('last_name', '')
            oEmail = REQUEST.get('email', '')
            oRole = REQUEST.get('role', [])
            self.updateUser(oZopeuser, oFirstname, oLastname, oEmail, oRole)
        elif deleteObjectAction(REQUEST):
            #delete User objects
            oIds = REQUEST.get('ids', [])
            self.deleteUser(oIds)
        REQUEST.RESPONSE.redirect('admin_html?pagetab=6')

    security.declareProtected(view_management_screens, 'manageHelpDeskPresentation')
    def manageHelpDeskPresentation(self, REQUEST=None):
        """Set HelpDesk presentation"""
        date_format = REQUEST.get('date_format', _DEFAULT_DATE_FORMAT)
        if REQUEST.has_key('show_time'):
            show_time = 1
        else:
            show_time = 0
        issues_perpage = REQUEST.get('issues_perpage', _DEFAULT_ISSUES_PERPAGE)
        self.updateHelpDeskPresentation(date_format, show_time, issues_perpage)
        REQUEST.RESPONSE.redirect('admin_html?pagetab=7')

    security.declareProtected(view_management_screens, 'manageHelpDeskImport')
    def manageHelpDeskImport(self, hdpath='', REQUEST=None):
        """ Import data from an older version of HelpDeskAgent """
        hd = self.unrestrictedTraverse(hdpath, None)
        if hd is not None:
            #import ref tables
            self.deleteIssuePriority(self.__issuepriority.keys())
            for x in hd.getListIssuePriority():
                o = IssuePriority(x.id, x.title, x.description, x.value)
                self.addIssuePriority(x.id, o)
            self.deleteIssueStatus(self.__issuestatus.keys())
            for x in hd.getListIssueStatus():
                o = IssueStatus(x.id, x.title, x.description, x.order)
                self.addIssueStatus(x.id, o)
            self.deleteIssueSendType(self.__issuesendtype.keys())
            for x in hd.getListIssueSendType():
                o = IssueSendType(x.id, x.title, x.description)
                self.addIssueSendType(x.id, o)
            self.deleteIssueCategory(self.__issuecategory.keys())
            for x in hd.getListIssueCategory():
                o = IssueCategory(x.id, x.title, x.description, x.priority,
                    x.advice, x.advicelink, x.issuesconsultant)
                self.addIssueCategory(x.id, o)
            #import issues
            for issue in hd.getAllIssues():
                ob = Issue.Issue(issue.id, issue.title, issue.date_open,
                    issue.consultant, issue.user_name, issue.user_email,
                    issue.user_phone, issue.subject, issue.category,
                    issue.sendtype, issue.priority, issue.status,
                    issue.description, issue.link, issue.security)
                self._setObject(issue.id, ob)
                ob = self._getOb(issue.id)
                ob.date_modify = issue.date_modify
                ob.data_close = issue.date_close
                ob.solution_time = issue.solution_time
                ob._Issue__issuecomment = {}
                ob._Issue__historycounter = issue._Issue__historycounter
                ob._Issue__issuehistory = {}
                #comments
                for c in issue.getListIssueComment():
                    try: content_type = c.content_type
                    except: content_type = 1
                    cob = IssueComment(c.id, c.date, c.username, content_type, c.content)
                    ob._Issue__issuecomment[c.id] = cob
                #history
                for h in issue.getListIssueHistory():
                    try: comments = h.comments
                    except: comments = ''
                    hob = IssueHistory(h.id, h.date, h.username, h.action,
                        h.status, h.priority, h.consultant, comments)
                    ob._Issue__issuehistory[h.id] = hob
                #attachements
                for x in issue.objectValues('File'):
                    ob.manage_addFile(x.getId(), str(x.data), x.title, content_type=x.content_type)
                ob._p_changed = 1
                self.CatalogIssue(ob)
        if REQUEST:
            REQUEST.RESPONSE.redirect('admin_html?pagetab=8')

    security.declareProtected(view, 'getAllIssues')
    def getAllIssues(self):
        """Returns a list with all Issue objects"""
        return self.objectValues(ISSUE_META_TYPE_LABEL)

    security.declareProtected(view, 'SearchSortIssues')
    def SearchSortIssues(self, start, skey, rkey, query, **args):
        """Returns a sorted list with Issue objects"""
        if (self.isHelpDeskAdministrator() != 1) and (self.isHelpDeskConsultant() != 1):
            args['security'] = self.getIssuePublic()
        issues = self.SearchIssues(query, args)
        if self.validParams(skey, rkey):
            issues = self.SortIssues(issues, skey, rkey)
        #paging
        total = len(issues)
        try: start = abs(int(start))
        except: start = 1
        start = min(start, total)
        stop = min(start + self.issues_perpage - 1, total)
        prev = next = -1
        if start != 1:
            prev = start - self.issues_perpage
            if prev < 0: prev = -1
        if stop < total: next = stop + 1
        return issues, start, stop, total, prev, next

    security.declarePrivate('SearchIssues')
    def SearchIssues(self, query, args):
        """ Search Issue objects - we'll use the internal
            ZCatalog objects to search through Issue objects
        """
        local_filter = {}
        only_new = 0
        for arg in args.keys():
            if args[arg] != '':
                if arg == 'new':
                    only_new = 1
                else:
                    local_filter[arg] = args[arg]
        issues = self.SearchCatalog(query, local_filter)
        if only_new:
            buf = map(None,
                    map(getattr, issues, ('date_open',)*len(issues)),
                    map(getattr, issues, ('date_modify',)*len(issues)),
                    issues)
            buf = filter(self.FilterIssue, buf)
            issues = map(operator.getitem, buf, (-1,)*len(buf))
        return issues

    security.declarePrivate('validParams')
    def validParams(self, sortby, how):
        """Validate sort parameters"""
        res = 1
        if (how != '' and how != '1'):
            res = 0
        else:
            if (self.valideIssueProperty(sortby)):
                res = 1
            else:
                res = 0
        return res

    security.declarePrivate('FilterIssue')
    def FilterIssue(self, issue_tuple):
        """Filter a tuple like (value1, value2, issue)"""
        return issue_tuple[0] == issue_tuple[1]

    security.declarePrivate('SortIssues')
    def SortIssues(self, issues, sortby, how):
        """Sort a list of issues by a property"""
        buf = map(None,
                map(getattr, issues, (sortby,)*len(issues)),
                xrange(len(issues)),
                issues)
        buf.sort(lambda x,y: cmp(unicode(x), unicode(y)))
        if how == '1':
            buf.reverse()
        return map(operator.getitem, buf, (-1,)*len(buf))


    ##########
    # STUFF  #
    ##########

    def SortObjsListByAttr(self, p_list, p_attr, p_desc=1):
        """Sort a list of objects by an attribute values"""
        l_len = len(p_list)
        l_temp = map(None, map(getattr, p_list, (p_attr,)*l_len), xrange(l_len), p_list)
        l_temp.sort()
        if p_desc:
            l_temp.reverse()
        return map(operator.getitem, l_temp, (-1,)*l_len)

    def getIssuesObject(self, oId):
        """Get an Issue object"""
        try: return self._getOb(oId)
        except: return None

    def GetRandomPassword(self):
        """Generate a random password"""
        return GenRandomId(10)

    def CurrentDate(self):
        """Returns a string with current date"""
        return self.FormatDate(DateTime())

    def CurrentDateTime(self):
        """Returns a string with current date time"""
        return self.FormatDateTime(DateTime())

    def FormatDate(self, datetime):
        """Returns a string with date"""
        return FormatDateByModel(datetime, self.getDateFormatModel())

    def FormatDateTime(self, datetime):
        """Returns a string with date time"""
        return FormatDateTimeToString(datetime)

    def GetFilterString(self, **args):
        """Returns a string like: property=value&property=value ... """
        filterquerystring = ''
        for arg in args.keys():
            if args[arg] != '':
                filterquerystring += arg + '='+ args[arg] + '&'
        if filterquerystring != '':
            filterquerystring = filterquerystring[0:len(filterquerystring)-1]
        return filterquerystring

    security.declarePublic('GetSortQueryString')
    def GetSortQueryString(self, property, sortby, how, filterquerystring):
        """Returns a string like : sort=property&how=(asc|desc)"""
        querystring=''
        if property==sortby:
            if how == 'asc':
                querystring += 'sort=' + property + '&how=desc'
            else:
                querystring += 'sort=' + property + '&how=asc'
        else:
            querystring += 'sort=' + property + '&how=asc'
        if filterquerystring != '':
            querystring += '&' + filterquerystring
        return querystring

    security.declarePublic('GetSortPicture')
    def GetSortPicture(self, property, sortby, how):
        """Returns the name of the sort picture"""
        picture='spacer'
        if property==sortby:
            if (how == 'asc'):
                picture = 'sort_asc'
            elif (how == 'desc'):
                picture = 'sort_desc'
        return picture

    def getDefaultAdviceLink(self):
        """Handle the HTTP_REFERER value and return a default value for advice link"""
        try:
            if self.REQUEST['HTTP_REFERER'][:len(self.absolute_url())] != self.absolute_url():
                return self.REQUEST['HTTP_REFERER']
        except:
            pass
        return ''


    #########
    # ROLES #
    #########

    def getHDRoleAdministrator(self):
        """Returns the name of the administrator role"""
        return HELPDESK_ROLE_ADMINISTRATOR

    def isHelpDeskAdministrator(self):
        """Test if current user is administrotor"""
        return self.REQUEST.AUTHENTICATED_USER.has_role(HELPDESK_ROLE_ADMINISTRATOR, self)

    def getHDRoleConsultant(self):
        """Returns the name of the resolver role"""
        return HELPDESK_ROLE_CONSULTANT

    def isHelpDeskConsultant(self):
        """Test if current user is resolver"""
        return self.REQUEST.AUTHENTICATED_USER.has_role(HELPDESK_ROLE_CONSULTANT, self)

    def isAuthenticated(self):
        """Test if current user is authenticated"""
        return self.REQUEST.AUTHENTICATED_USER.has_role(HELPDESK_ROLE_AUTHENTICATED, self)

    def getAuthenticatedUser(self):
        """Return the name of the authenticated user"""
        return self.REQUEST.AUTHENTICATED_USER.getUserName()

    #############
    # SECURITY  #
    #############

    def getIssuePublic(self):
        """Returns the value for a public issue"""
        return ISSUE_SECURITY_PUBLIC

    def isSecurityFlagPublic(self):
        """Test if default security flag for issues is 'public'"""
        return (self.default_security_flag == self.getIssuePublic())

    def isPublic(self, issue):
        """Test if current issue is public"""
        return (issue.security == self.getIssuePublic())

    def getIssuePrivate(self):
        """Returns the value for a private issue"""
        return ISSUE_SECURITY_PRIVATE

    def isSecurityFlagPrivate(self):
        """Test if default security flag for issues is 'private'"""
        return (self.default_security_flag == self.getIssuePrivate())

    def isPrivate(self, issue):
        """Test if current issue is private"""
        return (issue.security == self.getIssuePrivate())

    def checkPermissionPostIssues(self):
        """
        Check the right to post issues.
        """
        return getSecurityManager().checkPermission(PERMISSION_POST_ISSUES, self) is not None

    #############
    #   EMAILS  #
    #############
    def notifyNewIssue(self):
        """returns 1 if notify for new issue"""
        return self.notify & NOTIFY_ADD_ISSUE

    def notifyModifyIssue(self):
        """returns 1 if notify for edit issue"""
        return self.notify & NOTIFY_MODIFY_ISSUE

    def SendEmailNotifications(self, eSendOptions, eAction, eIssueId, eBody=''):
        """Sends emails"""
        #init some variables
        oIssue = self._getOb(eIssueId)
        eFrom = self.mail_from_address
        sIssueUrl = '%s/index_html' % oIssue.absolute_url(0)
        if eAction == ACTION_ADD_ISSUE:
            #new issue
            eSubject = self.add_issue_email_subject
            eContent = HELPDESK_DEFAULT_ADD_ISSUE_EMAIL_SUBJECT + '\n'
            eContent += '\nSubject\n-------\n%s' % oIssue.subject
            eContent += '\n\nDescription\n-----------\n%s' % oIssue.description
            eContent += '\n\nCategory\n--------\n%s' % self.getIssueCategoryTitle(oIssue.category)
            eContent += '\n\nStatus\n-----------\n%s' % self.getIssueStatusTitle(oIssue.status)
            eContent += '\n\nAssigned to\n-----------\n%s' % self.getUserName(oIssue.consultant)
            eContent += '\n\nPriority\n--------\n%s' % self.getIssuePriorityTitle(oIssue.priority)
            eContent += '\n\nFor more details %s' % sIssueUrl
        elif eAction == ACTION_UPDATE_ISSUE:
            #issue modified
            eSubject = self.update_issue_email_subject
            eContent = HELPDESK_DEFAULT_UPDATE_ISSUE_EMAIL_SUBJECT + '\n'
            eContent += '\nSubject\n-------\n%s' % oIssue.subject
            eContent += '\n\nStatus\n-----------\n%s' % self.getIssueStatusTitle(oIssue.status)
            eContent += '\n\nAssigned to\n-----------\n%s' % self.getUserName(oIssue.consultant)
            eContent += '\n\nPriority\n--------\n%s' % self.getIssuePriorityTitle(oIssue.priority)
            eContent += '\n\nFor more details %s' % sIssueUrl
        elif eAction == ACTION_DELETE_ISSUE:
            #issue deleted
            eSubject = self.delete_issue_email_subject
            eContent = HELPDESK_DEFAULT_DELETE_ISSUE_EMAIL_SUBJECT + '\n' + sIssueUrl
        elif eAction == ACTION_ADD_COMMENT:
            #new comment
            eSubject = self.add_issue_comment_email_subject
            eContent = HELPDESK_DEFAULT_ADD_ISSUE_COMMENT_EMAIL_SUBJECT
            eContent += '\n\nComment\n--------\n%s' % eBody
            eContent += '\n\nFor more details %s' % sIssueUrl
        elif eAction == ACTION_UPDATE_COMMENT:
            #comment modified
            eSubject = self.update_issue_comment_email_subject
            eContent = HELPDESK_DEFAULT_UPDATE_ISSUE_COMMENT_EMAIL_SUBJECT + '\n' + sIssueUrl
            eContent += '\n\nComment\n--------\n%s' % eBody
            eContent += '\n\nFor more details %s' % sIssueUrl
        elif eAction == ACTION_DELETE_COMMENT:
            #comment deleted
            eSubject = self.delete_issue_comment_email_subject
            eContent = HELPDESK_DEFAULT_DELETE_ISSUE_COMMENT_EMAIL_SUBJECT
            eContent += '\n\nFor more details %s' % sIssueUrl
        else:
            #unknown action
            return 1
        #send emails
        dictemails = {}
        if oIssue.consultant == '':
            #send emails to administrators
            if (eSendOptions & SENDEMAIL_HELPDESK_ADMINISTRATORS):
                eTo = self.getEmailUserAdministrator()
                if eTo != {}:
                    self.SendEmail(eContent, eTo, eFrom, eSubject)
                dictemails = eTo
        else:
            #do not send email if the authenticated user is the same with the issue's consultant
            if self.getAuthenticatedUser() != oIssue.consultant:
                if (eSendOptions & SENDEMAIL_HELPDESK_CONSULTANTS):
                    #send emails to resolver if there is any for this issue
                    eTo = self.getUserEmail(oIssue.consultant)
                    if eTo != '':
                        self.SendEmail(eContent, {eTo:''}, eFrom, eSubject)
                    dictemails.update({eTo:''})
            if (eSendOptions & SENDEMAIL_HELPDESK_USERS):
                #send emails to users
                eTo = oIssue.user_email
                if eTo != '' and not dictemails.has_key(eTo):
                    self.SendEmail(eContent, {eTo:''}, eFrom, eSubject)
        return 1


    ###########################
    #       INIT HELPDESK ELEMENTS  #
    ###########################
    security.declarePrivate('InitHelpDesk')
    def InitHelpDesk(self):
        """Create some default objects: priority, status, send type"""
        file = open(join(NAAYAHELPDESKAGENT_PRODUCT_PATH, 'HelpDesk.ini'), 'r')
        for line in file.readlines():
            line = line.strip()
            if line != '':
                iType, iValues = line.split('=')
                if iType == INIFILE_ISSUE_PRIORITY:
                    #add IssuePriority
                    iId, iTitle, iDescription, iValue = iValues.split(',')
                    self.addIssuePriority(iId, IssuePriority(iId, iTitle, iDescription, iValue))
                elif iType == INIFILE_ISSUE_STATUS:
                    #add IssueStatus
                    iId, iTitle, iDescription, iOrder = iValues.split(',')
                    self.addIssueStatus(iId, IssueStatus(iId, iTitle, iDescription, iOrder))
                elif iType == INIFILE_ISSUE_SENDTYPE:
                    #add IssueSendType
                    iId, iTitle, iDescription = iValues.split(',')
                    self.addIssueSendType(iId, IssueSendType(iId, iTitle, iDescription))
                elif iType == INIFILE_ISSUE_CATEGORY:
                    #add IssueCategory
                    iId, iTitle, iDescription, iPriority, iAdvice, iAdvicelink = iValues.split(',')
                    self.addIssueCategory(iId, IssueCategory(iId, iTitle, iDescription, iPriority, iAdvice, iAdvicelink, ''))
        file.close()

    ########################################
    security.declareProtected(view, 'menu_html')
    menu_html = PageTemplateFile('zpt/HelpDesk_menu', globals())

    security.declareProtected(view, 'style_html')
    style_html = PageTemplateFile('zpt/HelpDesk_style', globals())

    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/HelpDesk_index', globals())

    security.declareProtected(view, 'info_login_html')
    info_login_html = PageTemplateFile('zpt/HelpDesk_info_login', globals())

    security.declareProtected(PERMISSION_MANAGE_HELPDESK_SETTINGS, 'login_html')
    login_html = PageTemplateFile('zpt/HelpDesk_login', globals())

    security.declareProtected(PERMISSION_POST_ISSUES, 'add_issue_html')
    add_issue_html = PageTemplateFile('zpt/HelpDesk_add_issue', globals())

    security.declareProtected(PERMISSION_POST_ISSUES, 'add_issue_quick_html')
    add_issue_quick_html = PageTemplateFile('zpt/HelpDesk_add_issue_quick', globals())

    security.declareProtected(view, 'list_html')
    list_html = PageTemplateFile('zpt/HelpDesk_list', globals())

    security.declareProtected(view, 'error_html')
    error_html = PageTemplateFile('zpt/HelpDesk_error', globals())

    security.declareProtected(view_management_screens, 'admin_html')
    admin_html = PageTemplateFile('zpt/HelpDesk_admin', globals())

    security.declareProtected(view_management_screens, 'admin_settings_html')
    admin_settings_html = PageTemplateFile('zpt/HelpDesk_admin_settings', globals())

    security.declareProtected(view_management_screens, 'admin_catalog_html')
    admin_catalog_html = PageTemplateFile('zpt/HelpDesk_admin_catalog', globals())

    security.declareProtected(view_management_screens, 'admin_issue_priority_html')
    admin_issue_priority_html = PageTemplateFile('zpt/HelpDesk_admin_issue_priority', globals())

    security.declareProtected(view_management_screens, 'admin_issue_status_html')
    admin_issue_status_html = PageTemplateFile('zpt/HelpDesk_admin_issue_status', globals())

    security.declareProtected(view_management_screens, 'admin_issue_sendtype_html')
    admin_issue_sendtype_html = PageTemplateFile('zpt/HelpDesk_admin_issue_sendtype', globals())

    security.declareProtected(view_management_screens, 'admin_issue_category_html')
    admin_issue_category_html = PageTemplateFile('zpt/HelpDesk_admin_issue_category', globals())

    security.declareProtected(view_management_screens, 'admin_users_html')
    admin_users_html = PageTemplateFile('zpt/HelpDesk_admin_users', globals())

    security.declareProtected(view_management_screens, 'admin_users_ldap_form_html')
    admin_users_ldap_form_html = PageTemplateFile('zpt/HelpDesk_admin_users_ldap_form', globals())

    security.declareProtected(view_management_screens, 'admin_users_zope_form_html')
    admin_users_zope_form_html = PageTemplateFile('zpt/HelpDesk_admin_users_zope_form', globals())

    security.declareProtected(view_management_screens, 'admin_users_naaya_form_html')
    admin_users_naaya_form_html = PageTemplateFile('zpt/HelpDesk_admin_users_naaya_form', globals())

    security.declareProtected(view_management_screens, 'admin_presentation_html')
    admin_presentation_html = PageTemplateFile('zpt/HelpDesk_admin_presentation', globals())

    security.declareProtected(view_management_screens, 'admin_import_html')
    admin_import_html = PageTemplateFile('zpt/HelpDesk_admin_import', globals())

    security.declareProtected(view_management_screens, 'reports_form_html')
    reports_form_html = PageTemplateFile('zpt/HelpDesk_reports_form', globals())

    security.declareProtected(PERMISSION_MANAGE_HELPDESK_SETTINGS, 'reports_user_html')
    reports_user_html = PageTemplateFile('zpt/HelpDesk_reports_user', globals())

    security.declareProtected(view_management_screens, 'reports_manage_html')
    reports_manage_html = PageTemplateFile('zpt/HelpDesk_reports_manage', globals())

    #Declare permission defaults
    security.setPermissionDefault(PERMISSION_MANAGE_HELPDESK_SETTINGS, [HELPDESK_ROLE_ADMINISTRATOR, HELPDESK_ROLE_CONSULTANT])

#Initialize the HelpDesk class
InitializeClass(HelpDesk)


#################
#       GLOBAL STUFF    #
#################
_DATE_FORMATS = {
        '0':'dd/mm/yyyy',
        '1':'dd-mm-yyyy',
        '2':'mm/dd/yyyy',
        '3':'mm-dd-yyyy',
        '4':'yyyy/mm/dd',
        '5':'yyyy-mm-dd',
        '6':'dd mmm yyyy',
        '7':'dd month yyyy'
}
_DATE_MODELS = {
        '0':'%d/%m/%Y',
        '1':'%d-%m-%Y',
        '2':'%m/%d/%Y',
        '3':'%m-%d-%Y',
        '4':'%Y/%m/%d',
        '5':'%Y-%m-%d',
        '6':'%d %b %Y',
        '7':'%d %B %Y'
}
_TIME_MODEL = '%H:%M:%S'
_DEFAULT_DATE_FORMAT = '0'

_DEFAULT_ISSUES_PERPAGE = 25
_DEFAULT_ISSUE_SECURITY = ISSUE_SECURITY_PRIVATE
