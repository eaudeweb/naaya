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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alexandru Plugaru, Eau de Web

from zope import interface
from zope import component

from Products.Naaya.interfaces import INySite
from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

class AnonymousNotificationsPortlet(object):
    interface.implements(INyPortlet)
    component.adapts(INySite)

    title = 'sd-online email notifications'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        tmpl = self.template.__of__(context)
        return tmpl(macro=macro, context=context)
    template = NaayaPageTemplateFile('zpt/notifications_portlet', globals(),
                                'naaya.content-sdo.AnonymousNotification.notifications_portlet')