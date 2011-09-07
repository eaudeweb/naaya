from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from jsmap import country_code

country_profile_zpt = PageTemplateFile('zpt/country_profile.zpt', globals())

class CountryProfileView(BrowserPage):

    def __call__(self):
        ctx = self.aq_parent
        options = {
            'country_names': sorted(country_code,
                                    key=lambda x: x.lstrip('the ')),
        }
        return country_profile_zpt.__of__(ctx)(**options)
