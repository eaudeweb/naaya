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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web


#Naaya imports
from Products.naayaUpdater.updates import UpdateScript

class UpdateCSS(UpdateScript):
    """
    Generic script to clean up obsolete data in Naaya sites. This script must
    ALWAYS be safe to run on ANY site.
    """
    title = 'Cleanup'
    authors = ['Alex Morega']
    creation_date = 'Nov 12, 2009'

    def _update(self, portal):
        self.log.debug('/'.join(portal.getPhysicalPath()))

        self.remove_old_notification_emailpt(portal)
        self.remove_old_notifications_portlet(portal)

        return True

    def remove_old_notification_emailpt(self, portal):
        """
        Remove EmailPageTemplate objects from NotificationTool instances - they
        have been deprecated in favor of EmailPageTemplateFile objects on the
        NotificationTool class.

        -- Alex Morega, 2009/11/12
        """
        notification_tool = portal.getNotificationTool()
        if not hasattr(notification_tool, 'instant_emailpt'):
            # the NotificationTool code is older than 2009/11
            return

        ids = notification_tool.objectIds()

        for name in ['daily_template', 'instant_template',
                     'monthly_template', 'weekly_template']:
            if name in ids:
                notification_tool.manage_delObjects([name])
                self.log.info('NotificationTool: removing template %r', name)

    def remove_old_notifications_portlet(self, portal):
        """
        Remove the `portlet_notifications` object from `portal_portlets`
        -- Alex Morega, 2009/11/18
        """
        name = 'portlet_notifications'
        portlets_tool = portal.getPortletsTool()
        if name in portlets_tool.objectIds():
            portlets_tool.manage_delObjects(name)
            self.log.info('PortletsTool: removing portlet %r', name)
