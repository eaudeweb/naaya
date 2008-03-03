# Products imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaWidgets.Widget import Widget

class MatrixWidget(Widget):
    """Abstract class"""

    # Local properties
    choices = LocalProperty('choices')
    rows = LocalProperty('rows')

    def __init__(self, id, lang=None, **kwargs):
        Widget.__init__(self, id, lang, **kwargs)
        self.set_localproperty('choices', 'lines', lang)
        self.set_localproperty('rows', 'lines', lang)
