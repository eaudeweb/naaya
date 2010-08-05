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

"""
Patch for FormsTool
"""

#Python imports

#Zope imports
from Products.NaayaCore.FormsTool.FormsTool import FormsTool

_properties = (
    {'id': 'title', 'label': 'Title', 'type': 'string', 'mode': 'w'},
    {'id': 'custom_forms', 'label': 'These forms...', 'type': 'lines', 'mode': 'w'},
    {'id': 'custom_skin',
     'label': '...will use this layout.color-scheme \n (Example: chm.blue)',
     'type': 'string', 'mode': 'w'},
)

FormsTool.custom_forms = (
    'admin_.',
    '.+_add_html',
    'edit_html',
)

FormsTool.custom_skin = 'chm-admin.default'

FormsTool._properties = _properties
