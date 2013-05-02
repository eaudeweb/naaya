from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from profileoverview.profile import ProfileClient
from constants import GROUPWARE_META_ID

from naaya.core.backport import json
from naaya.core.zope2util import get_zope_env

local_users_zpt = PageTemplateFile('zpt/local_users.zpt', globals())
index_html_zpt = PageTemplateFile('zpt/index.zpt', globals())
eionet_forum_index_html_zpt = PageTemplateFile('zpt/eionet_forum_index.zpt',
                                               globals())

eionet_url = get_zope_env('EIONET_LDAP_EXPLORER', '')
NETWORK_NAME = get_zope_env('NETWORK_NAME', 'Eionet')

index_zpt = PageTemplateFile('zpt/help/index.zpt', globals())
main_features_zpt = PageTemplateFile('zpt/help/main_features.zpt', globals())
content_zpt = PageTemplateFile('zpt/help/content.zpt', globals())
ig_admin_zpt = PageTemplateFile('zpt/help/ig_admin.zpt', globals())
user_roles_zpt = PageTemplateFile('zpt/help/user_roles.zpt', globals())


def get_user_id(request):
    return request.AUTHENTICATED_USER.getId()

def grouped_igs(context):
    """
    Return list of Groupware site-s grouped by user access for logged in user,
    if any

    """
    portals = context.objectValues('Groupware site')
    sorted_igs = {}
    for portal in portals:
        if portal.portal_is_archived:
            sorted_igs.setdefault('archived', []).append(portal)
        else:
            sorted_igs.setdefault(portal.get_user_access(), []).append(portal)

    for portal_list in sorted_igs.values():
        portal_list.sort(key=lambda p: p.title_or_id())

    return sorted_igs


class LocalUsersPage(BrowserPage):
    def __call__(self):
        ctx = self.context.aq_inner # because self subclasses from Explicit
        local_users = {} #All local users per groupware site
        for site in ctx.objectValues('Groupware site'):
            local_users[site] = site.getAuthenticationTool().getUsers()
        return local_users_zpt.__of__(ctx)(local_users=local_users,
                                           grouped_igs=grouped_igs(context))

def nfp_admin_link(context, request):
    """
    Check if LDAP user is NFP and return the URL to 'Edit NRC members' section
    """
    nfp_url = ''

    user = context.REQUEST.AUTHENTICATED_USER
    site_id = context.getSite().getId()

    if site_id == 'nfp-eionet' and user.getUserName() != 'Anonymous User':
        zope_app = context.unrestrictedTraverse('/')
        client = ProfileClient(zope_app, user)
        roles_list = client.roles_list_in_ldap()
        leaf_roles_list = [ r for r in roles_list if not r['children'] ]

        country = ''
        for leaf in leaf_roles_list:
            if 'eionet-nfp-' in leaf['id']:
                country = leaf['id'].rsplit('-', 1)[-1]

        if country:
            nfp_url = ("%s/nfp_nrc/nrcs?nfp=%s" %
                       (context.getSite().absolute_url(), country))

    return nfp_url

def index_html(context, request):
    """
    Render Forum's first page
    """
    options = {'network_name': NETWORK_NAME,
               'grouped_igs': grouped_igs(context),
               'is_authenticated': (get_user_id(request) is not None)}
    return index_html_zpt.__of__(context)(**options)

def gw_meta_info(context, request=None):
    """
    Returns dict containing forum meta information.
    `request` is only used so this can be registered and called as a simpleView

    """
    root = context.unrestrictedTraverse("/")
    meta_info = {'title': root.title,
                 'root_site_title': getattr(root, 'root_site_title', ''),
                 'welcome_text': ''}
    forum_meta = getattr(root, GROUPWARE_META_ID, {})
    meta_info['welcome_text'] = forum_meta.get('welcome_text', '')
    return meta_info

def eionet_forum_index_html(context, request):
    """
    Render Forum's first page
    """
    options = {'is_authenticated': (get_user_id(request) is not None),
               'grouped_igs': grouped_igs(context)}
    return eionet_forum_index_html_zpt.__of__(context)(**options)

def archived_portals_json(context, request):
    """
    Return JSON with archived portals
    """
    archived_portals = grouped_igs(context).get('archived', [])

    portals = []

    for portal in archived_portals:
        portals.append({
            'id': portal.id,
            'title': portal.title_or_id(),
            'subtitle': portal.site_subtitle,
            'url': portal.absolute_url()
        })

    jsonp = request.form.get('jsonp', None)
    if jsonp:
        return "%s(%s)" % (jsonp, json.dumps(portals))
    else:
        return json.dumps(portals)

def help(context, request):
    """
    Render help content
    """
    return index_zpt.__of__(context)()#(**options)

def help_content(context, request):
    """
    Render help content - main content
    """
    return content_zpt.__of__(context)()#(**options)

def help_main_features(context, request):
    """
    Render help content - main features
    """
    return main_features_zpt.__of__(context)()#(**options)

def help_ig_admin(context, request):
    """
    Render help content - IG admin
    """
    return ig_admin_zpt.__of__(context)()#(**options)

def help_user_roles(context, request):
    """
    Render help content - user roles
    """
    return user_roles_zpt.__of__(context)()#(**options)
