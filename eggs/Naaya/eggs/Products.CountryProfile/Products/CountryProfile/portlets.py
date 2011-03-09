# -*- coding: utf-8 -*-
""" Country portlets """
from zope import interface, component
from Products.Naaya.interfaces import INySite
from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class CountryPortlet(object):
    """Display this portlet based on country"""
    interface.implements(INyPortlet)
    component.adapts(INySite)

    title = 'Country profile'
    template = PageTemplateFile('zpt/portlets/country_profile', globals())

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        try:
            country_profile = self.site.objectValues("MedwisCountryProfile")[0]
        except:
            return ""
        result = country_profile.query("get_country_code",
                                     label_en=getattr(context, 'title', ""))
        if result:
            country_code = result['CNT_CODE']
        else:
            return ""

        macro = self.site.getPortletsTool()._get_macro(position)
        tmpl = self.template.__of__(context)
        return tmpl(macro=macro, cprofile=country_profile, ccode=country_code)


class CountryComparisions(object):
    """Display this portlet under themes folder"""
    interface.implements(INyPortlet)
    component.adapts(INySite)

    title = 'Country comparisions'
    template = PageTemplateFile('zpt/portlets/country_comparisions', globals())

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        try:
            country_profile = self.site.objectValues("MedwisCountryProfile")[0]
        except:
            return ""

        records = country_profile.query('get_country_comparision',
                                    var='U24',
                                    src='aquastat',
                                    year='2000')

        macro = self.site.getPortletsTool()._get_macro(position)
        tmpl = self.template.__of__(context)
        return tmpl(macro=macro, cprofile=country_profile, records=records)


class YearComparisions(object):
    """Display this portlet under themes folder"""
    interface.implements(INyPortlet)
    component.adapts(INySite)

    title = 'Year comparisions'
    template = PageTemplateFile('zpt/portlets/year_comparisions', globals())

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        try:
            country_profile = self.site.objectValues("MedwisCountryProfile")[0]
        except:
            return ""

        records = country_profile.query('get_year_comparision',
                                    var='U24',
                                    src='aquastat',
                                    cnt='AL')

        macro = self.site.getPortletsTool()._get_macro(position)
        tmpl = self.template.__of__(context)
        return tmpl(macro=macro, cprofile=country_profile, records=records)
