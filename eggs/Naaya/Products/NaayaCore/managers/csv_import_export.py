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
# David Batranu, Eau de Web

""" Bulk upload contacts, urls, experts """

#Python import
import csv, codecs, cStringIO
from StringIO import StringIO
import urllib
import simplejson as json

#Zope imports
import transaction
from Acquisition import Implicit
from OFS.SimpleItem import Item
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, Unauthorized
from DateTime import DateTime
from zope.event import notify
from Products.NaayaCore.events import CSVImportEvent

#Product imports
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.NaayaCore.SchemaTool.widgets.GeoWidget import GeoWidget
from Products.NaayaCore.GeoMapTool.managers import geocoding
from Products.NaayaCore.interfaces import ICSVImportExtraColumns

class CSVImportTool(Implicit, Item):
    title = "CSV import"

    security = ClassSecurityInfo()
    geo_fields = {}

    def __init__(self, id):
        self.id = id

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'template')
    def template(self, meta_type, as_attachment=False, REQUEST=None):
        """ """
        if REQUEST and not self.getParentNode().checkPermissionPublishObjects():
            raise Unauthorized

        schema = self.getSite().getSchemaTool().getSchemaForMetatype(meta_type)
        if schema is None:
            raise ValueError('Schema for meta-type "%s" not found' % meta_type)
        output = StringIO()
        columns = []
        for widget in schema.listWidgets():
            if widget.multiple_form_values:
                for subname in widget.multiple_form_values:
                    columns.append(widget.title + ' - ' + subname)
            else:
                columns.append(widget.title)
        csv.writer(output).writerow(columns)
        if as_attachment and REQUEST is not None:
            filename = schema.title_or_id() + ' bulk upload.csv'
            set_response_attachment(REQUEST.RESPONSE, filename,
                'text/csv; charset=utf-8', output.len)
        return output.getvalue()

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'do_geocoding')
    def do_geocoding(self, properties):
        lat = properties.get(self.geo_fields['lat'], '')
        lon = properties.get(self.geo_fields['lon'], '')
        address = properties.get(self.geo_fields['address'], '')
        if lat.strip() == '' and lon.strip() == '' and address:
            if self.portal_map.map_engine == 'yahoo':
                coordinates = geocoding.yahoo_geocode(address)
            elif self.portal_map.map_engine == 'google':
                coordinates = geocoding.location_geocode(address)
            if coordinates != None:
                lat, lon = coordinates
                properties[self.geo_fields['lat']] = lat
                properties[self.geo_fields['lon']] = lon
        return properties


    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'do_import')
    def do_import(self, meta_type, data, REQUEST=None):
        """ """
        if REQUEST and not self.getParentNode().checkPermissionPublishObjects():
            raise Unauthorized

        errors = []

        schema = self.getSite().getSchemaTool().getSchemaForMetatype(meta_type)
        if schema is None:
            raise ValueError('Schema for meta-type not found: "%s"' % meta_type)

        content_type = self.getSite().get_pluggable_item(meta_type)
        add_object = content_type['add_method']

        location_obj = self.getParentNode()

        # build a list of property names based on the object schema
        # TODO: extract this loop into a separate function
        prop_map = {}
        for widget in schema.listWidgets():
            prop_name = widget.prop_name()

            if widget.multiple_form_values:
                for subname in widget.multiple_form_values:
                    prop_subname = prop_name + '.' + subname
                    prop_map[widget.title + ' - ' + subname] = {
                        'column': prop_subname, 'widget': widget}
                if isinstance(widget, GeoWidget):
                    for subname in widget.multiple_form_values:
                        self.geo_fields[subname] = prop_name + '.' + subname
            else:
                prop_map[widget.title] = {'column': prop_name, 'widget': widget}

        try:
            reader = UnicodeReader(data)
            try:
                header = reader.next()
            except StopIteration:
                if REQUEST is None:
                    raise ValueError('Invalid CSV file')
                else:
                    errors.append('Invalid CSV file')
                    reader = []

            record_number = 0
            obj_ids = []

            for row in reader:
                try:
                    record_number += 1
                    # TODO: extract this block into a separate function
                    properties = {}
                    extra_properties = {}
                    for column, value in zip(header, row):
                        if value == '':
                            continue
                        if column not in prop_map:
                            extra_properties[column] = value
                            continue
                        key = prop_map[column]['column']
                        widget = prop_map[column]['widget']
                        properties[key] = widget.convert_from_user_string(value)
                    properties = self.do_geocoding(properties)
                    ob_id = add_object(location_obj, _send_notifications=False, **properties)
                    ob = location_obj._getOb(ob_id)
                    if extra_properties:
                        adapter = ICSVImportExtraColumns(ob, None)
                        if adapter is not None:
                            adapter.handle_columns(extra_properties)
                    obj_ids.append(ob.getId())
                    ob.submitThis()
                    ob.approveThis()
                except UnicodeDecodeError, e:
                    raise
                except Exception, e:
                    self.log_current_error()
                    msg = 'Error while importing from CSV, row %d: %s' % (record_number, str(e))
                    if REQUEST is None:
                        raise ValueError(msg)
                    else:
                        errors.append(msg)

        except UnicodeDecodeError, e:
            if REQUEST is None:
                raise
            else:
                errors = ['CSV file is not utf-8 encoded']

        if not errors:
            notify(CSVImportEvent(location_obj, obj_ids))

        if REQUEST is not None:
            if errors:
                transaction.abort()
                self.setSessionErrors(errors)
            else:
                self.setSessionInfo(['%s object(s) of type "%s" successfully imported.'
                    % (record_number, schema.title_or_id())])
            return self.index_html(REQUEST, meta_type=meta_type)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'index_html')
    index_html = PageTemplateFile('../zpt/bulk_import', globals())

