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

def addCheckboxMatrixWidget(container, id="", title="CheckboxMatrix Widget", REQUEST=None, **kwargs):
    """ Contructor for CheckboxMatrix widget"""
    return addWidget(CheckboxMatrixWidget, container, id, title, REQUEST, **kwargs)

class CheckboxMatrixWidget(Widget):
    """ CheckboxMatrix Widget """

    meta_type = "Naaya Checkbox Matrix Widget"
    meta_label = "Checkbox matrix"
    meta_description = "Group of multiple choice questions with multiple answers per row"
    meta_sortorder = 501
    icon_filename = 'widgets/www/widget_checkboxmatrix.gif'

    _properties = Widget._properties + ()

    # Constructor
    _constructors = (addCheckboxMatrixWidget,)
    render_meth = PageTemplateFile('zpt/widget_checkboxmatrix.zpt', globals())

    # Local properties
    choices = LocalProperty('choices')
    rows = LocalProperty('rows')

    def __init__(self, id, lang=None, **kwargs):
        self.set_localproperty('choices', 'lines', lang)
        self.set_localproperty('rows', 'lines', lang)
        Widget.__init__(self, id, lang, **kwargs)

    def getDatamodel(self, form):
        """Get datamodel from form"""
        widget_id = self.getWidgetId()
        value = []
        for i in range(len(self.rows)):
            row_value = form.get('%s_%d' % (widget_id, i), [])
            row_value = [int(x) for x in row_value]
            value.append(row_value)
        return value

    def validateDatamodel(self, value):
        """Validate datamodel"""
        if not self.required:
            return
        unanswered = [x for x in value if not x]
        if unanswered:
            raise WidgetError('Value required for "%s"' % self.title)

InitializeClass(CheckboxMatrixWidget)

def register():
    return CheckboxMatrixWidget
