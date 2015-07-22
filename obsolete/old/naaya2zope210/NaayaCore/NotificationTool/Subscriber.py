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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Andrei Laza, Eau de Web

#Python imports

#Zope imports
from Acquisition import Implicit
from OFS.SimpleItem import Item
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import Unauthorized


#Product imports
from Products.NaayaCore.NotificationTool import NotificationTool

class Subscriber(Implicit, Item):
    def __init__(self, id):
        self.id = id
        self.title= 'Subscribe to notifications'

    def get_notification_tool(self):
        return self.getSite().getNotificationTool()

    def get_location(self):
        current_location = self.absolute_url(1)
        # remove site id and 'subscribe'
        current_location = current_location.split('/')[1:-1]
        return ('/').join(current_location)

    def get_location_link(self, REQUEST):
        return self.get_notification_tool().get_location_link(REQUEST)

    def get_user_id(self, REQUEST):
        user_id = REQUEST.AUTHENTICATED_USER.getId()
        if user_id is None:
            raise Unauthorized
        return user_id

    def get_implicit_lang(self):
        languages = self.gl_get_languages_map()
        for l in languages:
            if l['selected']:
                return l['id']
        return None

    def list_subscriptions(self, REQUEST):
        user_id = self.get_user_id(REQUEST)
        location = self.get_location()

        notificationTool = self.get_notification_tool()
        return notificationTool.list_subscriptions(user_id,
            location=location, inherit_location=True)

    def list_user_subscriptions(self, REQUEST):
        user_id = self.get_user_id(REQUEST)
        notificationTool = self.get_notification_tool()
        return notificationTool.list_subscriptions(user_id)

    def list_enabled_subscriptions(self):
        notificationTool = self.get_notification_tool()
        location = self.get_location()
        return notificationTool.available_notif_types('')

    def get_enabled_subscriptions(self, REQUEST):
        enabled = set(self.list_enabled_subscriptions())
        current = set((x.notif_type for x in self.list_subscriptions(REQUEST)))
        return enabled.difference(current)

    def subscribe(self, REQUEST, notif_type, lang=None):
        """ """
        user_id = self.get_user_id(REQUEST)
        location = self.get_location()

        # get the lang (if it's not explicit)
        if (lang is None) or (lang == ''):
            lang = self.get_implicit_lang()

        notificationTool = self.get_notification_tool()

        notificationTool.add_subscription(user_id, location, notif_type, lang)

        return REQUEST.RESPONSE.redirect(self.absolute_url())

    def delete_subscription(self, REQUEST, location, notif_type, lang):
        """ """
        user_id = self.get_user_id(REQUEST)
        notificationTool = self.get_notification_tool()
        notificationTool.remove_subscription(user_id, location, notif_type, lang)

        return REQUEST.RESPONSE.redirect(self.absolute_url())

    index_html = PageTemplateFile('zpt/subscribe', globals())

InitializeClass(Subscriber)

