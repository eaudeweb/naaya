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
from naaya.i18n.LocalPropertyManager import LocalAttribute

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaBase.NyContentType import NyContentType
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
try:
    import Products.TextIndexNG3
    txng_version = 2
except ImportError:
    txng_version = 0


class UpdateGeotaggedContent(UpdateScript):
    """ Update reinstall content types script  """
    title = 'Update geotagged content'
    creation_date = 'Jul 10, 2009'
    authors = ['Alex Morega']
    description = 'Converts geo data storage'

    def _update(self, portal):
        self.log.debug('/'.join(portal.getPhysicalPath()))
        schema_tool = portal.portal_schemas
        self._update_schemas(schema_tool)
        catalog = portal.portal_catalog
        add_indexes(catalog, self.log)
        if hasattr(portal, 'portal_control') and \
           "Broken" not in portal['portal_control'].meta_type:
            enable_geotagged_content(portal, self.log)
        for brain in catalog():
            ob = brain.getObject()
            if isinstance(ob, NyContentType):
                self._update_ob(portal, ob, schema_tool)
        return True

    def _update_schemas(self, schema_tool):
        from Products.NaayaCore.SchemaTool.widgets.GeoTypeWidget import GeoTypeWidget
        for schema in schema_tool.objectValues():
            defaults = schema.getDefaultDefinition()
            if defaults is None:
                continue

            def print_schema_report(msg):
                self.log.debug(msg + ' (%s schema at %s)' % (schema.id, 
                    '/'.join(schema.getPhysicalPath())))

            if schema.id == 'NyGeoPoint':
                # if NyGeoPoint has geo_type widget of type StringWidget, we must replace it.
                if ('geo_type-property' in schema.objectIds()
                  and not isinstance(schema['geo_type-property'], GeoTypeWidget)):
                    print_schema_report('Replacing geo_type property')
                    schema.manage_delObjects(['geo_type-property'])

                # also remove longitude, latitude, address properties
                if 'longitude-property' in schema.objectIds():
                    print_schema_report('Removing longitude property')
                    schema.manage_delObjects(['longitude-property'])

                if 'latitude-property' in schema.objectIds():
                    print_schema_report('Removing latitude property')
                    schema.manage_delObjects(['latitude-property'])

                if 'address-property' in schema.objectIds():
                    print_schema_report('Removing address property')
                    schema.manage_delObjects(['address-property'])

            if 'geo_location-property' not in schema.objectIds():
                if 'geo_location' in defaults:
                    default = defaults['geo_location']
                    print_schema_report('Adding geo_location property')
                    schema.addWidget('geo_location', **default)

            if 'geo_type-property' not in schema.objectIds():
                defaults = schema.getDefaultDefinition()
                if 'geo_type' in defaults:
                    default = defaults['geo_type']
                    print_schema_report('Adding geo_type property')
                    schema.addWidget('geo_type', **default)

    def _update_ob(self, portal, ob, schema_tool):
        ob_info = '(%s)' % ob.__class__.__name__ + '/'.join(ob.getPhysicalPath())

        schema = schema_tool.getSchemaForMetatype(ob.meta_type)
        if schema is None:
            self.log.debug(ob_info + ' skipping (no schema)')
            return

        if 'geo_location-property' in schema.objectIds():
            missing_schema_prop = False
        else:
            missing_schema_prop = True

        if missing_schema_prop:
            self.log.debug(ob_info + ' skipping (geo_location not in schema)')
            return


        found_lat, lat = fetch_and_remove(ob, 'latitude')
        found_lon, lon = fetch_and_remove(ob, 'longitude')
        found_address, address = fetch_and_remove(ob, 'address')
        found_geo_location = ('geo_location' in ob.__dict__)

        if found_geo_location:
            self.log.debug(ob_info + ' skipping (already has geo_location value)')
            return

        def normalize_coord(found, value):
            if not found:
                return None
            elif isinstance(value, float):
                if value:
                    return str(value)
                else:
                    return None
            elif isinstance(value, basestring):
                try:
                    if Decimal(value):
                        return value
                    else:
                        return None
                except:
                    return None
            else:
                return None

        lat = normalize_coord(found_lat, lat)
        lon = normalize_coord(found_lon, lon)


        if not (found_lat or found_lon or found_address):
            self.log.debug(ob_info + ' skipping (no old-style geo data)')
            return

        geo = Geo(lat, lon, address)
        if geo in (Geo(0, 0), Geo()):
            geo = None

        self.log.debug(ob_info + ' saving value ' + repr(geo))
        ob.geo_location = geo
        portal.catalogNyObject(ob)

def fetch_and_remove(ob, prop_name):
    found = False
    prop_value = None

    if prop_name in ob.__dict__:
        found = True
        prop_value = ob.__dict__[prop_name]
        del ob.__dict__[prop_name]

    if isinstance(prop_value, LocalAttribute):
        # for some reason, prop_value may be a LocalAttribute instance;
        # let's find the real value in _local_properties
        local_props = ob.__dict__['_local_properties']
        if prop_name in local_props:
            for value, timestamp in local_props[prop_name].values():
                if value:
                    prop_value = value
            del local_props[prop_name]
            ob._p_changed = 1

    if isinstance(prop_value, LocalAttribute):
        # if prop_value is still a LocalAttribute, we found nothing in
        # _local_properties; let's assign it a blank value and move on.
        prop_value = ''

    return found, prop_value

def add_indexes(catalog, log):
    add_field_index(catalog, 'geo_latitude', log)
    add_field_index(catalog, 'geo_longitude', log)

    indexes = catalog.indexes()
    if 'geo_address' not in indexes:
        if txng_version == 2:
            try: catalog.addIndex('geo_address', 'TextIndexNG3', extra={'default_encoding': 'utf-8'})
            except: pass
        else:
            try: catalog.addIndex('geo_address', 'TextIndex')
            except: pass
    else:
        log.debug('skipping index (already in catalog) geo_address')

def add_field_index(catalog, id, log):
    indexes = catalog.indexes()
    if id not in indexes:
        log.debug('adding index' + id)
        catalog.addIndex(id, 'FieldIndex')
    else:
        log.debug('skipping index (already in catalog) ' + id)

def enable_geotagged_content(portal, log):
    portal_control = portal.portal_control
    portal_map = portal.portal_map
    geotaggable_objects = [x['id'] for x in portal_map.list_geotaggable_types() if x['enabled']]
    portal_control_enabled = portal_control.settings.keys()
    if portal_control_enabled:
        for content_type in portal_control_enabled:
            class_name = portal.get_pluggable_item(content_type)['_class'].__name__
            if class_name not in geotaggable_objects:
                geotaggable_objects.append(class_name)
        portal_control.saveSettings(enabled_for=[]) #clear portal_control
        portal_map.admin_set_contenttypes(geotag=geotaggable_objects)
        log.debug('Setting geocodable content' + geotaggable_objects)
    else:
        log.debug('No geocodable content defined in portal control')
