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
from datetime import date
import xlrd

from BTrees.OOBTree import OOBTree
from Persistence import Persistent
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.User import BasicUserFolder, SimpleUser
from OFS.SimpleItem import SimpleItem

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile
from permissions import (PERMISSION_INVITE_TO_TALKBACKCONSULTATION,
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

    _create_html = NaayaPageTemplateFile('zpt/invitations_create', globals(),
                                         'tbconsultation_invitations_create')
    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'create')
    def create(self, REQUEST):
        """ Create an invitation, send e-mail """
        keys = ('name', 'email', 'organization', 'notes', 'message')
        formerrors = {}
        previews = []

        if REQUEST.REQUEST_METHOD == 'POST':
            do_preview = (REQUEST.form.get('do', '') == 'Preview')

            inviter_userid, inviter_name = self._get_inviter_info()

            formdata = dict( (key, REQUEST.form.get(key, '')) for key in keys )
            kwargs = dict(formdata, web_form=True,
                          inviter_userid=inviter_userid,
                          inviter_name=inviter_name)

            try:
                if do_preview:
                    preview = self._send_invitation(preview=True, **kwargs)
                    preview['preview_attribution'] = '%s (invited by %s)' % \
                        (formdata['name'], inviter_name)
                    previews.append(preview)
                else:
                    self._send_invitation(**kwargs)
                    self.setSessionInfoTrans('Invitation for ${name} '
                                             'has been sent.',
                                             name=formdata['name'])
                    return REQUEST.RESPONSE.redirect(self.absolute_url() + '/create')
            except FormError, e:
                self.setSessionErrorsTrans('The form contains errors. Please '
                                           'correct them and try again.')
                formerrors = dict(e.errors)

        else:
            formdata = dict( (key, '') for key in keys )

        return self._create_html(formdata=formdata, formerrors=formerrors,
                                 previews=previews)

    def bulk_create(self, REQUEST):
        """ Same as `create`, but input is an xls file """
        keys = ('name', 'email', 'organization', 'notes', 'message')
        previews = []
        if REQUEST.REQUEST_METHOD == 'POST':
            do_preview = (REQUEST.form.get('do', '') == 'Preview')

            inviter_userid, inviter_name = self._get_inviter_info()

            try:
                xls = REQUEST.form.get('input_file')
                spreadsheet = xlrd.open_workbook(file_contents=xls.read())
                sheet = spreadsheet.sheet_by_index(0)
            except Exception, e:
                self.setSessionErrorsTrans('Error reading the spreadsheet.')
            else:
                assert sheet.ncols == 5, "Expected sheet with 5 columns"
                header = sheet.row(0)
                assert ([x.value.strip() for x in header] ==
                    ['Name', 'Email', 'Organization', 'Notes', 'Message']),\
                    "Unexpected table header in spreadsheet"

                # on behalf situation
                on_behalf_uid = REQUEST.form.get('on_behalf', '')
                if on_behalf_uid != '':
                    auth_tool = self.getAuthenticationTool()
                    on_behalf_name = auth_tool.name_from_userid(on_behalf_uid)
                    if on_behalf_name:
                        # valid UID, overwriting the inviter
                        inviter_userid, inviter_name = on_behalf_uid, on_behalf_name
                    else:
                        # UID is '', therefore it does not exist
                        self.setSessionErrorsTrans('UID not found')
                        return self._create_html(formdata=dict( (key, '') for key in keys ),
                                                 formerrors={}, previews=previews)

                errors = []
                for i in range(1, sheet.nrows):
                    cells = sheet.row(i)
                    clean_it = lambda x: x.value.strip()
                    formdata = dict( (key, clean_it(cells[i])) for (i, key) in enumerate(keys))

                    kwargs = dict(formdata, web_form=True,
                          inviter_userid=inviter_userid,
                          inviter_name=inviter_name)
                    try:
                        if do_preview:
                            preview = self._send_invitation(preview=True, **kwargs)
                            preview['preview_attribution'] = '%s (invited by %s)' % \
                                (formdata['name'], inviter_name)
                            previews.append(preview)
                        else:
                            self._send_invitation(**kwargs)
                            # todo: ugly quick fix
                            existing = self.getSessionInfo() or ['']
                            self.setSessionInfoTrans('Invitation for ${name} '
                                                     'has been sent.',
                                                     name=formdata['name'])
                            self.setSessionInfo([existing[0] + '\n' + self.getSessionInfo()[0]])
                    except FormError, e:
                        errors.append('Error creating invitation for line #%d in spreadsheet: %r'
                                                   % ((i+1), [ (x[0], x[1].args) for x in e.errors]))
                    except Exception, e:
                        errors.append('Error creating invitation for line #%d in spreadsheet: %r'
                                                   % ((i+1), e.args))

                    if errors:
                        self.setSessionErrorsTrans('; '.join(errors))

        return self._create_html(formdata=dict( (key, '') for key in keys ),
                                 formerrors={}, previews=previews)

    def _get_inviter_info(self):
        auth_tool = self.getAuthenticationTool()
        inviter_userid = auth_tool.get_current_userid()
        inviter_name = self.get_user_name_or_userid(inviter_userid)
        return (inviter_userid, inviter_name)

    def _create_invitation(self, **invite_args):
        key = random_key()
        invitation = Invitation(key=key, **invite_args)
        self._invites.insert(key, invitation)
        return key

    _invite_email = EmailPageTemplateFile('zpt/invitations_email.zpt', globals())
    def _send_invitation(self, name, email, organization, notes, message,
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

        mail_opts = {
            'name': name,
            'consultation': self.get_consultation(),
            'inviter_name': inviter_name,
            'inviter_message': message,
        }

        if preview:
            mail_opts['keyed_url'] = '[PRIVATE URL]'
            mail_data = self._invite_email.render_email(**mail_opts)
            return {'preview_mail': mail_data}

        invite_args = {
            'inviter_userid': inviter_userid,
            'name': name,
            'email': email,
            'organization': organization,
            'notes': notes,
        }
        key = self._create_invitation(**invite_args)

        mail_opts['keyed_url'] = self.absolute_url() + '/welcome?key=' + key
        mail_data = self._invite_email.render_email(**mail_opts)

        email_tool = self.getEmailTool()
        email_tool.sendEmail(mail_data['body_text'],
                             email, email_tool.get_addr_from(),
                             mail_data['subject'])

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'index_html')
    def index_html(self, REQUEST):
        """ redirect to admin_html """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'admin_html')
    _admin_html = NaayaPageTemplateFile('zpt/invitations_admin', globals(),
                                        'tbconsultation_invitations_admin')
    def admin_html(self, REQUEST):
        """ the admin view """

        auth_tool = self.getAuthenticationTool()

        admin = self.checkPermissionManageTalkBackConsultation()
        if not admin:
            userid = auth_tool.get_current_userid()

        active = []
        revoked = []
        for invite in self._invites.itervalues():
            if not admin and not invite.inviter_userid == userid:
                continue
            if invite.enabled:
                active.append(invite)
            else:
                revoked.append(invite)
        name_from_userid = lambda user_id: auth_tool.name_from_userid(user_id)
        options = {
            'invites_active': active,
            'invites_revoked': revoked,
            'name_from_userid': name_from_userid,
        }
        return self._admin_html(**options)

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION,
                              'admin_invitation_enabled')
    def admin_invitation_enabled(self, key, value=False, REQUEST=None):
        """ disable, or re-enable, an invitation """

        auth_tool = self.getAuthenticationTool()

        admin = self.checkPermissionManageTalkBackConsultation()
        if not admin:
            userid = auth_tool.get_current_userid()

        invite = self._invites[key]
        if not admin and not invite.inviter_userid == userid:
            raise Unauthorized

        invite.enabled = value

        if REQUEST is not None:
            if value:
                msg = 'Invitation for ${name} has been restored.'
            else:
                msg = 'Invitation for ${name} has been revoked.'
            self.setSessionInfoTrans(msg, name=invite.name)
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    _welcome_html = NaayaPageTemplateFile('zpt/invitations_welcome', globals(),
                                          'tbconsultation_invitations_welcome')
    security.declarePublic('welcome')
    def welcome(self, REQUEST):
        """ welcome page for invitees """

        if REQUEST.get('logout', None) == 'on':
            try:
                del REQUEST.SESSION['nytb-current-key']
            except KeyError:
                pass # session key already removed
            cons_url = self.get_consultation().absolute_url()
            return REQUEST.RESPONSE.redirect(cons_url)

        key = REQUEST.get('key', None)
        invitation = self.get_invitation(key)

        if invitation is not None and invitation.enabled:
            auth_tool = self.getAuthenticationTool()
            inviter_name = auth_tool.name_from_userid(invitation.inviter_userid)
            REQUEST.SESSION['nytb-current-key'] = key
        else:
            invitation = None
            inviter_name = ''

        options = {
            'invitation': invitation,
            'inviter_name': inviter_name,
            'logout_url': self.absolute_url() + '/welcome?logout=on',
        }

        return self._welcome_html(REQUEST, **options)

    security.declarePrivate('get_current_invitation')
    def get_current_invitation(self, REQUEST):
        return self.get_invitation(REQUEST.SESSION.get('nytb-current-key', None))

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION,
                              'get_invitation')
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
        self.create_date = date.today()

    @property
    def pretty_date(self):
        return self.create_date.strftime('%Y/%m/%d')

class InvitationUsersTool(BasicUserFolder):
    def authenticate(self, name, password, request):
        invitation = self.invitations.get_current_invitation(request)
        if invitation is not None and invitation.enabled:
            return SimpleUser('invite:' + invitation.key, '',
                              ('InvitedReviewer',), [])
        else:
            return None

InitializeClass(InvitationUsersTool)

def random_key():
    """ generate a 120-bit random key, expressed as 20 base64 characters """
    return urlsafe_b64encode(''.join(chr(randrange(256)) for i in xrange(15)))
