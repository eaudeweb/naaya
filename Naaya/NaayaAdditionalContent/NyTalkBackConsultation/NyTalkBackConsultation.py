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
# David Batranu, Eau de Web
# Alex Morega, Eau de Web


#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from OFS.Image import cookId

#Product imports
from Products.NaayaContent.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyImageContainer import NyImageContainer
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties
from constants import *

#Chapter
from Chapter import addChapter
from Chapter import addChapter_html

#module constants

METATYPE_OBJECT = METATYPE_TALKBACKCONSULTATION
LABEL_OBJECT = 'TalkBack Consultation'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya TalkBack Consultation objects'
OBJECT_FORMS = []
OBJECT_CONSTRUCTORS = ['manage_addNyTalkBackConsultation_html',
                       'talkbackconsultation_add_html',
                       'addNyTalkBackConsultation']
OBJECT_ADD_FORM = 'talkbackconsultation_add_html'
DESCRIPTION_OBJECT = 'This is Naaya TalkBack Consultation type.'
PREFIX_OBJECT = 'tbcns'
ADDITIONAL_STYLE = PageTemplateFile('zpt/talkbackconsultation_style', globals()).read()
PROPERTIES_OBJECT = {
    'id':                  (0, '', ''),
    'title':               (1,
                            MUST_BE_NONEMPTY,
                            'The Title field must have a value.'),

    'description':         (0, '', ''),
    'start_date':          (0,
                            MUST_BE_DATETIME,
                            'The Start Date field must contain a valid date.'),

    'end_date':            (0,
                            MUST_BE_DATETIME,
                            'The End Date field must contain a valid date.'),

    'sortorder':           (0,
                            MUST_BE_POSITIV_INT,
                            'The Sort order field must contain a positive integer.'),

    'releasedate':         (0,
                            MUST_BE_DATETIME,
                            'The Release date field must contain a valid date.'),
    'allow_file':          (0, '', ''),
    'public_registration': (0, '', ''),
    'lang':                (0, '', '')
}

manage_addNyTalkBackConsultation_html = PageTemplateFile(
    'zpt/talkbackconsultation_manage_add', globals()
)
manage_addNyTalkBackConsultation_html.kind = METATYPE_TALKBACKCONSULTATION
manage_addNyTalkBackConsultation_html.action = 'addNyTalkBackConsultation'

talkbackconsultation_add_html = PageTemplateFile(
    'zpt/talkbackconsultation_add', globals()
)

