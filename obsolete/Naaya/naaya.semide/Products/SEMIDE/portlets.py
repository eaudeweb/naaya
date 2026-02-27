from zope.interface import implements
from zope.component import adapts

from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

from interfaces import ISEMIDESite

class AdministrationPortlet(object):
    implements(INyPortlet)
    adapts(ISEMIDESite)

    title = 'Administration'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(macro=macro)

    template = NaayaPageTemplateFile('skel/portlets/portlet_administration', globals(),
                                     'Products.SEMIDE.portlets.portlet_administration')
