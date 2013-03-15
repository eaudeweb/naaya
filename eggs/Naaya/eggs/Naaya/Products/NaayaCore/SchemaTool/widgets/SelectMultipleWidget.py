from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, manage_addWidget

def addSelectMultipleWidget(container, id="", title="Multiple Select Widget", REQUEST=None, **kwargs):
    """ Contructor for Multiple Select widget"""
    return manage_addWidget(SelectMultipleWidget, container, id, title, REQUEST, **kwargs)

class SelectMultipleWidget(Widget):
    """ Multiple Select Widget """

    meta_type = "Naaya Schema Multiple Select Widget"
    meta_label = "Multiple selection from list"
    meta_description = "Multiple value selection from a list of possible values"
    meta_sortorder = 150

    # Constructor
    _constructors = (addSelectMultipleWidget,)

    _properties = Widget._properties + (
        {'id':'list_id', 'mode':'w', 'type': 'string'},
    )

    list_id = ''
    data_type = 'list'
    help_text = (u'Click on one or more items from the list below to '
                  u'select/deselect them.')

    def convert_from_user_string(self, value):
        """ Convert a user-readable string to a value that can be saved """
        list_values = {}
        for node in self.get_list_nodes(self.list_id):
            list_values[node.title] = node.id
        return [list_values[val.strip()] for val in value.split(';')]

    def convert_to_user_string(self, values):
        """ Convert the list value to a user-readable string """
        list_values = {}
        for node in self.get_list_nodes(self.list_id):
            list_values[node.id] = node.title
        return ';'.join([list_values.get(value, value) for value in values])

    def get_selection_list(self):
        listing = self.get_list_nodes(self.list_id)
        if listing == []:
            return None
        return listing

    def list_is_tree(self):
        ptool = self.getPortletsTool()
        if ptool.getRefTreeById(self.list_id):
            return True

    hidden_template = PageTemplateFile('../zpt/property_widget_hidden_multiple', globals())

    template = PageTemplateFile('../zpt/property_widget_select_multiple', globals())
