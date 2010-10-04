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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web
# Cristian Ciupitu, Eau de Web

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.NaayaWidgets.Widget import WidgetError, manage_addWidget

from MultipleChoiceWidget import MultipleChoiceWidget

def addCheckboxesWidget(container, id="", title="Checkboxes Widget", REQUEST=None, **kwargs):
    """ Contructor for Checkboxes widget"""
    return manage_addWidget(CheckboxesWidget, container, id, title, REQUEST, **kwargs)

class CheckboxesWidget(MultipleChoiceWidget):
    """ Checkboxes Widget """

    meta_type = "Naaya Checkboxes Widget"
    meta_label = "Checkboxes"
    meta_description = "Multiple choice question with multiple answers"
    meta_sortorder = 102
    icon_filename = 'widgets/www/widget_checkbox.gif'

    _properties = MultipleChoiceWidget._properties + (
        {'id': 'display', 'type': 'selection', 'mode': 'w',
         'select_variable': 'display_modes', 'label': 'Display mode'},
        )

    # Constructor
    _constructors = (addCheckboxesWidget,)
    render_meth = PageTemplateFile('zpt/widget_checkboxes.zpt', globals())

    display = 'vertical'

    def display_modes(self):
        """ """
        return ['vertical', 'horizontal']

    def getDatamodel(self, form):
        """Get datamodel from form"""
        value_list = form.get(self.getWidgetId(), None)
        if value_list is None:
            return None
        return [int(x) for x in value_list]

    def validateDatamodel(self, value):
        """Validate datamodel"""
        if self.required and not value:
            raise WidgetError('Value required for "%s"' % self.title)

    def get_value(self, datamodel=None, **kwargs):
        """ Return a string with the data in this widget """
        if not datamodel:
            return self._get_default_value()
        res = []
        for answer in datamodel:
            res.append(self.choices[answer])
        return ', '.join(res)

InitializeClass(CheckboxesWidget)

def register():
    return CheckboxesWidget
