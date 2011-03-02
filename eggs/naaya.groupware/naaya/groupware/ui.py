from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

local_users_zpt = PageTemplateFile('zpt/local_users.zpt', globals())

class LocalUsersPage(BrowserPage):
    def __call__(self):
        ctx = self.context.aq_inner # because self subclasses from Explicit
        local_users = {} #All local users per groupware site
        for site in ctx.objectValues('Groupware site'):
            local_users[site] = site.getAuthenticationTool().getUsers()
        return local_users_zpt.__of__(ctx)(local_users=local_users)
