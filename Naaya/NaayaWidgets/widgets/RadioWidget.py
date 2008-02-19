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
from Products.Localizer.LocalPropertyManager import LocalProperty

from Products.NaayaWidgets.Widget import Widget, WidgetError, addWidget

from MultipleChoiceWidget import MultipleChoiceWidget

def addRadioWidget(container, id="", title="Radio Widget", REQUEST=None, **kwargs):
    """ Contructor for Radio widget"""
    return addWidget(RadioWidget, container, id, title, REQUEST, **kwargs)

class RadioWidget(MultipleChoiceWidget):
    """ Radio Widget """

    meta_type = "Naaya Radio Widget"
    meta_label = "Radio buttons"
    meta_description = "Multiple choice question with only one answer"
    meta_sortorder = 100
    icon_filename = 'widgets/www/widget_radiobutton.gif'

    _properties = Widget._properties + (
        {'id': 'display', 'type': 'selection', 'mode': 'w',
         'select_variable': 'display_modes', 'label': 'Display mode'},
        )

    # Constructor
    _constructors = (addRadioWidget,)
    render_meth = PageTemplateFile('zpt/widget_radio.zpt', globals())
    
    display = 'vertical'
    
    # Local properties
    choices = LocalProperty('choices')

    def __init__(self, id, lang=None, **kwargs):
        self.set_localproperty('choices', 'lines', lang)
        Widget.__init__(self, id, lang, **kwargs)

    def display_modes(self):
        """ """
        return ['vertical', 'horizontal']

    def getDatamodel(self, form):
        """Get datamodel from form"""
        value = form.get(self.getWidgetId(), None)
        if value is None:
            return None
        return int(value)

InitializeClass(RadioWidget)

def register():
    return RadioWidget
