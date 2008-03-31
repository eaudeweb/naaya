# Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Products imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Globals import InitializeClass
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaWidgets.Widget import Widget

class MultipleChoiceWidget(Widget):
    """Abstract class"""

    security = ClassSecurityInfo()

    # Local properties
    choices = LocalProperty('choices')

    # macros
    multiplechoice_render_meth = PageTemplateFile('zpt/widget_multiplechoice', globals())

    def __init__(self, id, lang=None, **kwargs):
        self.set_localproperty('choices', 'lines', lang)
        Widget.__init__(self, id, lang, **kwargs)

    security.declareProtected(view, 'getChoices')
    def getChoices(self):
        """ """
        return self.choices

InitializeClass(MultipleChoiceWidget)
