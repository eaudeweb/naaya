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
# Alex Morega, Eau de Web

# Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# Product imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaWidgets.Widget import manage_addWidget

from MatrixWidget import MatrixWidget

def addComboboxMatrixWidget(container, id="", title="ComboboxMatrix Widget", REQUEST=None, **kwargs):
    """ Contructor for ComboboxMatrix widget"""
    return manage_addWidget(ComboboxMatrixWidget, container, id, title, REQUEST, **kwargs)

class ComboboxMatrixWidget(MatrixWidget):
    """ ComboboxMatrix Widget """

    meta_type = "Naaya Combobox Matrix Widget"
    meta_label = "Combobox matrix"
    meta_description = "Group of multiple choice questions with multiple answers per row"
    meta_sortorder = 502
    icon_filename = 'widgets/www/widget_comboboxmatrix.gif'

    _properties = MatrixWidget._properties + ()

    values = LocalProperty('values')

    # Constructor
    _constructors = (addComboboxMatrixWidget,)
    render_meth = PageTemplateFile('zpt/widget_comboboxmatrix.zpt', globals())

    def __init__(self, id, lang=None, **kwargs):
        MatrixWidget.__init__(self, id, lang, **kwargs)
        self.set_localproperty('values', 'lines', lang)

    def getDatamodel(self, form):
        """Get datamodel from form"""
        widget_id = self.getWidgetId()
        value = []
        for i in range(len(self.rows)):
            row_value = []
            for j in range(len(self.choices)):
                choice_value = form.get('%s_%d_%d' % (widget_id, i, j), None)
                if choice_value is not None:
                    choice_value = int(choice_value)
                row_value.append(choice_value)
            value.append(row_value)
        return value

    def validateDatamodel(self, value):
        """Validate datamodel"""
        if not self.required:
            return
        unanswered = [x for x in value if not x]
        if unanswered:
            raise WidgetError('Value required for "%s"' % self.title)

    def render_csv(self, datamodel=None, **kwargs):
        """ Customize render_csv for this widget type """
        if datamodel is None:
            return self._render_default_csv()

        res = []
        for index, row_answers in enumerate(datamodel):
            title = self.rows[index]
            value = []
            if not row_answers:
                res.append('%s: No response' % title)
                continue
            for answer in row_answers:
                value.append(self.choices[answer])
            value = ', '.join(value)
            res.append('%s: %s' % (title, value))
        res = '\n'.join(res)
        return self._escape(res)

InitializeClass(ComboboxMatrixWidget)

def register():
    return ComboboxMatrixWidget
