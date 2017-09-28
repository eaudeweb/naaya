from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, manage_addWidget
from naaya.core.zope2util import path_in_site

def addPointerWidget(container, id="", title="Pointer Widget", REQUEST=None, **kwargs):
    """ Contructor for Pointer widget"""
    return manage_addWidget(PointerWidget, container, id, title, REQUEST, **kwargs)

class PointerWidget(Widget):
    """ Pointer Widget """

    meta_type = "Naaya Schema Pointer Widget"
    meta_label = "Location picker"
    meta_description = "Free text input with location picker."
    meta_sortorder = 150

    _properties = Widget._properties + (
        {'id': 'width', 'type': 'int', 'mode': 'w',
         'label': 'Display width'},
        {'id': 'size_max', 'type': 'int', 'mode': 'w',
         'label': 'Maximum input width'},
        {'id': 'relative', 'type': 'boolean', 'mode': 'w',
         'label': 'Path relative to object'},
        )

    # Constructor
    _constructors = (addPointerWidget,)

    width = 50
    size_max = 0
    relative = False

    def _convert_to_form_string(self, value):
        if isinstance(value, int):
            value = str(value)
        return value

    def initial_jstree_node(self, context):
        if self.relative:
            return path_in_site(context)
        else:
            return ''

    template = PageTemplateFile('../zpt/property_widget_pointer', globals())

InitializeClass(PointerWidget)
