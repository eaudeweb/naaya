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
# Alex Morega, Eau de Web


#Python imports
from decimal import Decimal

#Zope imports
from Products.Localizer.LocalAttributes import LocalAttribute

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript
from Products.NaayaBase.NyContentType import NyContentType
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
try:
    import Products.TextIndexNG3
    txng_version = 2
except ImportError:
    txng_version = 0


class UpdateGeotaggedContent(UpdateScript):
    """ Update reinstall content types script  """
    id = 'update_geotagged_content'
    update_id = 'update_geotagged_content'
    title = 'Update geotagged content'

    def _do_update_on_portal(self, portal, report_file, report_only):
        print>>report_file, '<h4>%s</h4>' % '/'.join(portal.getPhysicalPath())
        schema_tool = portal.portal_schemas
        self._update_schemas(schema_tool, report_file, report_only)
        catalog = portal.portal_catalog
        add_indexes(catalog, report_file, report_only)
        enable_geotagged_content(portal, report_file, report_only)
        for brain in catalog():
            ob = brain.getObject()
            if isinstance(ob, NyContentType):
                self._update_ob(ob, schema_tool, report_file, report_only)

    def _update_schemas(self, schema_tool, report_file, report_only):
        from Products.NaayaCore.SchemaTool.widgets.GeoTypeWidget import GeoTypeWidget
        for schema in schema_tool.objectValues():
            defaults = schema.getDefaultDefinition()
            if defaults is None:
                continue

            def print_schema_report(msg):
                print>>report_file, msg, '(%s schema at %s)<br />' % (schema.id, 
                    '/'.join(schema.getPhysicalPath()))

            if schema.id == 'NyGeoPoint':
                # if NyGeoPoint has geo_type widget of type StringWidget, we must replace it.
                if ('geo_type-property' in schema.objectIds()
                  and not isinstance(schema['geo_type-property'], GeoTypeWidget)):
                    print_schema_report('Replacing geo_type property')
                    if not report_only:
                        schema.manage_delObjects(['geo_type-property'])

                # also remove longitude, latitude, address properties
                if 'longitude-property' in schema.objectIds():
                    print_schema_report('Removing longitude property')
                    if not report_only:
                        schema.manage_delObjects(['longitude-property'])

                if 'latitude-property' in schema.objectIds():
                    print_schema_report('Removing latitude property')
                    if not report_only:
                        schema.manage_delObjects(['latitude-property'])

                if 'address-property' in schema.objectIds():
                    print_schema_report('Removing address property')
                    if not report_only:
                        schema.manage_delObjects(['address-property'])

            if 'geo_location-property' not in schema.objectIds():
                if 'geo_location' in defaults:
                    default = defaults['geo_location']
                    print_schema_report('Adding geo_location property')
                    if not report_only:
                        schema.addWidget('geo_location', **default)

            if 'geo_type-property' not in schema.objectIds():
                defaults = schema.getDefaultDefinition()
                if 'geo_type' in defaults:
                    default = defaults['geo_type']
                    print_schema_report('Adding geo_type property')
                    if not report_only:
                        schema.addWidget('geo_type', **default)

    def _update_ob(self, ob, schema_tool, report_file, report_only):
        ob_link = '<a href="%(ob_path)s/manage_workspace">%(ob_path)s</a>' % {
            'ob_path': '/'.join(ob.getPhysicalPath())}
        print>>report_file, span('path', ob_link)
        print>>report_file, '(%s)' % ob.__class__.__name__

        schema = schema_tool.getSchemaForMetatype(ob.meta_type)
        if schema is None:
            print>>report_file, span('action_skip',
                'skipping (no schema)'), '<br/>'
            return

        if not report_only and 'geo_location-property' in schema.objectIds():
            missing_schema_prop = False
        elif report_only and 'geo_location' in (schema.getDefaultDefinition() or {}):
            missing_schema_prop = False
        else:
            missing_schema_prop = True

        if missing_schema_prop:
            print>>report_file, span('action_skip',
                'skipping (geo_location not in schema)'), '<br/>'
            return


        found_lat, lat = fetch_and_remove(ob, 'latitude', report_only)
        found_lon, lon = fetch_and_remove(ob, 'longitude', report_only)
        found_address, address = fetch_and_remove(ob, 'address', report_only)

        if found_lat:
            try:
                Decimal(str(lat))
            except:
                lat = ''

        if found_lon:
            try:
                Decimal(str(lon))
            except:
                lon = ''

        if not (found_lat or found_lon or found_address):
            print>>report_file, span('action_skip',
                'skipping (no old-style geo data)'), '<br/>'
            return

        geo = Geo(str(lat), str(lon), address)
        if geo == Geo(0, 0):
            geo = None

        if not report_only:
            ob.geo_location = geo
            ob.recatalogNyObject(ob)

        print>>report_file, span('action_ok', 'saving value'), repr(geo), '<br/>'

