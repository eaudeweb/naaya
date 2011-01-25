from zope.publisher.browser import BrowserPage
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

upload_prefix = None

import_zpt = PageTemplateFile('import.zpt', globals())
import_result_zpt = PageTemplateFile('import_result.zpt', globals())

class ImportFromCirca_html(BrowserPage):
    def __call__(self):
        ctx = self.context.aq_inner # because self subclasses from Explicit
        return import_zpt.__of__(ctx)()

class ImportFromCirca(BrowserPage):
    def __call__(self):
        if upload_prefix is None:
            return "upload prefix not configured"
        ctx = self.context.aq_inner # because self subclasses from Explicit
        from edw.circaimport import work_in_zope
        #name = ctx.REQUEST.get('name')
        name = self.request.form['filename']
        report = work_in_zope(ctx, name, upload_prefix)
        return import_result_zpt.__of__(ctx)(report=report)
