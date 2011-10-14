from zope.interface import implements
from zope.component import adapts

from Products.Naaya.interfaces import INySite
from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

from interfaces import IGWSite

class NavigationPortlet(object):
    implements(INyPortlet)
    adapts(INySite)

    title = 'Navigation'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(macro=macro)

    template = NaayaPageTemplateFile('zpt/navigation_portlet', globals(),
                                     'naaya.groupware.navigation_portlet')


class AdministrationPortlet(object):
    implements(INyPortlet)
    adapts(IGWSite)

    title = 'Administration'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(macro=macro)

    template = NaayaPageTemplateFile('skel/portlets/portlet_administration', globals(),
                                     'naaya.groupware.portlets.portlet_administration')
