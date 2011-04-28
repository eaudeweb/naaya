from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.NaayaWidgets.Widget import Widget, WidgetError, manage_addWidget
from Products.NaayaWidgets.widgets.StringWidget import StringWidget

def addLocalizedStringWidget(container, id="", title="Localized String Widget",
                             REQUEST=None, **kwargs):
    """ """
    return manage_addWidget(LocalizedStringWidget, container, id, title,
                            REQUEST, **kwargs)

class LocalizedStringWidget(StringWidget):
    """ """
    meta_type = "Naaya Localized String Widget"
    meta_label = "Single line text (localized)"
    meta_description = "Free text input box that can be translated"

    localized = True

    # Constructor
    _constructors = (addLocalizedStringWidget,)
    render_meth = PageTemplateFile('zpt/widget_localized_string.zpt', globals())

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

InitializeClass(LocalizedStringWidget)

def register():
    return LocalizedStringWidget
