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
# Cristian Romanescu, Eau de Web
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
        {'id':'list_id', 'mode':'w', 'type': 'str'},
    )

    list_id = None
    data_type = 'list'

    def get_selection_list(self):
        list_ob = self.getPortletsTool().getRefListById(self.list_id)
        if list_ob is None:
            raise ValueError('Could not find selection list "%s"' % self.list_id)
        return list_ob.get_list()

    def isEmptyDatamodel(self, value):
        return not bool(value)

    template = PageTemplateFile('../zpt/property_widget_select_multiple', globals())
