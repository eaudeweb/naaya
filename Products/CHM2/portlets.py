from zope import interface, component

from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

from interfaces import ICHMSite

class AdministrationPortlet(object):
    interface.implements(INyPortlet)
    component.adapts(ICHMSite)

    title = 'Administration'

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(macro=macro)

    template = NaayaPageTemplateFile('skel/portlets/portlet_administration', globals(),
                                     'Products.CHM2.portlets.portlet_administration')


NaayaPageTemplateFile('skel-chm3/portlets/portlet_administration', globals(),
                      'Products.CHM2.portlets.portlet_administration', 'CHM3')


class CHMTermsTagCloudPortlet(object):
    interface.implements(INyPortlet)
    component.adapts(ICHMSite)

    title = 'CHM Terms'

    def __init__(self, site):
        self.site = site

    def chm_terms_frequency(self):
        attribute = 'chm_terms'
        separator = '|'
        lang = self.site.gl_get_selected_language()

        objects = self.site.getCatalogedObjectsCheckView(
            meta_type=['Naaya Folder',
                'Naaya Photo Folder', 'Naaya Photo Gallery', 'Naaya Contact',
                'Naaya Survey', 'Naaya Educational Product', 'Naaya News',
                'Naaya Story', 'Naaya File', 'Naaya URL', 'Naaya Extended File',
                'Naaya Document', 'Naaya Event', 'Naaya Media File', 'Naaya Pointer',
                'Naaya Blob File', 'Naaya Localized Blob File', 'Naaya GeoPoint'])

        ret = {}
        for ob in objects:
            if ob.hasLocalProperty(attribute):
                value = ob.getLocalAttribute(attribute, lang)
            elif hasattr(ob, attribute):
                value = getattr(ob, attribute)
            else:
                continue

            if not value or not isinstance(value, basestring):
                continue

            for raw_term in value.split(separator):
                term = raw_term.strip()
                ret.setdefault(term, 0)
                ret[term] += 1

        return ret

    def __call__(self, context, position):
        macro = self.site.getPortletsTool()._get_macro(position)
        return self.template.__of__(context)(macro=macro,
                                             tags=self.chm_terms_frequency())

    template = NaayaPageTemplateFile('skel/portlets/portlet_chmterms_tagcloud', globals(),
                                     'Products.CHM2.portlets.portlet_chmterms_tagcloud')
