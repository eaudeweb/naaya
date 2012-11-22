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

class LocalUsersPage(BrowserPage):
    def __call__(self):
        ctx = self.context.aq_inner # because self subclasses from Explicit
        local_users = {} #All local users per groupware site
        for site in ctx.objectValues('Groupware site'):
            local_users[site] = site.getAuthenticationTool().getUsers()
        return local_users_zpt.__of__(ctx)(local_users=local_users)

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
            nfp_url = eionet_url + '/nfp_nrc/nrcs?nfp=' + country

    return nfp_url

def index_html(context, request):
    """
    Render Forum's first page
    """
    return index_html_zpt.__of__(context)(network_name=NETWORK_NAME)

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
    return eionet_forum_index_html_zpt.__of__(context)()

def archived_portals_json(context, request):
    """
    Return JSON with archived portals
    """
    archived_portals = context.groupedIGs().get('archived', [])

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
