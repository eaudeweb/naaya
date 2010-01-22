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

# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens
from OFS.Folder import Folder
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaCore.constants import *
from Products.NaayaCore.SchemaTool.Schema import Schema
from Products.NaayaCore.GeoMapTool.GeoMapTool import GeoMapTool
from contentratings.interfaces import IUserRating
from naaya.content.base.interfaces import INyContentObject

_other_schema_products = {}
def register_schema_product(name, label, meta_type, default_schema):
    _other_schema_products[meta_type] = {
        'id':name,
        'title':label,
        'defaults':default_schema,
    }

def manage_addSchemaTool(self, REQUEST=None):
    """Add SchemaTool """

    ob = SchemaTool(ID_SCHEMATOOL, TITLE_SCHEMATOOL)
    self._setObject(ID_SCHEMATOOL, ob)
    ob = self._getOb(ID_SCHEMATOOL)

    ob.loadDefaultSchemas()

    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class SchemaTool(Folder):
    """ Container for Schema objects """

    meta_type = METATYPE_SCHEMATOOL
    _icon = '_misc/NaayaCore/SchemaTool.gif'

    security = ClassSecurityInfo()

    meta_types = (
        {
            'name': METATYPE_SCHEMA,
            'action': 'manage_addSchema_html',
            'permission': PERMISSION_ADD_NAAYACORE_TOOL,
        },
    )
    all_meta_types = meta_types

    def __init__(self, id, title):
        super(SchemaTool, self).__init__(id=id)
        self.title = title

    security.declareProtected(view_management_screens, 'manage_addSchema_html')
    manage_addSchema_html = PageTemplateFile('zpt/schema_add', globals())

    security.declareProtected(view_management_screens, 'manage_addSchema')
    def manage_addSchema(self, id, title, REQUEST):
        """ form subbit handler to add new schema """
        self.addSchema(id, title)
        return self.manage_main(self, REQUEST, update_menu=1)

    security.declarePrivate('addSchema')
    def addSchema(self, id, title='', defaults=None):
        """ add a new property schema """
        ob = Schema(id, title)
        self._setObject(id, ob)
        ob = self._getOb(id)
        if defaults is not None:
            ob.populateSchema(defaults)

    def _list_default_schemas(self):
        schemas = {}
        for meta_type, content in _other_schema_products.iteritems():
            schemas[meta_type] = content

        for meta_type, content_type in self.get_pluggable_content().iteritems():
            if content_type['default_schema'] is None:
                # this content type has not been ported to Schema
                continue
            schemas[meta_type] = {
                'id': content_type['schema_name'],
                'title':content_type['label'],
                'defaults': content_type['default_schema'],
            }

        from Products.Naaya import NyFolder
        schemas['Naaya Folder'] = {
            'id': 'NyFolder',
            'title': 'Folder',
            'defaults': NyFolder.DEFAULT_SCHEMA,
        }

        return schemas

    security.declarePrivate('loadDefaultSchemas')
    def loadDefaultSchemas(self):
        """ Populate self with initial schema definitions """
        if self.objectIds():
            raise ValueError('SchemaTool has already been populated with schemas')

        for content in self._list_default_schemas().values():
            self.addSchema(**content)

    def getSchemaForMetatype(self, meta_type):
        """ Get the property schema corresponding to the given metatype """
        default_schemas = self._list_default_schemas()
        schema_id = default_schemas.get(meta_type, {}).get('id', None)

        if schema_id is None:
            return None

        if schema_id not in self.objectIds():
            self.addSchema(**default_schemas[meta_type])

        return self._getOb(schema_id)

    def listSchemas(self, installed=None):
        """ Get a list of all schemas, indexed my meta_type """
        output = {}
        for content_type in self.getSite().get_pluggable_content().values():
            name = content_type['schema_name']
            meta_type = content_type['meta_type']
            if installed is True:
                if not self.getSite().is_pluggable_item_installed(meta_type):
                    continue
            if name in self.objectIds():
                output[meta_type] = self._getOb(name)
        return output

    def index_html(self, REQUEST):
        """ redirect to admin_html """
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/admin_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_html')
    admin_html = PageTemplateFile('zpt/admin_contenttypes', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'contenttypes_properties_html')
    contenttypes_properties_html = PageTemplateFile('zpt/contenttypes_properties', globals())

    admin_pt = PageTemplateFile('zpt/admin_template', globals())

    admin_tabs = [
        {'url': 'admin_html', 'title': 'Manage content types'},
        {'url': 'contenttypes_properties_html', 'title': 'Content types properties'}
    ]

    def list_geotaggable_types(self):
        return [item for item in self.list_content_types() if item.has_key('geo_taggable')]

    def list_content_types(self):
        portal_schemas = self.getSite().portal_schemas
        output = []
        for schema in portal_schemas.listSchemas(installed=True).values():
            temp_output = {'id': schema.id, 'title': schema.title_or_id()}
            try:
                geo_location = schema.getWidget('geo_location');
                geo_type = schema.getWidget('geo_type');
                temp_output['geo_taggable'] = True
                temp_output['geo_enabled'] = geo_location.visible and geo_type.visible
            except KeyError:
                # one or both widgets are missing; skip it
                temp_output.append = {'geo_taggable': False}
            if schema.is_ratable:
                temp_output['ratable'] = True
            else:
                temp_output['ratable'] = False
            output.append(temp_output)
        return output

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_set_contenttypes')
    def admin_set_contenttypes(self, geotag=[], ratable=[], REQUEST=None):
        """ Configure which content types are geotaggable """

        for schema in self.getSite().portal_schemas.objectValues():
            new_visible = (schema.id in geotag)

            try:
                geo_location = schema.getWidget('geo_location')
            except:
                pass
            else:
                geo_location.visible = new_visible

            try:
                geo_type = schema.getWidget('geo_type')
            except:
                pass
            else:
                geo_type.visible = new_visible

            if schema.id in ratable:
                schema.is_ratable = True
            else:
                schema.is_ratable = False

        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/contenttypes_properties_html')

    def get_ratings(self):
        """ """
        objects = self.getSite().getCatalogedObjects()
        ratings = []
        for ob in filter(INyContentObject.providedBy, objects):
            if ob.is_ratable() and IUserRating(ob).averageRating > 0:
                rating = IUserRating(ob)
                ratings.append((ob, rating.averageRating, rating.numberOfRatings))
        return ratings

    def sort_objects_by_ratings(self, skey=1, rkey=1, max_range=10):
        """ """
        import operator
        objects = self.get_ratings()
        objects = sorted(objects, key=operator.itemgetter(skey), reverse=rkey)
        max_range = min(max_range, len(objects))
        results = objects[0:max_range]
        return results

    _ratings_overview = PageTemplateFile('zpt/ratings_overview', globals())
    def ratings_overview_html(self, REQUEST):
        """ """
        skey = 1
        rkey = 1
        if REQUEST.has_key('show_lowest_rated'):
            rkey = 0
        elif REQUEST.has_key('show_most_rated'):
            skey=2
        max_range = int(REQUEST.get('number_of_objects', 10))
        if skey == 1 and rkey == 1:
                REQUEST.set('show_highest_rated', True)
        objects = self.sort_objects_by_ratings(skey, rkey, max_range)
        return self._ratings_overview(REQUEST, objects=objects)

InitializeClass(SchemaTool)
