# Python imports

# Zope imports
import Globals
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.ImageFile import ImageFile

# Product imports
from Products.Naaya.NySite import NySite
from Products.NaayaCore.managers.utils import utils
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile as nptf
try:
    from Products.RDFCalendar.RDFCalendar import manage_addRDFCalendar
    rdf_calendar_available = True
except:
    rdf_calendar_available = False


manage_addGroupwareSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addGroupwareSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = 'gw' + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % ('gw', ut.utGenerateUID())
    self._setObject(id, GroupwareSite(id, portal_uid, title, lang))
    ob = self._getOb(id)
    ob.loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return ob


class GroupwareSite(NySite):
    """ """

    meta_type = 'Groupware site'
    #icon = 'misc_/GroupwareSite/site.gif'

    manage_options = (
        NySite.manage_options
    )

    product_paths = NySite.product_paths + [Globals.package_home(globals())]
    security = ClassSecurityInfo()

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        #set default 'Naaya' configuration
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)

        #remove Naaya default content
        self.getLayoutTool().manage_delObjects('skin')
        self.getPortletsTool().manage_delObjects(['menunav_links', 'topnav_links'])
        self.manage_delObjects('info')

        #load groupware skel
        self.loadSkeleton(Globals.package_home(globals()))

        addNyFolder(self, id="library", title="Library", submitted=1)
        if rdf_calendar_available:
            events_rdf = self.getSyndicationTool()['latestevents_rdf']
            manage_addRDFCalendar(self, id="portal_rdfcalendar", title="Events calendar")
            summary_add = self['portal_rdfcalendar'].manage_addProduct['RDFSummary']
            summary_add.manage_addRDFSummary('latest_events', 'events',
                                             events_rdf.absolute_url(),
                                             '', 'yes')

    def get_user_access(self):
        user = self.REQUEST['AUTHENTICATED_USER'].getUserName()
        user_roles = self.getAuthenticationTool().get_all_user_roles(user)

        if 'Manager' in user_roles or 'Administrator' in user_roles:
            return 'admin'
        if 'Contributor' in user_roles and 'Administrator' not in user_roles and 'Manager' not in user_roles:
            return 'member'
        if self.checkPermissionView():
            return 'viewer'
        else:
            return 'restricted'

    def get_gw_root(self):
        return self.aq_parent.absolute_url()

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
        self.toggle_portal_restricted(kwargs.get('portal_is_restricted', None))
        super(GroupwareSite, self).admin_properties(REQUEST=REQUEST, **kwargs)

    def request_ig_access(self, REQUEST):
        """ Called when `request_ig_access_html` submits.
            Sends a mail to the portal administrator informing
            that the current user has requested elevated access.
        """
        role = REQUEST.form.get('role', '')
        location = REQUEST.form.get('location', '')
        sources = self.getAuthenticationTool().getSources()

        if not role or not sources:
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

        source_obj = sources[0] #should not be more than one
        if location == "__root":
            location = ''
        if location:
            location_obj = self.unrestrictedTraverse(location, None)
            location_title = location_obj.title_or_id()
            location_url = location_obj.absolute_url()
        else:
            location_title = self.title_or_id()
            location_url = self.absolute_url()

        user = REQUEST.AUTHENTICATED_USER

        user_admin_link = \
             ("%(ig_url)s/admin_sources_html?"
              "id=%(source_id)s&params=uid&term=%(userid)s&search_user=Search&"
              "req_role=%(role)s&req_location=%(location)s#ldap_user_roles") % \
                  {'role': role,
                   'userid': user.name,
                   'ig_url': self.absolute_url(),
                   'source_id': source_obj.getId(),
                   'location': location}

        mail_tool = self.getEmailTool()
        mail_to = self.administrator_email
        mail_from = mail_tool._get_from_address()
        mail_subject = "IG access request"
        mail_body = \
            ("This is an automated mail to inform you that "
             "user `%(userid)s` has requested %(role)s rights on "
             "%(location_title)s (%(location_url)s).\n\n"
             "You can choose to grant the request by following these steps:\n"
             " - Open the user administration page at %(user_admin_link)s\n"
             " - Verify the form contents for the requesting user\n"
             " - Click on the `Assign role` button\n")  % \
                {'role': role,
                 'userid': user.name,
                 'location_title': location_title,
                 'user_admin_link': user_admin_link,
                 'location_url': location_url}

        mail_tool.sendEmail(mail_body, mail_to, mail_from, mail_subject)

        return REQUEST.RESPONSE.redirect('%s/request_ig_access_html?mail_sent=True' % self.absolute_url())

    def relinquish_membership(self, REQUEST):
        """
        Allows a user to give up membership rights on this portal.
        Deletes all local user accounts, including LDAP mappings.
        """
        if REQUEST['REQUEST_METHOD'] != 'POST':
            return REQUEST.RESPONSE.redirect(self.getSite().aq_parent.absolute_url() + '/index_html')

        user = REQUEST.AUTHENTICATED_USER
        if user.name == 'Anonymous User':
            return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() + '/login_html')

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
            return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() + '/relinquish_membership_html?done=success')
        else:
            return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() + '/relinquish_membership_html?done=failed')


    security.declarePublic('unauthorized_html')
    def unauthorized_html(self, REQUEST):
        """ """
        return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() + '/login_html?' + REQUEST.get('came_from', ''))

    request_ig_access_html = nptf('zpt/request_ig_access', globals(), 'naaya.groupware.request_ig_access')
    relinquish_membership_html = nptf('zpt/relinquish_membership', globals(), 'naaya.groupware.relinquish_membership')

    gw_common_css = ImageFile('www/gw_common.css', globals())
    gw_print_css = ImageFile('www/gw_print.css', globals())
    gw_style_css = ImageFile('www/gw_style.css', globals())

InitializeClass(GroupwareSite)
