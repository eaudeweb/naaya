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
        {'id':'list_id', 'mode':'w', 'type': 'str'},
    )

    list_id = None

    def get_selection_list(self):
        list_ob = self.getPortletsTool().getRefListById(self.list_id)
        if list_ob is None:
            raise ValueError('Could not find selection list "%s"' % self.list_id)
        return list_ob.get_list()

    def isEmptyDatamodel(self, value):
        return not bool(value)

    def _convert_to_form_string(self, value):
        if isinstance(value, int):
            value = str(value)
        return value

    template = PageTemplateFile('../zpt/property_widget_select', globals())
