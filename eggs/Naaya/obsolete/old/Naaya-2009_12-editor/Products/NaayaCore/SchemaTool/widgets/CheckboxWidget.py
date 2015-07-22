# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
# Alex Morega, Eau de Web

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
            return str(value)
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

    template = PageTemplateFile('../zpt/property_widget_checkbox', globals())

InitializeClass(CheckboxWidget)
