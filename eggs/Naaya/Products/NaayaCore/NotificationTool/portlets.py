from naaya.core.zope2util import path_in_site
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class NotificationsPortlet(object):
    title = 'Subscribe to notifications'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        notif_tool = self.site.getNotificationTool()
        if not list(notif_tool.available_notif_types()):
            return ''

        macro = self.site.getPortletsTool()._get_macro(position)
        tmpl = self.template.__of__(context)
        return tmpl(macro=macro, notif_tool=notif_tool,
                    location=path_in_site(context))

    template = PageTemplateFile('zpt/portlet', globals())
