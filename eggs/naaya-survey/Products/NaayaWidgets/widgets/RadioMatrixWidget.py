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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass

# Product imports
from Products.NaayaWidgets.Widget import WidgetError, manage_addWidget

from MatrixWidget import MatrixWidget


def addRadioMatrixWidget(container, id="", title="RadioMatrix Widget",
                         REQUEST=None, **kwargs):
    """ Contructor for RadioMatrix widget"""
    return manage_addWidget(RadioMatrixWidget, container, id, title, REQUEST,
                            **kwargs)


class RadioMatrixWidget(MatrixWidget):
    """ RadioMatrix Widget """

    meta_type = "Naaya Radio Matrix Widget"
    meta_label = "Radio matrix"
    meta_description = ("Group of multiple choice questions with only "
                        "one answer per row")
    meta_sortorder = 500
    icon_filename = 'widgets/www/widget_radiomatrix.gif'

    _properties = MatrixWidget._properties + ()

    # Constructor
    _constructors = (addRadioMatrixWidget,)
    render_meth = PageTemplateFile('zpt/widget_radiomatrix.zpt', globals())

    def getChoices(self, REQUEST=None, anyLangNonEmpty=False):
        return super(RadioMatrixWidget, self).getChoices(
            anyLangNonEmpty=anyLangNonEmpty)

    def getDatamodel(self, form):
        """Get datamodel from form"""
        widget_id = self.getWidgetId()
        value = []
        for i in range(len(self.rows)):
            row_value = form.get('%s_%d' % (widget_id, i), None)
            if row_value is not None:
                row_value = int(row_value)
            value.append(row_value)
        return value

    def validateDatamodel(self, value):
        """Validate datamodel"""
        if not self.required:
            return
        unanswered = [x for x in value if x is None]
        if unanswered:
            raise WidgetError('Value required for "%s"' % self.title)

    def get_value(self, datamodel=None, **kwargs):
        """ Return a string with the data in this widget """
        if datamodel is None:
            return self._get_default_value()
        res = []
        for index, answer in enumerate(datamodel):
            if answer is None:
                data = '-'
            else:
                data = self.choices[answer]
            res.append(data)
        return res

InitializeClass(RadioMatrixWidget)


def register():
    return RadioMatrixWidget
