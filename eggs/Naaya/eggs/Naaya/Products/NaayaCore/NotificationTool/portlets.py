from naaya.core.zope2util import path_in_site
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

class NotificationsPortlet(object):
    title = 'Subscribe to notifications'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        notif_tool = self.site.getNotificationTool()
        #The portlet should only be rendered if at least one notification type
        #is activated, of if the user has administrative rights, so he should
        #be able to subscribe to administrative notifications
        if not list(notif_tool.available_notif_types()) and not \
                    self.site.checkPermissionPublishObjects():
            return ''

        macro = self.site.getPortletsTool()._get_macro(position)
        tmpl = self.template.__of__(context)
        location = path_in_site(context)
        if context == notif_tool:
            location = ''
        return tmpl(macro=macro, notif_tool=notif_tool,
                    location=location)

    template = NaayaPageTemplateFile('zpt/portlet', globals(), 'naaya.core.notifications.notifications_portlet')
