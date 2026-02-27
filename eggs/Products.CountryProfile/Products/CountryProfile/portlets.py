# -*- coding: utf-8 -*-
""" Country portlets """
from zope import interface, component
from Products.Naaya.interfaces import INySite
from Products.NaayaCore.PortletsTool.interfaces import INyPortlet
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

@interface.implementer(INyPortlet)
@component.adapter(INySite)
class CountryPortlet(object):
    """Display this portlet based on country"""

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


@interface.implementer(INyPortlet)
@component.adapter(INySite)
class CountryComparisions(object):
    """Display this portlet under themes folder"""

    title = 'Country comparisons'
    template = PageTemplateFile('zpt/portlets/country_comparisions', globals())

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        try:
            country_profile = self.site.objectValues("MedwisCountryProfile")[0]
        except:
            return ""
        form = context.REQUEST.form
        records = country_profile.query('get_country_comparision',
                                    var=form.get('country-var', 'U24'),
                                    src=form.get('country-src', 'aquastat'),
                                    year=form.get('year', '1990'))

        macro = self.site.getPortletsTool()._get_macro(position)
        tmpl = self.template.__of__(context)
        return tmpl(macro=macro, cprofile=country_profile, records=records)


@interface.implementer(INyPortlet)
@component.adapter(INySite)
class YearComparisions(object):
    """Display this portlet under themes folder"""

    title = 'Year comparisons'
    template = PageTemplateFile('zpt/portlets/year_comparisions', globals())

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        try:
            country_profile = self.site.objectValues("MedwisCountryProfile")[0]
        except:
            return ""
        form = context.REQUEST.form
        records = country_profile.query('get_year_comparision',
                                    var=form.get('year-var', 'U24'),
                                    src=form.get('year-src', 'aquastat'),
                                    cnt=form.get('cnt_code', 'AL'))

        macro = self.site.getPortletsTool()._get_macro(position)
        tmpl = self.template.__of__(context)
        return tmpl(macro=macro, cprofile=country_profile, records=records)


@interface.implementer(INyPortlet)
@component.adapter(INySite)
class SourceComparisions(object):
    """Display this portlet under themes folder"""

    title = 'Data source comparisons'
    template = PageTemplateFile('zpt/portlets/source_comparisions', globals())

    def __init__(self, site):
        self.site = site

    def __call__(self, context, position):
        try:
            country_profile = self.site.objectValues("MedwisCountryProfile")[0]
        except:
            return ""

        form = context.REQUEST.form
        records, sources, years = country_profile.query('get_source_comparision_grouped',
                                    var=form.get('var', 'U24'),
                                    cnt=form.get('cnt_code', 'AL'))

        macro = self.site.getPortletsTool()._get_macro(position)
        tmpl = self.template.__of__(context)
        return tmpl(macro=macro, cprofile=country_profile, records=records, sources=sources, years=years)