def span(cls, txt):
    return '<span class="%s">%s</span>' % (cls, txt)

def fetch_and_remove(ob, prop_name, report_only):
    found = False
    prop_value = None

    if prop_name in ob.__dict__:
        found = True
        prop_value = ob.__dict__[prop_name]
        if not report_only:
            del ob.__dict__[prop_name]

    if isinstance(prop_value, LocalAttribute):
        # for some reason, prop_value may be a LocalAttribute instance;
        # let's find the real value in _local_properties
        local_props = ob.__dict__['_local_properties']
        if prop_name in local_props:
            for value, timestamp in local_props[prop_name].values():
                if value:
                    prop_value = value
            if not report_only:
                del local_props[prop_name]
                ob._p_changed = 1

    if isinstance(prop_value, LocalAttribute):
        # if prop_value is still a LocalAttribute, we found nothing in
        # _local_properties; let's assign it a blank value and move on.
        prop_value = ''
        
    return found, prop_value

def add_indexes(catalog, report_file, report_only):
    indexes = catalog.indexes()
    if 'geo_location' not in indexes:
        if report_only:
            print>>report_file, span('action_ok', 'adding index'), 'geo_location', '<br/>'
        else:
            try: catalog.addIndex('geo_location', 'FieldIndex')
            except: pass
    else:
        print>>report_file, span('action_skip', 'skipping index (already in catalog)'), 'geo_location', '<br/>'

    if 'geo_address' not in indexes:
        if report_only:
            print>>report_file, span('action_ok', 'adding index'), 'geo_address', '<br/>'
        else:
            if txng_version == 2:
                try: catalog.addIndex('geo_address', 'TextIndexNG3', extra={'default_encoding': 'utf-8'})
                except: pass
            else:
                try: catalog.addIndex('geo_address', 'TextIndex')
                except: pass
    else:
        print>>report_file, span('action_skip', 'skipping index (already in catalog)'), 'geo_address', '<br/>'

def enable_geotagged_content(portal, report_file, report_only):
    portal_control = portal.portal_control
    portal_map = portal.portal_map
    geotaggable_objects = [x['id'] for x in portal_map.list_geotaggable_types() if x['enabled']]
    portal_control_enabled = portal_control.settings.keys()
    if portal_control_enabled:
        for content_type in portal_control_enabled:
            class_name = portal.get_pluggable_item(content_type)['_class'].__name__
            if class_name not in geotaggable_objects:
                geotaggable_objects.append(class_name)
        if report_only:
            print>>report_file, span('action_ok', 'Setting geocodable content'), geotaggable_objects, '<br/>'
        else:
            portal_control.saveSettings(enabled_for=[]) #clear portal_control
            portal_map.admin_set_contenttypes(geotag=geotaggable_objects)
            print>>report_file, span('action_ok', 'Setting geocodable content'), geotaggable_objects, '<br/>'
    else:
        print>>report_file, span('action_skip', 'No geocodable content defined in portal control'), '', '<br/>'