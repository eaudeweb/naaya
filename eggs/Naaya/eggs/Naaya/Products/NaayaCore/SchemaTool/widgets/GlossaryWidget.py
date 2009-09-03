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
# Alex Morega, Eau de Web

from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo

from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Widget import WidgetError, manage_addWidget
from StringWidget import StringWidget

def addGlossaryWidget(container, id="", title="Glossary Widget", REQUEST=None, **kwargs):
    """ Contructor for Glossary widget"""
    return manage_addWidget(GlossaryWidget, container, id, title, REQUEST, **kwargs)

class GlossaryWidget(StringWidget):
    """ Glossary Widget """

    security = ClassSecurityInfo()

    meta_type = "Naaya Schema Glossary Widget"
    meta_label = "Glossary"
    _constructors = (addGlossaryWidget,)

    _properties = StringWidget._properties + (
        {'id':'glossary_id', 'mode':'w', 'type': 'str'},
    )

    glossary_id = None

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ Update glossary widget properties"""

        def get_prop(prop):
            return (REQUEST or {}).get(prop, kwargs.get(prop, None))

        self.glossary_id = get_prop('glossary_id')

        if get_prop('all_content_types'):
            for schema in self.getParentNode().getParentNode().objectValues():
                if self.id in schema.objectIds([self.meta_type]):
                    schema._getOb(self.id).glossary_id = self.glossary_id

        return super(GlossaryWidget, self).saveProperties(REQUEST=REQUEST, **kwargs)

    def get_glossary(self):
        site = self.getSite()
        if self.glossary_id in site.objectIds(['Naaya Glossary', 'Naaya Thesaurus']):
            return site._getOb(self.glossary_id)

    template = PageTemplateFile('../zpt/property_widget_glossary', globals())

    admin_html_template = StringWidget.admin_html
    admin_html = PageTemplateFile('../zpt/admin_schema_property_glossary', globals())

InitializeClass(GlossaryWidget)
