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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web
# Andrei Laza, Eau de Web


#Python imports

#Zope imports
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript
from Products.naayaUpdater.utils import get_portals

from Products.NaayaCore.SchemaTool.widgets.Widget import widgetid_from_propname

try:
    from naaya.content.base.discover import get_pluggable_content
except ImportError:
    from Products.NaayaContent.discover import get_pluggable_content

try:
    from Products.NaayaCore.constants import ID_SCHEMATOOL
except ImportError:
    # we're probably on an old Naaya version with no Schema code
    pass

class UpdatePortalSchemas(UpdateScript):
    """ Update portal schemas script """
    title = 'Update portal schemas'
    authors = ['David Batranu']
    creation_date = 'Jan 01, 2010'

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/update_schemas', globals())

    security.declareProtected(view_management_screens, 'find_schema_differences')
    def find_schema_differences(self):
        """
        Searches for schema properties that differ
        from their definition in their content code
        """
        content_types = get_pluggable_content().values()
        portals = get_portals(self)
        missing_properties = {}
        modified_properties = {}
        for portal in portals:
            schema = portal._getOb(ID_SCHEMATOOL, None)
            if schema:
                 modified_properties[portal] = self.find_modified_schema_properties(content_types, schema)
                 missing_properties[portal] = self.find_missing_schema_properties(content_types, schema)
        return {'missing_properties': missing_properties, 'modified_properties': modified_properties}

    security.declareProtected(view_management_screens, 'find_missing_schema_properties')
    def find_missing_schema_properties(self, content_types, schema):
        result = {}
        for content_type in content_types:
            content_schema = getattr(content_type['_module'], 'DEFAULT_SCHEMA', {})
            if content_schema:
                for property in content_schema.keys():
                    try:
                        schema.getSchemaForMetatype(content_type['meta_type']).getWidget(property)
                    except KeyError:
                        result.setdefault(content_type['meta_type'], []).append(property)
        return result

    security.declareProtected(view_management_screens, 'find_modified_schema_properties')
    def find_modified_schema_properties(self, content_types, schema):
        result = {}
        for content_type in content_types:
            content_schema = getattr(content_type['_module'], 'DEFAULT_SCHEMA', {})
            if content_schema:
                for property in content_schema.keys():
                    fs_widget_type = content_schema[property]['widget_type']
                    try:
                        portal_widget_type = schema.getSchemaForMetatype(content_type['meta_type']).getWidget(property).get_widget_type()
                    except KeyError:
                        continue
                    if fs_widget_type != portal_widget_type:
                        result.setdefault(content_type['meta_type'], {})[property] = {'fs': fs_widget_type, 'site': portal_widget_type}
        return result

    security.declareProtected(view_management_screens, 'add_missing_schema_property')
    def add_missing_schema_property(self, property_data, REQUEST=None):
        """ """
        for prop in property_data:
            location = prop.split('||')
            portal = location[0]
            content_type = location[1]
            property = location[2]
            property_schema = get_pluggable_content()[content_type]['default_schema'][property]

            portal = self.unrestrictedTraverse(portal, None)
            schema_tool = portal._getOb(ID_SCHEMATOOL, None)
            schema = schema_tool.getSchemaForMetatype(content_type)
            schema.addWidget(property, **property_schema)

        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/update_schemas_html?find=true' % self.absolute_url())

    security.declareProtected(view_management_screens, 'update_modified_schema_property')
    def update_modified_schema_property(self, property_data, REQUEST=None):
        """ """
        for prop in property_data:
            location = prop.split('||')
            portal = location[0]
            content_type = location[1]
            property = location[2]
            property_schema = get_pluggable_content()[content_type]['default_schema'][property]

            portal = self.unrestrictedTraverse(portal, None)
            schema_tool = portal._getOb(ID_SCHEMATOOL, None)
            schema = schema_tool.getSchemaForMetatype(content_type)
            schema.manage_delObjects([widgetid_from_propname(property)])
            schema.addWidget(property, **property_schema)

        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/update_schemas_html?find=true' % self.absolute_url())
