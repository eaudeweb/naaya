from zope import interface
from zope import component

from Products.Naaya.interfaces import INySite
from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

class InfoFolderPortlet(object):
    interface.implements(INyPortlet)
    component.adapts(INySite)

    title = 'sd-online latest uploads'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(macro=macro)

    template = NaayaPageTemplateFile('zpt/latest_uploads_portlet', globals(),
                                     'naaya.content-sdo.infofolder.latest_uploads_portlet')

class InfoFolderSearchPortlet(object):
    interface.implements(INyPortlet)
    component.adapts(INySite)

    title = 'sd-online folder search'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(macro=macro)

    template = NaayaPageTemplateFile('zpt/infofolder_search_portlet', globals(),
                                     'naaya.content-sdo.infofolder.infofolder_search_portlet')

class InfoFolderEventsPortlet(object):
    interface.implements(INyPortlet)
    component.adapts(INySite)

    title = 'sd-online events filter'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(macro=macro)

    template = NaayaPageTemplateFile('zpt/events_filter', globals(),
                                     'naaya.content-sdo.infofolder.events_filter')

