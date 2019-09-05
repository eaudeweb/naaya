import os
from copy import copy
import logging
from datetime import datetime
from urlparse import urlparse

import Globals
from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PythonScripts.PythonScript import manage_addPythonScript
from zExceptions import BadRequest
from zope.interface import implements
from zope.event import notify

from Products.NaayaCore.AuthenticationTool.events import RoleAssignmentEvent
from Products.Naaya.NySite import NySite
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile \
    as nptf
from Products.NaayaCore.EmailTool.EmailPageTemplate import \
    EmailPageTemplateFile
from naaya.component import bundles
from naaya.core.utils import cleanup_message
from naaya.core.zope2util import get_zope_env, path_in_site
try:
    from Products.RDFCalendar.RDFCalendar import manage_addRDFCalendar
    rdf_calendar_available = True
except ImportError:
    rdf_calendar_available = False
from eea.usersdb.factories import agent_from_site

from naaya.groupware.member_search import MemberSearch
from naaya.groupware.interfaces import IGWSite
from naaya.groupware.constants import METATYPE_GROUPWARESITE
from naaya.groupware.profileoverview.profile import ProfileClient

log = logging.getLogger(__name__)

manage_addGroupwareSite_html = PageTemplateFile('zpt/site_manage_add',
                                                globals())


def manage_addGroupwareSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id:
        id = 'gw' + ut.utGenRandomId(6)
    self._setObject(id, GroupwareSite(id, title=title, lang=lang))
    ob = self._getOb(id)
    ob.loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return ob


groupware_bundle = bundles.get("Groupware")
groupware_bundle.set_parent(bundles.get("Naaya"))
NETWORK_NAME = get_zope_env('NETWORK_NAME', 'Eionet')

ACTION_LOG_TYPES = {
    'role_request': 'IG role request',
    'role_request_review': 'IG role request review'
}


