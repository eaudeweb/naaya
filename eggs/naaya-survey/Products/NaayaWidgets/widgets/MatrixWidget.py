# Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Products imports
from naaya.i18n.LocalPropertyManager import LocalProperty
from Products.NaayaWidgets.Widget import Widget

class MatrixWidget(Widget):
    """Abstract class"""

    # Local properties
    choices = LocalProperty('choices')
    rows = LocalProperty('rows')

    # macros
    matrix_render_meth = PageTemplateFile('zpt/widget_matrix', globals())

    def __init__(self, id, lang=None, **kwargs):
        Widget.__init__(self, id, lang, **kwargs)
        choices = kwargs.get('choices', [])
        self.set_localproperty('choices', 'lines', lang, choices)
        rows = kwargs.get('rows', [])
        self.set_localproperty('rows', 'lines', lang, rows)

    def getChoices(self, anyLangNonEmpty=False):
        """ """
        if anyLangNonEmpty and not self.choices:
            return self.getLocalAttribute('choices', langFallback=True)
        else:
            return self.choices
