import logging
import random
from datetime import datetime, timedelta
import string

from persistent import Persistent
from BTrees.OOBTree import OOBTree as BTree
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from Products.NaayaCore.EmailTool.EmailPageTemplate import \
     EmailPageTemplateFile
from naaya.core.exceptions import i18n_exception
from naaya.core.zope2util import physical_path

log = logging.getLogger('naaya.core.auth.recover_password')

email_template = EmailPageTemplateFile('emailpt/recover_password.zpt',
                                       globals())

TOKEN_SYMBOL = string.ascii_letters + string.digits
BAD_TOKEN_MSG = ("Your password change link is invalid - it probably expired."
                 " Please try again.")

class TokenData(Persistent):
    def __init__(self, user_id):
        self.user_id = user_id
        self.create_time = datetime.now()

class RecoverPassword(SimpleItem):
    """ multi-step process to reset a user's password """

    security = ClassSecurityInfo()

    title = u"Recover password"

    def __init__(self, id):
        super(RecoverPassword, self).__init__()
        self.id = id

    def _get_token_map(self):
        acl_users = self.getSite().acl_users.aq_base
        if not hasattr(acl_users, '_recover_password_tokens'):
            acl_users._recover_password_tokens = BTree()
        return acl_users._recover_password_tokens

    def _new_token(self, user_id):
        """ Generate a token to allow password reset for `user_id`. """
        token = ''.join(random.choice(TOKEN_SYMBOL) for c in range(12))
        self._get_token_map()[token] = TokenData(user_id)
        log.info("new password reset token in site %r for user %r: %r",
                 physical_path(self.getSite()), user_id, token)
        return token

    def _lookup_token(self, token):
        """
        Retrieve a token. If it's valid, return `user_id`; otherwise None.
        """
        token_map = self._get_token_map()
        if token in token_map:
            return token_map[token].user_id
        else:
            return None

    def _remove_token(self, token):
        """ Remove a token after it's used. """
        del self._get_token_map()[token]

    def _cleanup_expired_tokens(self):
        cutoff_time = datetime.now() - timedelta(hours=1)
        token_map = self._get_token_map()
        tokens_to_remove = set()
        for token, data in token_map.iteritems():
            if data.create_time < cutoff_time:
                tokens_to_remove.add(token)

        for token in tokens_to_remove:
            del token_map[token]

    def _set_password(self, user_id, new_password):
        user = self.getSite().acl_users.getUser(user_id)
        assert user is not None
        log.info("changing password in site %r for user %r",
                 physical_path(self.getSite()), user_id)
        user.__ = new_password


    security.declarePublic('index_html')
    index_html = NaayaPageTemplateFile(
            'zpt/recover_password_index', globals(),
            'naaya.core.auth.recover_password_index')

    _request_token_html = NaayaPageTemplateFile(
            'zpt/recover_password_request_token', globals(),
            'naaya.core.auth.recover_password_request_token')
    security.declarePublic('request_token')
    def request_token(self, email, REQUEST=None):
        """
        User submits an email address. If address found, an email is sent with
        a password reset token.
        """
        auth_tool = self.getSite().getAuthenticationTool()
        users = list(auth_tool.lookup_user_by_email(email))
        if not users:
            err = i18n_exception(ValueError,
                                 'E-mail address not found: "${email}"',
                                 email=email)
            if REQUEST is None:
                raise err
            else:
                self.setSessionErrorsTrans(err)
                return REQUEST.RESPONSE.redirect(self.absolute_url())

        for user in users:
            token = self._new_token(user.getId())

            url = '%s/confirm?token=%s' % (self.absolute_url(), token)

            email_data = email_template.render_email(user=user,
                                                     portal=self.getSite(),
                                                     confirmation_url=url)
            email_tool = self.getSite().getEmailTool()
            email_tool.sendEmail(email_data['body_text'], [email],
                                 email_tool.get_addr_from(),
                                 email_data['subject'])

        if REQUEST is not None:
            options = {'email': email}
            return self._request_token_html(REQUEST, **options)

    security.declarePublic('confirm')
    def confirm(self, token, REQUEST): # no point in allowing REQUEST=None
        """
        User clicked on the link in the email. Check if the token is valid, and
        if so, allow user to reset their password.
        """

        user_id = self._lookup_token(token)
        if user_id is None:
            self.setSessionErrorsTrans(BAD_TOKEN_MSG)
            return REQUEST.RESPONSE.redirect(self.absolute_url())

        REQUEST.RESPONSE.redirect(self.absolute_url() +
                                  '/set_new_password_html?token=' + token)

    security.declarePublic('set_new_password_html')
    set_new_password_html = NaayaPageTemplateFile(
            'zpt/recover_password_set_new', globals(),
            'naaya.core.auth.recover_password_set_new')

    security.declarePublic('set_new_password')
    def set_new_password(self, token, new_password, REQUEST=None):
        """
        User entered a new password. Update their password and remove the
        token.
        """

        user_id = self._lookup_token(token)
        if user_id is None:
            if REQUEST is None:
                raise ValueError(BAD_TOKEN_MSG)
            else:
                self.setSessionErrorsTrans(BAD_TOKEN_MSG)
                return REQUEST.RESPONSE.redirect(self.absolute_url())

        if REQUEST is not None:
            new_password_confirm = REQUEST.form['new_password_confirm']
            if new_password != new_password_confirm:
                self.setSessionErrorsTrans("Passwords do not match")
                return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                '/set_new_password_html?token=' + token)

        self._set_password(user_id, new_password)
        self._remove_token(token)

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/done_html')

    done_html = NaayaPageTemplateFile('zpt/recover_password_done', globals(),
                                      'naaya.core.auth.recover_password_done')

InitializeClass(RecoverPassword)

#@component.adapter(INySite, IHeartbeat)
def cleanup_expired_tokens(site, hb):
    site.acl_users.recover_password._cleanup_expired_tokens()
