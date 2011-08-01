from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.publisher.browser import BrowserPage

bulk_chm_terms_template = PageTemplateFile('zpt/bulk_chm_terms', globals())

class bulk_chm_terms_html(BrowserPage):
    def __call__(self):
        context = self.aq_parent
        glossary_widget = context._get_schema().getWidget('chm_terms')
        template = glossary_widget.render_html('')
        return bulk_chm_terms_template.__of__(context)(template=template)

class bulk_chm_terms_save(BrowserPage):
    def __call__(self, REQUEST):
        chm_terms = REQUEST.get('chm_terms', None)
        if chm_terms:
            for ob in self.aq_parent.objectValues():
                try:
                    widget = ob._get_schema().getWidget('chm_terms')
                except KeyError:
                    #No widget so nothing to do
                    pass
                else:
                    current_prop = ob.getLocalProperty('chm_terms')
                    new_terms = chm_terms
                    if current_prop:
                        current_prop = current_prop.split(widget.separator)
                        new_terms = list(set(new_terms)|set(current_prop))
                    new_terms = widget.convert_formvalue_to_pythonvalue(new_terms)
                    ob._change_schema_properties(chm_terms=new_terms)
        REQUEST.RESPONSE.redirect(self.aq_parent.absolute_url()+'/bulk_chm_terms_html?success=true')

class bulk_chm_terms_delete(BrowserPage):
    def __call__(self, REQUEST):
        for ob in self.aq_parent.objectValues():
            current_prop = ob.getLocalProperty('chm_terms')
            if current_prop:
                ob._change_schema_properties(chm_terms='')
        REQUEST.RESPONSE.redirect(self.aq_parent.absolute_url()+'/bulk_chm_terms_html?success=true')
