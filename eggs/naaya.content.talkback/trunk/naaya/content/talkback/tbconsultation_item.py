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

# Python imports
import os
import sys
import operator
from copy import deepcopy

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from App.ImageFile import ImageFile
from DateTime import DateTime
from zope.event import notify

# Product imports
from Products.Naaya.NyFolderBase import NyFolderBase
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.managers.utils import utils, slugify, uniqueId
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyNonCheckControl import NyNonCheckControl
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyContentType import (NyContentType, NyContentData,
                                              NY_CONTENT_BASE_SCHEMA)
from Products.NaayaBase.NyProperties import NyProperties
from constants import *
from Products.NaayaBase.NyRoleManager import NyRoleManager
from Products.NaayaBase.NyAccess import NyAccess
from Products.NaayaCore.LayoutTool.LayoutTool import AdditionalStyle
from naaya.core import submitter
from naaya.core.zope2util import DT2dt
from naaya.core.zope2util import abort_transaction_keep_session
from naaya.content.base.events import NyContentObjectAddEvent
from naaya.content.base.events import NyContentObjectEditEvent

# local imports
from Section import addSection
from Section import addSection_html
from invitations import InvitationsContainer, InvitationUsersTool
from comments_admin import CommentsAdmin
from permissions import (PERMISSION_ADD_TALKBACK_CONSULTATION,
                         PERMISSION_REVIEW_TALKBACKCONSULTATION,
                         PERMISSION_REVIEW_TALKBACKCONSULTATION_AFTER_DEADLINE,
                         PERMISSION_MANAGE_TALKBACKCONSULTATION,
                         PERMISSION_INVITE_TO_TALKBACKCONSULTATION)

# module constants

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

DEFAULT_SCHEMA = deepcopy(NY_CONTENT_BASE_SCHEMA)
DEFAULT_SCHEMA.update({
    'start_date': {
        "sortorder": 100,
        "widget_type": "Date",
        "data_type": 'date',
        "label": "First day",
    },
    'end_date': {
        "sortorder": 110,
        "widget_type": "Date",
        "data_type": 'date',
        "label": "Last day",
    },
    'public_registration': {
        "sortorder": 120,
        "widget_type": "Checkbox",
        "label": "Allow users to register as reviewers for this consultation",
        "data_type": "bool",
        "default": False,
    },
    'allow_file': {
        "sortorder": 130,
        "widget_type": "Checkbox",
        "label": "Allow reviewers to upload files when posting a comment",
        "data_type": "bool",
        "default": False,
    },
    'allow_reviewer_invites': {
        "sortorder": 140,
        "widget_type": "Checkbox",
        "label": "Allow reviewers to invite other people to review",
        "data_type": "bool",
        "default": False,
    },
    'show_contributor_request_role': {
        "sortorder": 150,
        "widget_type": "Checkbox",
        "label": "Allow reviewers to invite other people to review",
        "data_type": "bool",
        "default": False,
        "visible": False,
    },
})
DEFAULT_SCHEMA['coverage']['visible'] = False
DEFAULT_SCHEMA['keywords']['visible'] = False
DEFAULT_SCHEMA['sortorder']['visible'] = False
DEFAULT_SCHEMA['sortorder']['sortorder'] = 115  # Show sortorder in edit form
DEFAULT_SCHEMA['releasedate']['visible'] = False
DEFAULT_SCHEMA['discussion']['visible'] = False

