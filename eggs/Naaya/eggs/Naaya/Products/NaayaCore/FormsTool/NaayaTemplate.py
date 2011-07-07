from Products.PageTemplates.PageTemplate import PageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from FormsTool import register_naaya_template

class NaayaPageTemplateFile(PageTemplateFile):
    def __init__(self, filename, _globals, name):
        PageTemplateFile.__init__(self, filename, _globals, __name__=name)
        register_naaya_template(self, name)

    def pt_render(self, *args, **kwargs):
        try:
            site = self.getSite()
        except AttributeError, e:
            # there's no site in our acquisition context
            current_form = self
        else:
            forms_tool = site.getFormsTool()
            current_form = forms_tool[self.__name__]

        current_form = current_form.aq_self.__of__(self.aq_parent)

        return PageTemplate.pt_render(current_form, *args, **kwargs)
