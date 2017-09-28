from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.naayaUpdater.updates import UpdateScript

class UpdateSchemaWidgets(UpdateScript):
    title='Update schema widgets'
    authors = ['Alexandru Plugaru']
    creation_date = 'Aug 31, 2010'
    description = "Migrate the data from one type of widget to the other, \
 currently works for localized objects only."
    index_html = PageTemplateFile('zpt/update_schema_widgets', globals())

    def _update(self, portal):
        schema_tool = portal.getSchemaTool()
        schemas = {}
        for field, value in self.REQUEST.form.items():
            try:
                meta_type, widget_id = field.split('|')
            except ValueError:
                continue
            try:
                schema = schema_tool._getOb(meta_type)
            except KeyError:
                continue
            try:
                widget = schema._getOb(widget_id)
            except KeyError:
                continue

            if schemas.has_key(schema.id):
                schemas[schema.id].append(widget)
            else:
                schemas[schema.id] = [widget]

        for schema_id, widgets in schemas.items():
            update_method = self.REQUEST.form.get('method', None)
            if update_method is not None: #Run specific update method
                getattr(self, update_method)(portal,
                                        schema_tool._getOb(schema_id), widgets)
            else:
                self.log.error('No action has been selected!')
                return False
        return True


    def unlocalize(self, portal, schema, widgets):
        """ Move the data from _local_properties to simple attribute on object
        After all the objects in question are modified
        """
        if len(portal.get_languages()) > 1:
            raise ValueError(
                'There are multiple languages present on this portal')

        catalog_tool = portal.getCatalogTool()
        meta_type = _get_meta_type(portal, schema)
        lang = portal.get_selected_language()

        for widget in widgets:
            widget.localized = False
            self.log.info('%s[%r] is now unlocalized', schema.id, widget.id)
        objects = [brain.getObject() for brain in
                   catalog_tool(meta_type=meta_type)]
        for ob in objects:
            if hasattr(ob, widget.prop_name()): #Already updated?
                 self.log.info('Skipped %r', ob.absolute_url(1))
                 continue
            for widget in widgets:
                try:
                    value = ob._local_properties[widget.prop_name()][lang][0]
                    del ob._local_properties[widget.prop_name()]
                except KeyError:
                    continue
                if widget.data_type == 'bool':
                    value = bool(value)
                elif isinstance(value, str):
                    value = unicode(value, 'utf-8')
                setattr(ob, widget.prop_name(), value)
            ob.recatalogNyObject(ob)
            self.log.info('Updated %r', ob.absolute_url(1))

    def localize(self, portal, schema, widgets):
        """ Move the data from _local_properties to simple attribute on object
        After all the objects in question are modified
        """

        catalog_tool = portal.getCatalogTool()
        meta_type = _get_meta_type(portal, schema)
        lang = portal.get_selected_language()

        for widget in widgets:
            widget.localized = True
            self.log.info('%s[%r] is now localized', schema.id, widget.id)

        objects = [brain.getObject() for brain in
                   catalog_tool(meta_type=meta_type)]
        for ob in objects:
            for widget in widgets:
                ob.set_localproperty(widget.prop_name(),
                                     getattr(ob, widget.prop_name()), lang)
                delattr(ob, widget.prop_name())
            ob.recatalogNyObject(ob)
            self.log.info('Updated %r', ob.absolute_url(1))

def _get_meta_type(portal, schema):
    for meta_type, _schema in portal.getSchemaTool().listSchemas().items():
        if schema == _schema:
            return meta_type
    else:
        raise ValueError("No meta_type for %r" % schema)