# this dictionary is updated at the end of the module
config = {
    'product': 'NaayaContent',
    'module': 'tbconsultation_item',
    'package_path': os.path.abspath(os.path.dirname(__file__)),
    'meta_type': METATYPE_TALKBACKCONSULTATION,
    'label': 'TalkBack Consultation',
    'permission': PERMISSION_ADD_TALKBACK_CONSULTATION,
    'forms': [],
    'add_form': 'talkbackconsultation_add_html',
    'description': 'This is Naaya TalkBack Consultation type.',
    'default_schema': DEFAULT_SCHEMA,
    'schema_name': METATYPE_TALKBACKCONSULTATION,
    'import_string': '',
    '_module': sys.modules[__name__],
    'additional_style': AdditionalStyle('www/talkbackconsultation_style.css',
                                        globals()),
    'icon': os.path.join(os.path.dirname(__file__), 'www',
                         'NyTalkBackConsultation.gif'),
    '_misc': {
        'NyTalkBackConsultation.gif': ImageFile(
            'www/NyTalkBackConsultation.gif', globals()),
        'NyTalkBackConsultation_marked.gif': ImageFile(
            'www/NyTalkBackConsultation_marked.gif', globals()),
        'tb-editor.css': ImageFile('www/tb-editor.css', globals()),
    },
    }

talkbackconsultation_add = NaayaPageTemplateFile(
    'zpt/talkbackconsultation_add', globals(), 'tbconsultation_add')


def talkbackconsultation_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({
        'here': self,
        'kind': config['meta_type'],
        'action': 'addNyTalkBackConsultation',
        'form_helper': form_helper,
        'submitter_info_html': submitter.info_html(self, REQUEST),
        },
        'tbconsultation_add')


def _create_NyTalkBackConsultation_object(parent, id, contributor):
    """ Creates a consultation object and returns it """
    ob = NyTalkBackConsultation(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob


def addNyTalkBackConsultation(self, id='', REQUEST=None, contributor=None,
                              **kwargs):
    """
    Create a Naaya TalkBack Consultation type of object.
    """
    l_referer = '/'
    if REQUEST is not None:
        l_referer = REQUEST.get('HTTP_REFERER', '/').split('/')[-1]
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(
        schema_raw_data.pop('releasedate', ''))

    id = uniqueId(slugify(id or schema_raw_data.get('title', ''),
                          removelist=[]),
                  lambda x: self._getOb(x, None) is not None)
    if contributor is None:
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyTalkBackConsultation_object(self, id, contributor)
    form_errors = ob.process_submitted_form(schema_raw_data, _lang,
                                            _override_releasedate=_releasedate)
    if REQUEST is not None:
        submitter_errors = submitter.info_check(self, REQUEST, ob)
        form_errors.update(submitter_errors)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1])  # pick a random error
        else:
            abort_transaction_keep_session(REQUEST)
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect(l_referer)

    self.setSessionInfoTrans("TalkBack Consultation object created")
    # process parameters
    if self.checkPermissionSkipApproval():
        approved, approved_by = (1,
                                 self.REQUEST.AUTHENTICATED_USER.getUserName())
    else:
        approved, approved_by = 0, None

    ob.approveThis(approved, approved_by)
    ob.submitThis()

    ob.show_contributor_request_role = ob.public_registration
    self.recatalogNyObject(ob)

    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))

    # log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    # redirect if case
    if REQUEST is not None:
        if (l_referer == 'talkbackconsultation_add' or
                l_referer.find('talkbackconsultation_manage_add') != -1):
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'talkbackconsultation_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    return ob.getId()


