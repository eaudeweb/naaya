from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget

def addTextAreaWidget(container, id="", title="Lines Widget", REQUEST=None, **kwargs):
    """ Contructor for Lines widget"""
    return manage_addWidget(TextAreaWidget, container, id, title, REQUEST, **kwargs)

class TextAreaWidget(Widget):
    """ Multi-line text Widget """

    meta_type = "Naaya Schema Text Area Widget"
    meta_label = "Paragraph text"
    meta_description = "Multiple line answer, used for longer responses"
    meta_sortorder = 151

    _properties = Widget._properties + (
        {'id': 'rows', 'type': 'int', 'mode': 'w', 'label': 'Display lines'},
        {'id': 'columns', 'type': 'int', 'mode': 'w', 'label': 'Display columns'},
        {'id':'tinymce', 'mode':'w', 'type': 'boolean'},
    )

    # Constructor
    _constructors = (addTextAreaWidget,)

    rows = 10
    columns = 50
    tinymce = False

    template = PageTemplateFile('../zpt/property_widget_textarea', globals())

InitializeClass(TextAreaWidget)
