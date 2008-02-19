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

def addLabelWidget(container, id="", title="Label Widget", REQUEST=None, **kwargs):
    """ Contructor for Label widget"""
    return addWidget(LabelWidget, container, id, title, REQUEST, **kwargs)

class LabelWidget(Widget):
    """ Multi-line text Widget """

    meta_type = "Naaya Label Widget"
    meta_label = "Label"
    meta_description = "Descriptive text, there is no answer to it"
    meta_sortorder = 50
    icon_filename = 'widgets/www/widget_label.gif'

    _properties = Widget._properties + ()

    # Constructor
    _constructors = (addLabelWidget,)
    render_meth = PageTemplateFile('zpt/widget_label.zpt', globals())

    # Local properties
    text = LocalProperty('text')

    def __init__(self, id, lang=None, **kwargs):
        Widget.__init__(self, id, lang, **kwargs)
        self.set_localproperty('text', 'text', lang)

    def getDatamodel(self, form):
        """Get datamodel from form"""
        return None

InitializeClass(LabelWidget)

def register():
    return LabelWidget