class NyTalkBackConsultation(Implicit, NyContentData, NyContentType,
                             NyAttributes, NyProperties, NyRoleManager,
                             NyContainer, NyNonCheckControl, utils,
                             NyFolderBase):
    """ """

    meta_type = METATYPE_TALKBACKCONSULTATION
    meta_label = LABEL_OBJECT

    meta_types = [
        {'name': METATYPE_TALKBACKCONSULTATION_SECTION, 'action': 'addSection',
            'permission': PERMISSION_MANAGE_TALKBACKCONSULTATION},
    ]

    icon = 'misc_/NaayaContent/NyTalkBackConsultation.gif'
    icon_marked = 'misc_/NaayaContent/NyTalkBackConsultation_marked.gif'

    security = ClassSecurityInfo()

    edit_access = NyAccess('edit_access', {
        PERMISSION_REVIEW_TALKBACKCONSULTATION: "Submit comments",
        PERMISSION_MANAGE_TALKBACKCONSULTATION: "Administer consultation",
        PERMISSION_INVITE_TO_TALKBACKCONSULTATION: "Send invitations",
    })

    section_sort_order = tuple()

    def __init__(self, id, contributor):
        """ """
        self.id = id
        self.contributor = contributor
        NyContainer.__dict__['__init__'](self)
        NyProperties.__dict__['__init__'](self)
        self.invitations = InvitationsContainer('invitations')
        self.submitted = 1

    def set_allow_reviewer_invites(self, allow):
        perm = '_Naaya___Invite_to_TalkBack_Consultation_Permission'
        roles = getattr(self, perm, [])

        if allow and 'Reviewer' not in roles:
            new_roles = roles + ('Reviewer',)
        elif not allow and 'Reviewer' in roles:
            new_roles = tuple(role for role in roles if role != 'Reviewer')
        else:
            new_roles = roles

        if new_roles:
            setattr(self, perm, new_roles)
        else:
            if hasattr(self, perm):
                delattr(self, perm)

    def get_allow_reviewer_invites(self):
        perm = '_Naaya___Invite_to_TalkBack_Consultation_Permission'
        roles = getattr(self, perm, [])
        return ('Reviewer' in roles)

    allow_reviewer_invites = property(get_allow_reviewer_invites,
                                      set_allow_reviewer_invites)

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'saveProperties')

    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED(EXCEPTION_NOTAUTHORIZED_MSG)

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
        _releasedate = self.process_releasedate(
            schema_raw_data.pop('releasedate', ''), self.releasedate)

        form_errors = self.process_submitted_form(
            schema_raw_data, _lang, _override_releasedate=_releasedate)

        if not form_errors:
            self._p_changed = True
            self.recatalogNyObject(self)
            # log date
            contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            notify(NyContentObjectEditEvent(self, contributor))
            if REQUEST:
                self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                         date=self.utGetTodayDate())
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' %
                                          (self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors,
                                             schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' %
                                          (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1])  # pick an error

    security.declareProtected(view, 'get_consultation')

    def get_consultation(self):
        return self

    security.declareProtected(view, 'list_sections')

    def list_sections(self):
        """ """
        metatypes = [METATYPE_TALKBACKCONSULTATION_SECTION]
        sections = dict(self.objectItems(metatypes))

        output = []
        for section_id in self.section_sort_order:
            if section_id in sections:
                output.append(sections.pop(section_id))

        output.extend(sorted(sections.values(),
                             key=operator.attrgetter('title')))

        return output

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'save_sort_order')

    def save_sort_order(self, sort_section_id, REQUEST=None):
        """ save the sort order of sections """
        self.section_sort_order = tuple(sort_section_id)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url())

    _comments_atom = NaayaPageTemplateFile('zpt/comments_atom', globals(),
                                           'tbconsultation_comments_atom')
    security.declareProtected(view, 'comments_atom')

    def comments_atom(self, REQUEST=None, days=2):
        """ ATOM feed with consultation comments """

        if isinstance(days, basestring):
            try:
                days = int(days)
            except:
                days = 2

        cutoff = DateTime() - days
        comments_list = []
        for section in self.list_sections():
            for paragraph in section.get_paragraphs():
                for comment in paragraph.get_comments():
                    if comment.comment_date < cutoff:
                        continue
                    comments_list.append(comment)
        comments_list.sort(key=operator.attrgetter('comment_date'),
                           reverse=True)

        if comments_list:
            feed_updated = comments_list[0].comment_date
        else:
            feed_updated = DateTime()

        def atom_date_format(date):
            d = DT2dt(date).strftime('%Y-%m-%dT%H:%M:%S%z')
            return d[:-2] + ':' + d[-2:]

        if REQUEST is not None:
            REQUEST.RESPONSE.setHeader('Content-Type', 'application/atom+xml')

        return self._comments_atom(comments_list=comments_list,
                                   atom_date_format=atom_date_format,
                                   feed_updated=feed_updated)

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
        """ Returns the remaining days for the consultation
        or the number of days before it starts """
        today = self.utGetTodayDate().earliestTime()
        if not self.start_date or not self.end_date:
            return (1, 0)

        after_end_date = self.end_date + 1
        if self.start_date.lessThanEqualTo(today):
            return (1, int(str(after_end_date - today).split('.')[0]))
        else:
            return (0, int(str(self.start_date - today).split('.')[0]))

    security.declareProtected(view_management_screens, 'manage_options')

    def manage_options(self):
        """ """

        l_options = (NyContainer.manage_options[0],)
        l_options += ({'label': 'View', 'action': 'index_html'},) + \
            NyContainer.manage_options[3:8]
        return l_options

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'delete_sections')

    def delete_sections(self, del_section_id, REQUEST=None):
        """ remove the specified sections """
        self.manage_delObjects(list(del_section_id))
        self.setSessionInfoTrans('Removed ${count} sections.',
                                 count=str(len(del_section_id)))
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url())

    def get_user_name(self):
        # first, check if we have an invite key
        invitation = self.invitations.get_current_invitation(self.REQUEST)
        if invitation is not None:
            return invitation.name

        # no invite key; look for current Zope user
        auth_tool = self.getAuthenticationTool()
        userid = auth_tool.get_current_userid()

        if userid is None:  # anonymous user
            return None

        name = auth_tool.name_from_userid(userid)
        if name == '':
            name = userid
        return name

    def get_user_name_or_userid(self, userid=None):
        if userid is None:
            return self.get_user_name()

        auth_tool = self.getAuthenticationTool()
        name = auth_tool.name_from_userid(userid)
        if name == '':
            name = userid

        return name

    def checkTalkBackConsultationUser(self):
        """
        Checks if the user is logged in and has reviewer rights:
        0 if user is anonymous,
        1 if user has reviewer role
        2 if user doesn't have reviewer role
        """
        review_check = self.checkPermissionReviewTalkBackConsultation()

        if self.isAnonymousUser():
            return 0
        elif review_check:
            return 1
        elif not review_check:
            return 2

    security.declareProtected(view, 'check_cannot_comment')

    def check_cannot_comment(self):
        """ """

        if not self.checkPermissionReviewTalkBackConsultation():
            if self.isAnonymousUser():
                return 'not-logged-in'
            else:
                return 'no-permission'

        if self.get_days_left()[1] <= 0 and not (
                self.checkPermissionManageTalkBackConsultation() or
                self.checkPermissionReviewTalkBackConsultationAfterDeadline()):
            return 'deadline-reached'

    security.declareProtected(
        PERMISSION_COMMENTS_ADD, 'log_in_authenticated')

    def log_in_authenticated(self, REQUEST=None):
        """ Log in user and redirect to TalkBack Consultation index """
        if REQUEST is not None:
            self.REQUEST.RESPONSE.redirect(self.absolute_url())

    # permissions
    def checkPermissionReviewTalkBackConsultation(self):
        """
        Check for reviewing the TalkBack Consultation.
        """
        return self.checkPermission(PERMISSION_REVIEW_TALKBACKCONSULTATION)

    security.declareProtected(
        PERMISSION_REVIEW_TALKBACKCONSULTATION_AFTER_DEADLINE,
        'review_after_deadline')

    def review_after_deadline(self):
        """
        Dummy function to register the permission.
        """
        raise NotImplementedError

    def checkPermissionReviewTalkBackConsultationAfterDeadline(self):
        """
        Check for reviewing the TalkBack Consultation
        after the deadline has passed.
        """
        return self.checkPermission(
            PERMISSION_REVIEW_TALKBACKCONSULTATION_AFTER_DEADLINE)

    def checkPermissionManageTalkBackConsultation(self):
        """
        Check for managing the TalkBack Consultation.
        """
        return self.checkPermission(PERMISSION_MANAGE_TALKBACKCONSULTATION)

    def checkPermissionInviteToTalkBackConsultation(self):
        """
        Check for inviting others to the TalkBack Consultation.
        """
        return self.checkPermission(PERMISSION_INVITE_TO_TALKBACKCONSULTATION)

    def own_comments(self):
        """
        Check if the current user has any comments on the consultation
        """
        return [comment for comment in self.admin_comments._all_comments()
                if comment['comment'].contributor ==
                self.REQUEST.AUTHENTICATED_USER.getUserName()]

    security.declareProtected(view, 'custom_editor')

    def custom_editor(self, editor_tool, lang, dom_id):
        extra_options = {
            'content_css':
                self.absolute_url() + '/misc_/NaayaContent/tb-editor.css',
            'theme_advanced_buttons1':
                'bold,italic,underline,strikethrough,sub,sup,forecolor,'
                'backcolor,removeformat,separator,'
                'bullist,numlist,separator,'
                'justifyleft,justifycenter,justifyright,justifyfull,separator,'
                'link,unlink,hr,image,separator,'
                'pastetext,pasteword,cleanup,code,help',
            'theme_advanced_buttons2': '',
        }
        return editor_tool.render(dom_id, lang, image_support=True,
                                  extra_options=extra_options)

    security.declareProtected(view, 'get_files')

    def get_files(self):
        """ Get a list of all files attached to the consultation"""
        return [ob for ob in self.objectValues('Naaya Blob File')]

    addSection = addSection

    # zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/talkbackconsultation_manage_edit',
                                        globals())

    # site pages
    security.declareProtected(view, 'index_html')
    index_html = NaayaPageTemplateFile('zpt/talkbackconsultation_index',
                                       globals(), 'tbconsultation_index')

    # standard_template_macro, header and footer templates are proxied
    # since invited reviewers have "View" permission only in this folder;
    # if the consultation is restricted, they would not be able to see
    # consultation pages.
    def standard_html_header(self, *args, **kwargs):
        return self.aq_parent.standard_html_header(*args, **kwargs)

    def standard_html_footer(self, *args, **kwargs):
        return self.aq_parent.standard_html_footer(*args, **kwargs)

    def standard_template_macro(self, *args, **kwargs):
        return self.aq_parent.standard_template_macro(*args, **kwargs)

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'edit_html')
    edit_html = NaayaPageTemplateFile('zpt/talkbackconsultation_edit',
                                      globals(), 'tbconsultation_edit')

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION,
                              'section_add_html')
    section_add_html = addSection_html

    __allow_groups__ = InvitationUsersTool()
    _View_Permission = ['InvitedReviewer']
    _Naaya___Review_TalkBack_Consultation_Permission = ['InvitedReviewer']
    __ac_roles__ = ['InvitedReviewer']

    admin_comments = CommentsAdmin('admin_comments')

InitializeClass(NyTalkBackConsultation)
manage_addNyTalkBackConsultation_html = PageTemplateFile(
    'zpt/talkbackconsultation_manage_add', globals())
manage_addNyTalkBackConsultation_html.kind = METATYPE_TALKBACKCONSULTATION
manage_addNyTalkBackConsultation_html.action = 'addNyTalkBackConsultation'

config.update({
    'constructors': (manage_addNyTalkBackConsultation_html,
                     addNyTalkBackConsultation),
    'folder_constructors': [
        ('manage_addNyTalkBackConsultation_html',
         manage_addNyTalkBackConsultation_html),
        ('talkbackconsultation_add_html', talkbackconsultation_add_html),
        ('addNyTalkBackConsultation', addNyTalkBackConsultation),
    ],
    'add_method': addNyTalkBackConsultation,
    'validation': issubclass(NyTalkBackConsultation, NyValidation),
    '_class': NyTalkBackConsultation,
})


def get_config():
    return config
