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
import json

from BTrees.OOBTree import OOBTree
from Persistence import Persistent
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.User import BasicUserFolder, SimpleUser
from OFS.SimpleItem import SimpleItem

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile
from Products.NaayaCore.EmailTool.EmailTool import (save_bulk_email,
                                                    get_bulk_emails,
                                                    get_bulk_email,
                                                    _mail_in_queue,
                                                    check_cached_valid_emails,
                                                    export_email_list_xcel)
from naaya.core.zope2util import path_in_site
from permissions import PERMISSION_INVITE_TO_TALKBACKCONSULTATION
import xlwt
import xlrd

from datetime import datetime
from Products.NaayaCore.managers import utils
g_utils = utils.utils()
from StringIO import StringIO


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
        save_bulk_email(self.getSite(), [email], email_tool.get_addr_from(),
                        mail_data['subject'], mail_data['body_text'],
                        where_to_save=path_in_site(self.get_consultation()))

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'index_html')
    def index_html(self, REQUEST):
        """ redirect to admin_html """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'check_emails')
    def check_emails(self, REQUEST=None, RESPONSE=None):
        """Return already resolved email addresses
        and a list with those to be resolved by a different call"""
        emails = REQUEST.get("emails[]")
        if not emails:
            return None
        invalid, not_resolved = check_cached_valid_emails(self, emails)
        return json.dumps({'invalid': invalid, 'notResolved': not_resolved})

    def _get_invitations(self):
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
        return {
            'invites_active': active,
            'invites_revoked': revoked,
            'name_from_userid': name_from_userid,
        }

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'admin_html')
    _admin_html = NaayaPageTemplateFile('zpt/invitations_admin', globals(),
                                        'tbconsultation_invitations_admin')
    def admin_html(self, REQUEST):
        """ the admin view """
        options = self._get_invitations()
        return self._admin_html(**options)

    def _xcel_prepare_data(self, invitation, keys):
        """Extracts a ready for xcel export row out of invitation
        Only the keys enumerates in keys are look for.

        Specifically looks for fields 'private_url' and 'name_from_userid'
        and resolve them to values not directly available in invitation obj """
        _separator = ', '
        _max_cell = 32767
        row_data = []
        for k in keys:
            if k == 'private_url':
                v = self.absolute_url() + '/welcome?key=' + invitation.key
            elif k == 'name_from_userid':
                v = self.getAuthenticationTool().name_from_userid(
                    invitation.inviter_userid)
            else:
                v = getattr(invitation, k, None)
            if not v:
                row_data.append('')
            elif isinstance(v, tuple) or isinstance(v, list):
                # FIXME: elements inside iteratable must be strings...
                row_data.append(_separator.join(v))
            elif isinstance(v, datetime):
                row_data.append(g_utils.utShowFullDateTime(v))
            else:
                row_data.append(unicode(v))
            # xcel limit for cell content
            if len(row_data[-1]) > _max_cell:
                row_data[-1] = row_data[-1][:_max_cell]
        return row_data

    def _xcel_populate_sheet(self, wb, sheet_name, header, keys, invitations):
        style = xlwt.XFStyle()
        normalfont = xlwt.Font()
        headerfont = xlwt.Font()
        headerfont.bold = True
        style.font = headerfont

        ws = wb.add_sheet(sheet_name)
        for col_idx, col_name in enumerate(header):
            ws.row(0).set_cell_text(col_idx, col_name, style)
        style.font = normalfont
        for row_idx, invitation in enumerate(invitations, 1):
            row = self._xcel_prepare_data(invitation, keys)
            for col_idx, col_value in enumerate(row):
                ws.row(row_idx).set_cell_text(col_idx, col_value, style)

    def _xcel_export_invitations(self, header, keys, options):
        wb = xlwt.Workbook(encoding='utf-8')
        self._xcel_populate_sheet(wb, 'Active Invitations', header, keys,
                                  options['invites_active'])
        self._xcel_populate_sheet(wb, 'Revoked Invitations', header, keys,
                                  options['invites_revoked'])
        output = StringIO()
        wb.save(output)
        return output.getvalue()

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'invitations_export')
    def invitations_export(self, REQUEST, RESPONSE):
        """Aggregate an xcel file from invitations on this object
        (just like admin_html does to populate the web page)"""
        if not REQUEST:
            RESPONSE.badRequestError("MALFORMED_URL")
        headers = REQUEST.get('headers')
        keys = REQUEST.get('keys')
        if not headers or not keys:
            RESPONSE.badRequestError("MALFORMED_URL")
        headers = headers.split(',')
        keys = keys.split(',')
        if len(headers) != len(keys):
            RESPONSE.badRequestError("MALFORMED_URL")

        RESPONSE.setHeader('Content-Type', 'application/vnd.ms-excel')
        RESPONSE.setHeader('Content-Disposition',
                            'attachment; filename=consultation_invitations.xls')
        options = self._get_invitations()
        return self._xcel_export_invitations(headers, keys, options)

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

    NaayaPageTemplateFile('zpt/email_archive', globals(),
        'tbconsultation-email_archive')
    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'saved_mails')
    def saved_emails(self, REQUEST=None, RESPONSE=None):
        """ Display all saved invitation emails """
        emails = get_bulk_emails(self.getSite(),
                                where_to_read=path_in_site(self.get_consultation()))
        return self.getFormsTool().getContent({'here': self,
                                               'emails': emails,
                                               'consultation': self.get_consultation()},
                                               'tbconsultation-email_archive')

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'saved_emails_export')
    def saved_emails_export(self, REQUEST=None, RESPONSE=None):
        """ Aggregate an xcel file from emails on disk
        (just like saved_emails does to populate the web page)"""
        if not REQUEST:
            RESPONSE.badRequestError("MALFORMED_URL")
        headers = REQUEST.form.get('headers')
        keys = REQUEST.form.get('keys')
        ids = REQUEST.form.get('id')
        if not headers or not keys:
            RESPONSE.badRequestError("MALFORMED_URL")
        headers = headers.split(',')
        keys = keys.split(',')
        if len(headers) != len(keys):
            RESPONSE.badRequestError("MALFORMED_URL")

        RESPONSE.setHeader('Content-Type', 'application/vnd.ms-excel')
        RESPONSE.setHeader('Content-Disposition',
                            'attachment; filename=consultation_invitation_emails.xls')
        cols = zip(headers, keys)
        return export_email_list_xcel(self.getSite(), cols, ids,
                    where_to_read=path_in_site(self.get_consultation()))

    NaayaPageTemplateFile('zpt/email_view', globals(),
        'tb_consultation-view_email')
    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'view_email')
    def view_email(self, filename, REQUEST=None, RESPONSE=None):
        """ Display a specfic saved email """
        email = get_bulk_email(self.getSite(), filename,
                                where_to_read=path_in_site(self.get_consultation()))
        return self.getFormsTool().getContent({'here': self,
                                                'email': email,
                                                'consultation': self.get_consultation()},
            'tb_consultation-view_email')

    security.declareProtected(PERMISSION_INVITE_TO_TALKBACKCONSULTATION, 'mail_in_queue')
    def mail_in_queue(self, filename):
        """ Check if a specific message is still in queue """
        COMMON_KEYS = ['sender', 'recipients', 'subject', 'content', 'date']
        check_values = {}
        archived_email = get_bulk_email(self.getSite(), filename,
                                where_to_read=path_in_site(self.get_consultation()))
        for key in COMMON_KEYS:
            check_values[key] = archived_email[key]
        return _mail_in_queue(self.getSite(), filename, check_values)

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
