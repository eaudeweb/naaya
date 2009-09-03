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
# Cristian Ciupitu, Eau de Web
# Alex Morega, Eau de Web

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Widget import Widget, WidgetError, manage_addWidget

def addTextAreaWidget(container, id="", title="Lines Widget", REQUEST=None, **kwargs):
    """ Contructor for Lines widget"""
    return manage_addWidget(TextAreaWidget, container, id, title, REQUEST, **kwargs)

class TextAreaWidget(Widget):
    """ Multi-line text Widget """

    meta_type = "Naaya Schema Text Area Widget"
    meta_label = "Paragraph text"
    meta_description = "Multiple line answer, used for longer responses"
    meta_sortorder = 151

    _properties = Widget._properties + (
        {'id': 'rows', 'type': 'int', 'mode': 'w', 'label': 'Display lines'},
        {'id': 'columns', 'type': 'int', 'mode': 'w', 'label': 'Display columns'},
        {'id':'tinymce', 'mode':'w', 'type': 'boolean'},
    )

    # Constructor
    _constructors = (addTextAreaWidget,)

    rows = 10
    columns = 50
    tinymce = False

    def isEmptyDatamodel(self, value):
        return not bool(value)

    template = PageTemplateFile('../zpt/property_widget_textarea', globals())

InitializeClass(TextAreaWidget)
