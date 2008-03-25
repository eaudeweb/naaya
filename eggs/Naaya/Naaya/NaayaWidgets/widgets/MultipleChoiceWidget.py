# Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Products imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaWidgets.Widget import Widget

class MultipleChoiceWidget(Widget):
    """Abstract class"""
    pass

    # Local properties
    choices = LocalProperty('choices')

    multiplechoice_render_meth = PageTemplateFile('zpt/widget_multiplechoice', globals())

    def __init__(self, id, lang=None, **kwargs):
        self.set_localproperty('choices', 'lines', lang)
        Widget.__init__(self, id, lang, **kwargs)