InitializeClass(CSVImportTool)


class CSVExportTool(Implicit, Item):
    title = "CSV export"

    security = ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'export')
    def export(self, meta_type, as_attachment=False, REQUEST=None):
        """ """
        if REQUEST and not self.getParentNode().checkPermissionPublishObjects():
            raise Unauthorized

        schema = self.getSite().getSchemaTool().getSchemaForMetatype(meta_type)
        if schema is None:
            raise ValueError('Schema for meta-type "%s" not found' % meta_type)

        widgets = schema.listWidgets()
        prop_names = [widget.prop_name() for widget in widgets]

        output = StringIO()
        csv_writer = csv.writer(output)
        csv_writer.writerow([widget.title for widget in widgets])

        for ob in self.getSite().getCatalogedObjects(meta_type=[meta_type]):
            csv_writer.writerow([
                unicode(getattr(ob, prop_name)).encode('utf-8')
                for prop_name in prop_names
            ])

        if as_attachment and REQUEST is not None:
            set_response_attachment(REQUEST.RESPONSE, filename,
                'text/csv; charset=utf-8', output.len)
        return output.getvalue()

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'export_json')
    def export_json(self, meta_type=None, pretty=False,
            as_attachment=False, REQUEST=None):
        """
        export all objects of `meta_type` (or, if None, all content) as JSON
        """

        if as_attachment and REQUEST is not None:
            set_response_attachment(REQUEST.RESPONSE,
                '%s.json' % self.getSite().getId(), 'application/json')
        data = {}
        for ob in self.getSite().getCatalogedObjects():
            if not isinstance(ob, NyContentData):
                continue
            ob_data = dict(ob.dump_data(), meta_type=ob.meta_type)
            data[relative_path_to_site(ob)] = ob_data

        if pretty:
            kwargs = {'indent': 4}
        else:
            kwargs = {'sort_keys': False}

        return json.dumps(data, default=json_encode, **kwargs)

InitializeClass(CSVExportTool)

def json_encode(ob):
    """ try to encode some known value types to JSON """
    if isinstance(ob, DateTime):
        return str(ob)
    raise ValueError

def set_response_attachment(RESPONSE, filename, content_type, length=None):
    RESPONSE.setHeader('Content-Type', 'text/csv; charset=utf-8')
    if length is not None:
        RESPONSE.setHeader('Content-Length', length)
    RESPONSE.setHeader('Pragma', 'public')
    RESPONSE.setHeader('Cache-Control', 'max-age=0')
    RESPONSE.setHeader('Content-Disposition', "inline; filename*=UTF-8''%s"
        % urllib.quote(filename))

def relative_path_to_site(ob):
    site = ob.getSite()
    site_path = '/'.join(site.getPhysicalPath())
    ob_path = '/'.join(ob.getPhysicalPath())
    return ob_path[len(site_path):]

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self
