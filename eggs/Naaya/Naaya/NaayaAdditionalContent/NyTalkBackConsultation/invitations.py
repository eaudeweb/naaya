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

from base64 import urlsafe_b64encode
from random import randrange

from BTrees.OOBTree import OOBTree
from Persistence import Persistent
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.User import BasicUserFolder, SimpleUser
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile
from constants import (PERMISSION_INVITE_TO_TALKBACKCONSULTATION,
                       PERMISSION_MANAGE_TALKBACKCONSULTATION)

class FormError(Exception):
    def __init__(self, errors):
        self.errors = errors

class InvitationsContainer(SimpleItem):
    security = ClassSecurityInfo()

    title = "Consultation invitations"

    def __init__(self, id):
        super(SimpleItem, self).__init__(id)
        self.id = id
        self._invites = OOBTree()

    _create_html = PageTemplateFile('zpt/invitations_create', globals())
    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'create')
    def create(self, REQUEST):
        """ Create an invitation, send e-mail """
        keys = ('name', 'email', 'organization', 'notes', 'message')
        formerrors = {}
        extra_opts = {}

        if REQUEST.REQUEST_METHOD == 'POST':
            do_preview = (REQUEST.form.get('do', '') == 'Preview')
            formdata = dict( (key, REQUEST.form.get(key, '')) for key in keys )

            auth_tool = self.getAuthenticationTool()
            inviter_userid = auth_tool.get_current_userid()
            inviter_name = auth_tool.name_from_userid(inviter_userid)

            kwargs = dict(formdata, web_form=True,
                          inviter_userid=inviter_userid,
                          inviter_name=inviter_name)

            try:
                if do_preview:
                    extra_opts.update(self._create_invitation(preview=True, **kwargs))
                    extra_opts['preview_attribution'] = '%s (invited by %s)' % \
                        (formdata['name'], inviter_name)
                else:
                    self._create_invitation(**kwargs)
                    self.setSessionInfo(['Invitation for %s '
                                         'has been sent.' %
                                            formdata['name']])
                    return REQUEST.RESPONSE.redirect(self.absolute_url() + '/create')
            except FormError, e:
                formerrors = dict(e.errors)

        else:
            formdata = dict( (key, '') for key in keys )

        return self._create_html(formdata=formdata, formerrors=formerrors,
                                 **extra_opts)

    _invite_email = EmailPageTemplateFile('zpt/invitations_email.zpt', globals())
    def _create_invitation(self, name, email, organization, notes, message,
                           inviter_userid, inviter_name,
                           web_form=False, preview=False):
        errors = []
        if not name:
            errors.append(('name', ValueError('Name is mandatory')))
        if not email:
            errors.append(('email', ValueError('Email is mandatory')))

        if errors:
            if web_form:
                raise FormError(errors)
            else:
                raise errors[0][1]

        key = random_key()
        keyed_url = self.absolute_url() + '/welcome?key=' + key

        kwargs = {
            'name': name,
            'consultation': self.get_consultation(),
            'keyed_url': keyed_url,
            'inviter_name': inviter_name,
            'inviter_message': message,
        }
        mail_data = self._invite_email.render_email(**kwargs)

        if preview:
            return {'preview_mail': mail_data}

        invitation = Invitation(inviter_userid, key, name, email, organization, notes)
        self._invites.insert(key, invitation)

        email_tool = self.getEmailTool()
        email_tool.sendEmail(mail_data['body_text'],
                             email, email_tool._get_from_address(),
                             mail_data['subject'])

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'index_html')
    def index_html(self, REQUEST):
        """ redirect to admin_html """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'admin_html')
    _admin_html = PageTemplateFile('zpt/invitations_admin', globals())
    def admin_html(self, REQUEST):
        """ the admin view """
        options = {
            'invites': self._invites.values(),
            'name_from_userid': self.getAuthenticationTool().name_from_userid,
        }
        return self._admin_html(**options)

    security.declareProtected(PERMISSION_MANAGE_TALKBACKCONSULTATION, 'admin_revoke_invitation')
    def admin_revoke_invitation(self, key, REQUEST=None):
        """ disable an invitation """
        invite = self._invites[key]
        invite.enabled = False
        if REQUEST is not None:
            self.setSessionInfo(['Invitation for %s has been revoked.' % invite.name])
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    _welcome_html = NaayaPageTemplateFile('zpt/invitations_welcome', globals(),
                                          'tbconsultation_invitations_welcome')
    security.declarePublic('welcome')
    def welcome(self, REQUEST):
        """ welcome page for invitees """

        key = REQUEST.get('key', None)
        invitation = self.get_invitation(key)

        if invitation is not None and invitation.enabled:
            auth_tool = self.getAuthenticationTool()
            inviter_name = auth_tool.name_from_userid(invitation.inviter_userid)
            REQUEST.SESSION.set('nytb-current-key', key)
        else:
            invitation = None
            inviter_name = ''

        return self._welcome_html(REQUEST,
                                  invitation=invitation,
                                  inviter_name=inviter_name)

    security.declarePrivate('get_current_invitation')
    def get_current_invitation(self, REQUEST):
        return self.get_invitation(REQUEST.SESSION.get('nytb-current-key', None))

    security.declarePrivate('get_invitation')
    def get_invitation(self, key):
        return self._invites.get(key, None)

InitializeClass(InvitationsContainer)

class Invitation(Persistent):
    def __init__(self, inviter_userid, key, name, email, organization, notes):
        self.inviter_userid = inviter_userid
        self.name = name
        self.email = email
        self.organization = organization
        self.notes = notes
        self.key = key
        self.enabled = True

class InvitationUsersTool(BasicUserFolder):
    def authenticate(self, name, password, request):
        # first try to authenticate using the site acl_users
        auth_tool = self.getSite().getAuthenticationTool()
        user = auth_tool.authenticate(name, password, request)
        if user is not None:
            return user

        # no user logged in; try with an invite key
        invitation = self.invitations.get_current_invitation(request)
        if invitation is not None and invitation.enabled:
            return SimpleUser('invited_reviewer', '', ('InvitedReviewer',), [])
        else:
            return None

InitializeClass(InvitationUsersTool)

def random_key():
    """ generate a 120-bit random key, expressed as 20 base64 characters """
    return urlsafe_b64encode(''.join(chr(randrange(256)) for i in xrange(15)))
