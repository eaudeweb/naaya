from zope import interface, component

from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

from interfaces import INySite

class AdministrationPortlet(object):
    interface.implements(INyPortlet)
    component.adapts(INySite)

    title = 'Administration'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(macro=macro)

    template = NaayaPageTemplateFile('skel/portlets/portlet_administration', globals(),
                                     'Products.Naaya.portlets.portlet_administration')
