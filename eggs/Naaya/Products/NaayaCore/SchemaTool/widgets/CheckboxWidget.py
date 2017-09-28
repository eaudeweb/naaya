from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget

def addCheckboxWidget(container, id="", title="Checkbox Widget", REQUEST=None, **kwargs):
    """ Contructor for Checkbox widget"""
    return manage_addWidget(CheckboxWidget, container, id, title, REQUEST, **kwargs)

class CheckboxWidget(Widget):
    """ Checkbox Widget """

    meta_type = "Naaya Schema Checkbox Widget"
    meta_label = "Checkbox"
    _constructors = (addCheckboxWidget,)

    default = 0

    def render_meth(self):
        """ """
        raise NotImplementedError

    def parseFormData(self, data):
        """Get datamodel from form"""
        return bool(data)

    def validateDatamodel(self, value):
        """Validate datamodel"""
        pass

    def _convert_to_form_string(self, value):
        if isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return bool(value)
        else:
            return value

    def convert_from_user_string(self, value):
        """ Convert a user-readable string to a value that can be saved """
        if self.getDataType() is bool:
            value_map = {'yes': True, 'no': False, '': False}
            if value not in value_map:
                raise ValueError('Values for "%s" must be "yes", "no" or blank'
                    % self.title_or_id())
            return value_map[value]
        else:
            return value

    def convert_to_user_string(self, value):
        """ Convert a database value to a user-readable string """
        if self.getDataType() is bool:
            value_map = {True: 'yes', False: 'no'}
            return value_map[bool(value)]
        else:
            return value

    def convert_formvalue_to_pythonvalue(self, value):
        if value is None:
            return 0
        else:
            return int(bool(value))

    template = PageTemplateFile('../zpt/property_widget_checkbox', globals())

    hidden_template = PageTemplateFile('../zpt/property_widget_checkbox_hidden', globals())

InitializeClass(CheckboxWidget)
