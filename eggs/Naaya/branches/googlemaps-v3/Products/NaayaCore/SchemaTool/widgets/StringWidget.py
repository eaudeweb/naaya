from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget

def addStringWidget(container, id="", title="String Widget", REQUEST=None, **kwargs):
    """ Contructor for String widget"""
    return manage_addWidget(StringWidget, container, id, title, REQUEST, **kwargs)

class StringWidget(Widget):
    """ String Widget """

    meta_type = "Naaya Schema String Widget"
    meta_label = "Single line text"
    meta_description = "Free text input box"
    meta_sortorder = 150

    _properties = Widget._properties + (
        {
            'id': 'width',
            'label': 'Display width',
            'type': 'int',
            'mode': 'w',
        },
        {
            'id': 'size_max',
            'label': 'Maximum input width',
            'type': 'int',
            'mode': 'w',
        },
    )

    # Constructor
    _constructors = (addStringWidget,)

    width = 50
    size_max = 0

    def _convert_to_form_string(self, value):
        if isinstance(value, int):
            value = str(value)
        return value

    template = PageTemplateFile('../zpt/property_widget_string', globals())

InitializeClass(StringWidget)
