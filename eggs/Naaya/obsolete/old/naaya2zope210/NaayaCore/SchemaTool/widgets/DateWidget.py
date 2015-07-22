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
# Cristian Ciupitu, Eau de Web
# Alex Morega, Eau de Web

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Product imports
from Widget import Widget, WidgetError, manage_addWidget


def addDateWidget(container, id="", title="Date Widget", REQUEST=None, **kwargs):
    """ Contructor for Date widget"""
    return manage_addWidget(DateWidget, container, id, title, REQUEST, **kwargs)

class DateWidget(Widget):
    """Date Widget"""

    meta_type = "Naaya Schema Date Widget"
    meta_label = "Date"
    meta_description = "A valid date chosen by the user"
    meta_sortorder = 200

    _properties = Widget._properties + ()

    # Constructor
    _constructors = (addDateWidget,)

    def parseFormData(self, value):
        """Get datamodel from form"""
        if not value:
            return None
        try:
            day, month, year = [int(i) for i in value.strip().split('/')]
            value = DateTime(year, month, day)
        except:
            raise WidgetError('Invalid date string for "%s"' % self.title)
        return value

    def _convert_to_form_string(self, value):
        if isinstance(value, DateTime):
            value = value.strftime('%d/%m/%Y')
        return value

    template = PageTemplateFile('../zpt/property_widget_date', globals())

InitializeClass(DateWidget)
