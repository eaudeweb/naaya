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

# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.NaayaWidgets.Widget import WidgetError, manage_addWidget
from MultipleChoiceWidget import MultipleChoiceWidget

def addRadioWidget(container, id="", title="Radio Widget", REQUEST=None, **kwargs):
    """ Contructor for Radio widget"""
    return manage_addWidget(RadioWidget, container, id, title, REQUEST, **kwargs)

class RadioWidget(MultipleChoiceWidget):
    """ Radio Widget """

    meta_type = "Naaya Radio Widget"
    meta_label = "Radio buttons"
    meta_description = "Multiple choice question with only one answer"
    meta_sortorder = 100
    icon_filename = 'widgets/www/widget_radiobutton.gif'

    security = ClassSecurityInfo()

    _properties = MultipleChoiceWidget._properties + (
        {'id': 'display', 'type': 'selection', 'mode': 'w',
         'select_variable': 'display_modes', 'label': 'Display mode'},
        {'id':'add_extra_choice', 'type': 'boolean','mode':'w', 'label': 'Required widget'},
        )

    # Constructor
    _constructors = (addRadioWidget,)
    render_meth = PageTemplateFile('zpt/widget_radio.zpt', globals())

    display = 'vertical'
    add_extra_choice = False

    def display_modes(self):
        """ """
        return ['vertical', 'horizontal']

    def getChoices(self, REQUEST=None, anyLangNonEmpty=False):
        """ """
        choices = super(RadioWidget, self).getChoices(anyLangNonEmpty=anyLangNonEmpty)
        if self.add_extra_choice:
            L = list(choices)
            catalog = self.getPortalTranslations()
            L.append(catalog('Other', lang=self.gl_get_selected_language(), add=True))
            return L
        else:
            return choices

    def getExtraChoiceInputId(self):
        """ -> the id of the INPUT element used for the extra choice"""
        return "extra_choice_" + self.id


    def getDatamodel(self, form, anyLangNonEmpty=False):
        """Get datamodel from form"""
        choices = super(RadioWidget, self).getChoices(anyLangNonEmpty=anyLangNonEmpty)
        value = form.get(self.getWidgetId(), None)
        if value is None:
            return None
        value = int(value)
        if not self.add_extra_choice:
            return value
        if value != len(choices):
            return (value, None)
        return (value, form.get(self.getExtraChoiceInputId(), None))

    def getChoiceIdx(self, datamodel, REQUEST=None):
        """ -> the choice index from datamodel"""
        if datamodel is None:
            return None
        if not self.add_extra_choice:
            return datamodel
        return datamodel[0]

    def getChoice(self, datamodel, REQUEST=None, anyLangNonEmpty=False):
        """ -> the exact choice made by the respondent; might be the text of the extra choice"""
        choiceIdx = self.getChoiceIdx(datamodel)
        if choiceIdx is None:
            return None
        choices = super(RadioWidget, self).getChoices(anyLangNonEmpty=anyLangNonEmpty)
        if choiceIdx < len(choices):
            return choices[choiceIdx]
        return datamodel[1]

    def get_value(self, datamodel=None, **kwargs):
        """ Return a string with the data in this widget """
        if datamodel is None:
            return self._get_default_value()
        return str(self.getChoice(datamodel))

InitializeClass(RadioWidget)

def register():
    return RadioWidget