class GroupwareSite(NySite):
    """ """
    implements(IGWSite)
    meta_type = METATYPE_GROUPWARESITE
    # icon = 'misc_/GroupwareSite/site.gif'

    manage_options = (
        NySite.manage_options
    )

    product_paths = NySite.product_paths + [Globals.package_home(globals())]
    security = ClassSecurityInfo()
    display_subobject_count = "on"
    portal_is_archived = False
    content_versioning_enabled = False

    def __init__(self, *args, **kwargs):
        """ """
        NySite.__dict__['__init__'](self, *args, **kwargs)
        self.display_subobject_count = "on"
        self.set_bundle(groupware_bundle)
        self.portal_is_archived = False  # The semantics of this flag is
        # that you can't request membership of the IG any longer.

    security.declarePrivate('loadDefaultData')

    def loadDefaultData(self):
        """ """
        # set default 'Naaya' configuration
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)

        # remove Naaya default content
        layout_tool = self.getLayoutTool()
        naaya_skins = [skin.getId() for skin in
                       layout_tool.objectValues('Naaya Skin')]
        logos = [image.getId() for image in
                 layout_tool.objectValues('Image')]
        layout_tool.manage_delObjects(naaya_skins + logos)
        self.getPortletsTool().manage_delObjects(['menunav_links',
                                                  'topnav_links'])
        self.manage_delObjects('info')

        # load groupware skel
        self.loadSkeleton(Globals.package_home(globals()))

        if rdf_calendar_available:
            manage_addRDFCalendar(self, id="portal_rdfcalendar",
                                  title="Events calendar")
            rdfcalendar_ob = self._getOb('portal_rdfcalendar')

            # adding range index to catalog
            class Empty(object):
                pass
            extra = Empty()  # Extra has to be an object.. see DateRangeIndex
            extra.since_field = 'start_date'
            extra.until_field = 'end_date'
            self.getCatalogTool().addIndex('resource_interval',
                                           'DateRangeIndex', extra=extra)

            # adding local_events Script (Python)
            manage_addPythonScript(rdfcalendar_ob, 'local_events')
            local_events_ob = rdfcalendar_ob._getOb('local_events')
            local_events_ob._params = 'year=None, month=None, day=None'
            local_events_ob.write(open(os.path.dirname(__file__) +
                                  '/skel/others/local_events.py', 'r').read())

        self.getPortletsTool().assign_portlet('library', 'right',
                                              'portlet_latestuploads_rdf',
                                              True)

        # set default main topics
        self.getPropertiesTool().manageMainTopics(['about', 'library'])

        # add meta on brains for group local roles
        self.getCatalogTool().addColumn('ny_ldap_group_roles')

    def get_user_access(self, user=None):
        """
        Returns one of 'admin', 'member', 'viewer' or 'restricted' for logged
        in user, if not explicitly specified.

        """
        if user is None:
            user = self.REQUEST.get('AUTHENTICATED_USER', None)
        if user is not None:
            if user.has_permission(PERMISSION_PUBLISH_OBJECTS, self):
                return 'admin'
            elif user.allowed(self, ['Contributor']):
                return 'member'
            elif user.has_permission(view, self):
                return 'viewer'
        return 'restricted'

    def get_gw_root(self):
        return self.aq_parent.absolute_url()

    def get_gw_site_root(self):
        return self.aq_parent

    @property
    def portal_is_restricted(self):
        view_perm = getattr(self, '_View_Permission', [])
        return isinstance(view_perm, tuple) and ('Anonymous' not in view_perm)

    security.declarePrivate('toggle_portal_restricted')

    def toggle_portal_restricted(self, status):
        permission = getattr(self, '_View_Permission', [])

        if status:
            new_permission = [x for x in permission if x != 'Anonymous']
            if 'Contributor' not in new_permission:
                new_permission.append('Contributor')
            self._View_Permission = tuple(new_permission)
        else:
            new_permission = list(permission)
            new_permission.append('Anonymous')
            self._View_Permission = new_permission

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_properties')

    def admin_properties(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST is not None:
            kwargs.update(REQUEST.form)
        self.portal_is_archived = kwargs.get('portal_is_archived', False)
        self.toggle_portal_restricted(kwargs.get('portal_is_restricted', None))
        super(GroupwareSite, self).admin_properties(REQUEST=REQUEST, **kwargs)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_email')

    def admin_email(self, mail_server_name='', mail_server_port='',
                    administrator_email='', mail_address_from='',
                    notify_on_errors_email='', REQUEST=None):
        """ """
        self.getEmailTool().manageSettings(mail_server_name, mail_server_port,
                                           administrator_email,
                                           mail_address_from,
                                           notify_on_errors_email)
        if REQUEST:
            self.setSessionInfoTrans(MESSAGE_SAVEDCHANGES,
                                     date=self.utGetTodayDate())
            REQUEST.RESPONSE.redirect('%s/admin_email_html' %
                                      self.absolute_url())

    def _validate_form_date(self, value, all_day):
        if all_day is True:
            try:
                date = datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                return False
        else:
            try:
                date = datetime.strptime(value, "%d/%m/%Y %H:%M")
            except ValueError:
                return False

        return date

    security.declarePrivate('_user_admin_link')

    def _user_admin_link(self, log_entry):
        """ Used by review request access (email and view) """
        return ("%(ig_url)s/admin_sources_html?id=%(source_id)s&s="
                "assign_to_users&params=uid&term=%(userid)s&search_user="
                "Search&req_role=%(role)s&req_location=%(location)s"
                "#ldap_user_roles") % \
            {'role': log_entry.role,
             'userid': log_entry.user,
             'ig_url': self.absolute_url(),
             'source_id': self.getAuthenticationTool().getSources()[0].getId(),
             'location': log_entry.location}

    security.declarePrivate('_review_access_request_first_page')

    def _review_access_request_first_page(self, log_entry):
        """
        Called by review_ig_request to access first (actual) page of
        review request, containing user and request information

        """
        # get roles
        app = self.aq_parent
        user = app.acl_users.getUser(log_entry.user)
        client = ProfileClient(app, user)
        roles_list = client.roles_list_in_ldap()
        leaf_roles_list = [r for r in roles_list if not r['children']]
        # get all user info from LDAP
        agent = agent_from_site(self)
        user_info = agent.user_info(log_entry.user)

        return self.review_ig_request_html(
            log_entry=log_entry, user=user_info, ldap_roles=leaf_roles_list,
            user_admin_link=self._user_admin_link(log_entry))

    def review_ig_request(self, REQUEST=None, **kw):
        """ Administrator reviews user access request and decides to grant or
        reject the user access with some message. Here we check if the user
        has the right key that allows to review the user's request.

        XXX: Works only with a single source (no local users)

        """
        # Store found keys in session, optimising the search
        action_logger = self.getActionLogger()
        source_obj = self.getAuthenticationTool().getSources()[0]
        session_data = self.getSession('log_entry', {})

        if REQUEST is not None:
            kw.update(REQUEST.form)

        key = kw.get('key', '')
        log_entry = None
        if key in session_data:
            log_entry_id = session_data[key]
            log_entry = action_logger[log_entry_id]
        else:
            count = 0
            action_logs = [(i, l) for i, l in action_logger.items()
                           if l.type in ACTION_LOG_TYPES.values()]
            for log_id, log in action_logs:
                if getattr(log, 'key', None) == key:
                    count += 1
                    log_entry = log
                    log_entry_id = log_id
                if count == 2:  # Raise info message because this key is old
                    return self.review_ig_request_html(log_entry=log_entry,
                                                       multiple_access=True)
            if log_entry is None:
                self.setSessionErrorsTrans("Key ${key} not found", key=key)
                return REQUEST.RESPONSE.redirect(self.getSite().absolute_url())

            session_data.update({key: log_entry_id})
            self.setSession('log_entry', session_data)

        if REQUEST.REQUEST_METHOD == 'GET':
            return self._review_access_request_first_page(log_entry)
        else:
            result = {}
            send_mail = bool(kw.get('send_mail', False))
            # Create a new action log with the result of the review request
            # based on the current action log
            new_log_entry = copy(log_entry)
            new_log_entry.type = ACTION_LOG_TYPES['role_request_review']
            new_log_entry.created_datetime = DateTime()

            if 'grant' in kw:
                result['granted'] = True
                source_obj.addUserRoles(name=log_entry.user,
                                        location=log_entry.location,
                                        roles=log_entry.role,
                                        send_mail=send_mail,
                                        REQUEST=REQUEST)

                new_log_entry.action = 'Granted'
                action_logger.append(new_log_entry)

                # Add to site logger this grant of access
                context = self.unrestrictedTraverse(log_entry.location, None)
                notify(
                    RoleAssignmentEvent(
                        context, REQUEST.AUTHENTICATED_USER.getUserName(),
                        log_entry.user, [log_entry.role], []))

            elif 'reject' in kw:
                result['granted'] = False
                reason = kw.get('reason', '')
                if send_mail is True:
                    user_info = source_obj.get_user_info(log_entry.user)
                    mail_tool = self.getEmailTool()
                    mail_to = user_info.email
                    mail_from = mail_tool._get_from_address()
                    mail_data = self.request_rejected_emailpt.render_email(**{
                        'here': self,
                        'role': log_entry.role,
                        'reason': reason,
                        'firstname': getattr(user_info, 'first_name', ''),
                        'lastname': getattr(user_info, 'last_name', ''),
                        'location_title': log_entry.location_title,
                        'location_url': log_entry.location_url,
                        'network_name': NETWORK_NAME,
                    })
                    mail_tool.sendEmail(mail_data['body_text'], mail_to,
                                        mail_from, mail_data['subject'])

                new_log_entry.action = 'Rejected'
                new_log_entry.reason = reason
                action_logger.append(new_log_entry)

            # after reviewing the request access, session is cleared to prevent
            # one administrator (or delegate) to access the link several times
            del session_data[key]

            return REQUEST.RESPONSE.redirect(self.getSite().absolute_url())

    def request_ig_access(self, REQUEST):
        """ Called when `request_ig_access_html` submits.
            Sends a mail to the portal administrator informing
            that the current user has requested elevated access.
        """

        if self.portal_is_archived:
            raise BadRequest("You can't request access to archived IGs")

        role = REQUEST.form.get('role', '')
        location = REQUEST.form.get('location', '')
        location_url = REQUEST.form.get('location_url', '')
        explanatory_text = cleanup_message(
            REQUEST.form.get('explanatory_text', '').strip())
        if not explanatory_text:
            explanatory_text = '-'

        if not role:
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

        if location == "/":
            location = ''
        if not location and location_url:
            o = urlparse(location_url.replace('/index_html', ''))
            location = o.path
        if location:
            location_obj = self.unrestrictedTraverse(location, None)
            while True:
                if location_obj.meta_type in ['Naaya Meeting',
                                              'Groupware site']:
                    break
                else:
                    location_obj = location_obj.aq_parent
            site_id = self.getSite().getId()
            location = '/' + site_id + '/' + path_in_site(location_obj)
            location_title = location_obj.title_or_id()
            location_url = location_obj.absolute_url()
        else:
            location_title = self.title_or_id()
            location_url = self.absolute_url()

        user = REQUEST.AUTHENTICATED_USER

        member_search_link = (
            "%(ig_url)s/member_search?search_string=%(userid)s" % {
                'ig_url': self.absolute_url(),
                'userid': user.name
            }
        )

        # Create an action  for the current request and include a link in the
        # e-mail so that the log can be viewed or passed to another
        # administrator
        key = self.utGenerateUID()
        log_entry_id = self.getActionLogger().create(
            type=ACTION_LOG_TYPES['role_request'], key=key,
            user=user.getUserName(), role=role, location=location,
            location_url=location_url, location_title=location_title
        )
        log_entry = self.getActionLogger()[log_entry_id]

        user_admin_link = self._user_admin_link(log_entry)

        review_link = (
            "%(ig_url)s/review_ig_request?key=%(key)s" % {
                'ig_url': self.absolute_url(),
                'key': key
            }
        )

        mail_tool = self.getEmailTool()
        mail_to = self.administrator_email
        mail_from = mail_tool.get_addr_from()
        try:
            firstname = getattr(user, 'firstname', '').decode('utf-8')
        except UnicodeDecodeError:
            firstname = getattr(user, 'firstname', '').decode('latin1')
        try:
            lastname = getattr(user, 'lastname', '').decode('utf-8')
        except UnicodeDecodeError:
            lastname = getattr(user, 'lastname', '').decode('latin1')
        mail_data = self.request_ig_access_emailpt.render_email(**{
            'here': self,
            'role': role,
            'user': user,
            'firstname': firstname,
            'lastname': lastname,
            'email': getattr(user, 'mail', ''),
            'location_title': location_title,
            'user_admin_link': user_admin_link,
            'member_search_link': member_search_link,
            'location_url': location_url,
            'review_link': review_link,
            'explanatory_text': explanatory_text,
            'network_name': NETWORK_NAME,
        })
        mail_tool.sendEmail(mail_data['body_text'], mail_to,
                            mail_from, mail_data['subject'])

        return REQUEST.RESPONSE.redirect(
            '%s/request_ig_access_html?mail_sent=True' % self.absolute_url())

    def relinquish_membership(self, REQUEST):
        """
        Allows a user to give up membership rights on this portal.
        Deletes all local user accounts, including LDAP mappings.
        """
        if REQUEST['REQUEST_METHOD'] != 'POST':
            return REQUEST.RESPONSE.redirect(
                self.getSite().aq_parent.absolute_url() + '/index_html')

        user = REQUEST.AUTHENTICATED_USER
        if user.name == 'Anonymous User':
            return REQUEST.RESPONSE.redirect(
                self.getSite().absolute_url() + '/login_html')

        acl = self.getAuthenticationTool()
        relinquished = False
        for source in acl.getSources():
            relinquished = source.removeUser(user.name)

        try:
            acl.manage_delUsers([user.name])
            if user.name not in acl.getUserNames():
                relinquished = True
        except KeyError:
            pass

        if relinquished:
            return REQUEST.RESPONSE.redirect(
                self.getSite().absolute_url() +
                '/relinquish_membership_html?done=success')
        else:
            return REQUEST.RESPONSE.redirect(
                self.getSite().absolute_url() +
                '/relinquish_membership_html?done=failed')

    security.declarePublic('requestrole_html')

    def requestrole_html(self, REQUEST):
        """ redirect to request_ig_access_html """
        url = '%s/request_ig_access_html' % self.absolute_url()
        REQUEST.RESPONSE.redirect(url)

    security.declarePublic('login_html')

    def login_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() +
                                         '/login/login_form?%s' %
                                         REQUEST.environ.get('QUERY_STRING'))

    security.declarePublic('logout_html')

    def logout_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() +
                                         '/login/logout')

    security.declarePublic('inside_meeting')

    def check_inside_meeting(self, came_from=None):
        """ """
        if came_from:
            o = urlparse(
                came_from.replace('/index_html', '').replace('/edit_html', ''))
            if o.path:
                location_obj = self.unrestrictedTraverse(o.path, None)
                return _inside_meeting(location_obj)

    request_ig_access_emailpt = EmailPageTemplateFile(
        'zpt/emailpt/request_ig_access.zpt', globals())
    request_rejected_emailpt = EmailPageTemplateFile(
        'zpt/emailpt/request_rejected.zpt', globals())

    review_ig_request_html = nptf('zpt/review_ig_request', globals(),
                                  'naaya.groupware.review_ig_request')
    request_ig_access_html = nptf('zpt/request_ig_access', globals(),
                                  'naaya.groupware.request_ig_access')
    relinquish_membership_html = nptf('zpt/relinquish_membership', globals(),
                                      'naaya.groupware.relinquish_membership')

    member_search = MemberSearch(id='member_search')


InitializeClass(GroupwareSite)


def groupware_bundle_registration():
    """ Register things from skel into the GROUPWARE bundle """
    from Products.NaayaCore.FormsTool import bundlesupport
    templates_path = os.path.join(os.path.dirname(__file__), 'skel', 'forms')
    bundlesupport.register_templates_in_directory(templates_path, 'Groupware')


def _inside_meeting(location_obj):
    if location_obj.meta_type == 'Naaya Meeting':
        return True
    elif location_obj.meta_type == 'Groupware site':
        return False
    else:
        return _inside_meeting(location_obj.aq_parent)
