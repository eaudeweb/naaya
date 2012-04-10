from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from profileoverview.profile import ProfileClient

from App.config import getConfiguration

local_users_zpt = PageTemplateFile('zpt/local_users.zpt', globals())
index_html_zpt = PageTemplateFile('zpt/index.zpt', globals())

CONFIG = getConfiguration()
eionet_url = getattr(CONFIG, 'environment', {}).get('EIONET_LDAP_EXPLORER', '')

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
    return index_html_zpt.__of__(context)()