def addNyTalkBackConsultation(self,
                              id='',
                              title='',
                              description='',
                              sortorder='',
                              start_date='',
                              end_date='',
                              public_registration='',
                              allow_file='',
                              contributor=None,
                              releasedate='',
                              lang=None,
                              REQUEST=None,
                              **kwargs):
    """
    Create a Naaya TalkBack Consultation type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER

    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'talkbackconsultation_manage_add' or \
           l_referer.find('talkbackconsultation_manage_add') != -1) and REQUEST:
        r = self.getSite().\
          check_pluggable_item_properties(
              METATYPE_TALKBACKCONSULTATION,
              id=id,
              title=title,
              sortorder=sortorder,
              start_date=start_date,
              end_date=end_date,
              public_registration=public_registration)
    else:
        r = []
    if not len(r):
        auth_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        #process parameters
        if contributor is None:
            contributor = auth_user
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, auth_user
        else:
            approved, approved_by = 0, None
        releasedate = self.process_releasedate(releasedate)
        if lang is None: lang = self.gl_get_selected_language()
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None) is not None:
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NyTalkBackConsultation(id,
                                    title,
                                    description,
                                    sortorder,
                                    start_date,
                                    end_date,
                                    public_registration,
                                    allow_file, contributor,
                                    releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(
            self.processDynamicProperties(METATYPE_TALKBACKCONSULTATION, REQUEST, kwargs),
            lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.submitThis()
        ob.approveThis(approved, approved_by)
        ob.updateRequestRoleStatus(public_registration, lang)
        ob.checkReviewerRole()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #log post date
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'talkbackconsultation_manage_add' or \
               l_referer.find('talkbackconsultation_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'talkbackconsultation_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect(
                    '%s/messages_html' % self.absolute_url()
                )
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(
                METATYPE_TALKBACKCONSULTATION,
                id=id,
                title=title,
                description=description,
                sortorder=sortorder,
                releasedate=releasedate,
                start_date=start_date,
                end_date=end_date,
                allow_file=allow_file,
                public_registration=public_registration,
                lang=lang
            )
            REQUEST.RESPONSE.redirect(
                '%s/talkbackconsultation_add_html' % self.absolute_url()
            )
        else:
            raise Exception, '%s' % ', '.join(r)

class NyTalkBackConsultation(NyAttributes,
                             Implicit,
                             NyProperties,
                             NyContainer,
                             NyCheckControl,
                             NyValidation,
                             utils):
    """ """

    meta_type = METATYPE_TALKBACKCONSULTATION
    meta_label = LABEL_OBJECT

    all_meta_types = ()

    icon = 'misc_/NaayaContent/NyTalkBackConsultation.gif'
    icon_marked = 'misc_/NaayaContent/NyTalkBackConsultation_marked.gif'

    title = LocalProperty('title')
    description = LocalProperty('description')

    security = ClassSecurityInfo()

    def __init__(self,
                 id,
                 title,
                 description,
                 sortorder,
                 start_date,
                 end_date,
                 public_registration,
                 allow_file,
                 contributor,
                 releasedate,
                 lang):
        """ """


        self.id = id
        self.contributor = contributor
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyContainer.__dict__['__init__'](self)
        self.save_properties(title,
                             description,
                             sortorder,
                             start_date,
                             end_date,
                             public_registration,
                             allow_file,
                             releasedate,
                             lang)

        NyProperties.__dict__['__init__'](self)
        self.submitted = 1

    security.declarePrivate('save_properties')
    def save_properties(self,
                        title,
                        description,
                        sortorder,
                        start_date,
                        end_date,
                        public_registration,
                        allow_file,
                        releasedate,
                        lang):

        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)

        if not hasattr(self, 'imageContainer'):
            self.imageContainer = NyImageContainer(self, True)

        if start_date:
            self.start_date = self.utConvertStringToDateTimeObj(start_date)
        else:
            self.start_date = self.utGetTodayDate()

        if end_date:
            self.end_date = self.utConvertStringToDateTimeObj(end_date)
        else:
            self.end_date = self.utGetTodayDate()

        try: self.sortorder = abs(int(sortorder))
        except: self.sortorder = DEFAULT_SORTORDER

        self.releasedate = releasedate
        self.public_registration = public_registration
        self.allow_file = allow_file

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'saveProperties')
    def saveProperties(self,
                       title='',
                       description='',
                       sortorder='',
                       start_date='',
                       end_date='',
                       public_registration='',
                       allow_file='',
                       lang='',
                       REQUEST=None):
        """ """


        if not title:
            self.setSession('title', title)
            self.setSession('description', description)
            self.setSessionErrors(['The Title field must have a value.'])
            if REQUEST:
                return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise ValueError('The title field must have a value.')

        releasedate = self.releasedate
        self.updateRequestRoleStatus(public_registration, lang)
        self.save_properties(title, description, sortorder, start_date, end_date, public_registration, allow_file, releasedate, lang)

        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'updateRequestRoleStatus')
    def updateRequestRoleStatus(self, public_registration, lang):
        """ Allow public registration for this consultation """
        if public_registration: self.updateDynamicProperties(self.processDynamicProperties(METATYPE_TALKBACKCONSULTATION, {'show_contributor_request_role': 'on'}), lang)
        if not public_registration: self.updateDynamicProperties(self.processDynamicProperties(METATYPE_TALKBACKCONSULTATION, {'show_contributor_request_role': ''}), lang)

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'checkReviewerRole')
    def checkReviewerRole(self):
        """
        Checks if the 'Reviewer' role exists,
        creates and adds review permissions if it doesn't exist
        """


        auth_tool = self.getAuthenticationTool()
        roles = auth_tool.list_all_roles()
        PERMISSION_GROUP = 'Review content'

        if PERMISSION_GROUP not in auth_tool.listPermissions().keys():
            auth_tool.addPermission(PERMISSION_GROUP, 'Allow posting reviews/comments to consultation objects.', [PERMISSION_REVIEW_TALKBACKCONSULTATION])
        else:
            permissions = auth_tool.getPermission(PERMISSION_GROUP).get('permissions', [])
            if PERMISSION_REVIEW_TALKBACKCONSULTATION not in permissions:
                permissions.append(PERMISSION_REVIEW_TALKBACKCONSULTATION)
                auth_tool.editPermission(PERMISSION_GROUP, 'Allow posting reviews/comments to consultation objects.', permissions)

        if 'Reviewer' not in roles:
            auth_tool.addRole('Reviewer', [PERMISSION_GROUP])
        else:
            role_permissions = auth_tool.getRolePermissions('Reviewer')
            if PERMISSION_GROUP not in role_permissions:
                role_permissions.append(PERMISSION_GROUP)
                auth_tool.editRole('Reviewer', role_permissions)

        #give permissions to administrators
        admin_permissions = self.permissionsOfRole('Administrator')
        site = self.getSite()
        if PERMISSION_MANAGE_TALKBACKCONSULTATION not in admin_permissions:
            site.manage_permission(PERMISSION_MANAGE_TALKBACKCONSULTATION, ('Administrator', ), acquire=1)
            site.manage_permission(PERMISSION_REVIEW_TALKBACKCONSULTATION, ('Administrator', ), acquire=1)

    security.declareProtected(view, 'get_start_date')
    def get_start_date(self):
        """ Returns the start date in dd/mm/yyyy string format. """

        return self.utConvertDateTimeObjToString(self.start_date)

    security.declareProtected(view, 'get_end_date')
    def get_end_date(self):
        """ Returns the end date in dd/mm/yyyy string format. """

        return self.utConvertDateTimeObjToString(self.end_date)

    security.declareProtected(view, 'get_days_left')
    def get_days_left(self):
        """ Returns the remaining days for the consultation or the number of days before it starts """

        today = self.utGetTodayDate().earliestTime()
        if not self.start_date or not self.end_date:
            return (1, 0)

        if self.start_date.lessThanEqualTo(today):
            return (1, int(str(self.end_date - today).split('.')[0]))
        else:
            return (0, int(str(self.start_date - today).split('.')[0]))

    security.declareProtected(view_management_screens, 'manage_options')
    def manage_options(self):
        """ """

        l_options = (NyContainer.manage_options[0],)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyContainer.manage_options[3:8]
        return l_options

    #security.declareProtected(PERMISSION_REVIEW_TALKBACKCONSULTATION, 'addComment')
    #def addComment(self, title='', contributor_name='', message='', file='', REQUEST=None):
        #""" """

        #if not title or not contributor_name or not message:
            #self.setSession('title', title)
            #self.setSession('contributor_name', contributor_name)
            #self.setSession('message', message)
            #self.setSessionErrors(['Fill in all mandatory fields.'])
            #return REQUEST.RESPONSE.redirect(self.absolute_url() + '/add_talkbackconsultation_comment')

        #contributor = REQUEST.AUTHENTICATED_USER.getUserName()
        #if not self.allow_file: file = ''
        #days = self.get_days_left()

        #if days[0] == 1 and days[1] > 0:
            #if not self.check_contributor_comment(contributor):
                #addTalkBackConsultationComment(self, title, contributor, contributor_name, message, file, REQUEST)
            #else:
                #return REQUEST.RESPONSE.redirect(self.absolute_url() + '/add_talkbackconsultation_comment?status=failed')
        #elif days[0] ==1 and days[1] <= 0:
            #return REQUEST.RESPONSE.redirect(self.absolute_url() + '/add_talkbackconsultation_comment?status=late')
        #elif days[0] <= 0:
            #return REQUEST.RESPONSE.redirect(self.absolute_url() + '/add_talkbackconsultation_comment?status=soon')

    def checkTalkBackConsultationUser(self):
        """
        Checks if the user is logged in and has reviewer rights:
        0 if user is anonymous,
        1 if user has reviewer role
        2 if user doesn't have reviewer role
        """
        review_check = self.checkPermissionReviewTalkBackConsultation()

        if self.isAnonymousUser(): return 0
        elif review_check: return 1
        elif not review_check: return 2

    #permissions
    def checkPermissionReviewTalkBackConsultation(self):
        """
        Check for reviewing the TalkBack Consultation.
        """
        return self.checkPermission(PERMISSION_REVIEW_TALKBACKCONSULTATION)

    def checkPermissionManageTalkBackConsultation(self):
        """
        Check for managing the TalkBack Consultation.
        """
        return self.checkPermission(PERMISSION_MANAGE_TALKBACKCONSULTATION)











###################################
######TalkBack section, move to top
###################################


    def add_chapter(self, title='', body='',  REQUEST=None):
        """ """
        addChapter(self, title=title, body=body)
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    def list_chapters(self):
        """ """
        return self.objectValues([METATYPE_TALKBACKCONSULTATION_CHAPTER])

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/talkbackconsultation_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/talkbackconsultation_index', globals())

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'edit_html')
    edit_html = PageTemplateFile('zpt/talkbackconsultation_edit', globals())

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'chapter_add_html')
    chapter_add_html = addChapter_html

InitializeClass(NyTalkBackConsultation)
