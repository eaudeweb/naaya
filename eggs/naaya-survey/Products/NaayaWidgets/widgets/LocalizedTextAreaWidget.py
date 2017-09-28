from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.NaayaWidgets.Widget import Widget, WidgetError, manage_addWidget
from Products.NaayaWidgets.widgets.TextAreaWidget import TextAreaWidget

def addLocalizedTextAreaWidget(container, id="", title="Localized Lines Widget",
                             REQUEST=None, **kwargs):
    """ """
    return manage_addWidget(LocalizedTextAreaWidget, container, id, title,
                            REQUEST, **kwargs)

class LocalizedTextAreaWidget(TextAreaWidget):
    """ """
    meta_type = "Naaya Localized Text Area Widget"
    meta_label = "Paragraph text (localized)"
    meta_description = "Multiple line answer that can be translated, used for longer responses"

    localized = True

    # Constructor
    _constructors = (addLocalizedTextAreaWidget,)
    render_meth = PageTemplateFile('zpt/widget_localized_textarea.zpt',
                                   globals())

    def isEmptyDatamodel(self, value):
        return not bool(value)

    def getDatamodel(self, form):
        """Get datamodel from form"""
        ret = {}
        widget_id = self.getWidgetId()

        for lang in self.gl_get_languages_mapping():
            lang_code = lang['code']
            field_name = "%s-%s" % (self.getWidgetId(), lang_code)

            value = form.get(field_name, None)
            if value:
                ret[lang_code] = value

        return ret

InitializeClass(LocalizedTextAreaWidget)

def register():
    return LocalizedTextAreaWidget
