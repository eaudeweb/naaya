from zope.interface import implements
from zope.component import adapts

from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

from interfaces import IEWSite

class ObjectListingPortlet(object):
    implements(INyPortlet)
    adapts(IEWSite)

    title = 'List contained objects'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        return self.template.__of__(context)()

    template = NaayaPageTemplateFile('zpt/listing_portlet', globals(),
                                     'naaya.envirowindows.folder.listing_portlet')


class AdministrationPortlet(object):
    implements(INyPortlet)
    adapts(IEWSite)

    title = 'Administration'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(macro=macro)

    template = NaayaPageTemplateFile('skel/portlets/portlet_administration', globals(),
                                     'Products.EnviroWindows.portlets.portlet_administration')
