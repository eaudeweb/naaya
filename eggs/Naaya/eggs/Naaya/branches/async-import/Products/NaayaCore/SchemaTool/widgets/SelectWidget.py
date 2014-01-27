from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget

def addSelectWidget(container, id="", title="Select Widget", REQUEST=None, **kwargs):
    """ Contructor for Select widget"""
    return manage_addWidget(SelectWidget, container, id, title, REQUEST, **kwargs)

class SelectWidget(Widget):
    """ Select Widget """

    meta_type = "Naaya Schema Select Widget"
    meta_label = "Select from list"
    meta_description = "Value selection from a list of possible values"
    meta_sortorder = 150

    # Constructor
    _constructors = (addSelectWidget,)

    _properties = Widget._properties + (
        {'id':'list_id', 'mode':'w', 'type': 'string'},
    )

    list_id = ''
    help_text = u'Click on the items from the list below to select/deselect \
    them.'

    def get_selection_list(self):
        listing = self.get_list_nodes(self.list_id)
        if listing == []:
            return None
        return listing

    def list_is_tree(self):
        ptool = self.getPortletsTool()
        if ptool.getRefTreeById(self.list_id):
            return True

    def _convert_to_form_string(self, value):
        if isinstance(value, int):
            value = str(value)
        return value

    template = PageTemplateFile('../zpt/property_widget_select', globals())
