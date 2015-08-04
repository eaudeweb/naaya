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

def addComboboxWidget(container, id="", title="Combobox Widget", REQUEST=None, **kwargs):
    """ Contructor for Combobox widget"""
    return manage_addWidget(ComboboxWidget, container, id, title, REQUEST, **kwargs)

class ComboboxWidget(MultipleChoiceWidget):
    """ Combobox Widget """

    meta_type = "Naaya Combobox Widget"
    meta_label = "Combobox"
    meta_description = "Multiple choice question with only one answer"
    meta_sortorder = 101
    icon_filename = 'widgets/www/widget_combobox.gif'

    _properties = MultipleChoiceWidget._properties + ()

    # Constructor
    _constructors = (addComboboxWidget,)
    render_meth = PageTemplateFile('zpt/widget_combobox.zpt', globals())

    def getDatamodel(self, form):
        """Get datamodel from form"""
        value = form.get(self.getWidgetId(), None)
        if value is None:
            return None
        return int(value)

    def get_value(self, datamodel=None, **kwargs):
        """ Return a string with the data in this widget """
        if datamodel is None:
            return self._get_default_value()
        return str(self.choices[datamodel])

InitializeClass(ComboboxWidget)

def register():
    return ComboboxWidget
