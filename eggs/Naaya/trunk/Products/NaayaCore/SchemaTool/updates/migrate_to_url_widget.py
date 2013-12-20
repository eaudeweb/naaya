from Products.naayaUpdater.updates import UpdateScript

from Products.NaayaCore.SchemaTool.widgets.URLWidget import convert_string_to_URL

class MigrateToURLWidget(UpdateScript):
    title = "Migrate String Widgets to URL Widgets (based on default schema)"
    authors = ["Andrei Laza"]
    creation_date = 'Nov 18, 2011'

    def _update(self, portal):
        portal_catalog = portal.getCatalogTool()
        portal_schemas = portal.portal_schemas
        meta_types = (set(portal_schemas._list_default_schemas().keys())
                         &
                         set(portal_schemas.listSchemas().keys()))
        default_schemas = portal_schemas._list_default_schemas()
        current_schemas = portal_schemas.listSchemas()

        for meta_type in meta_types:
            default_schema = default_schemas[meta_type]['defaults']
            current_schema = current_schemas[meta_type]

            default_prop_names = set(default_schema.keys())
            current_prop_names = set([name[:-len('-property')]
                                      for name in current_schema.objectIds()
                                      ])
            other_prop_names = ((default_prop_names - current_prop_names)
                                |
                                (current_prop_names - default_prop_names))
            if other_prop_names:
                self.log.warn('%s did not match properties: %r',
                              meta_type, list(other_prop_names))

            prop_names = (default_prop_names & current_prop_names)
            for prop_name in prop_names:
                default_prop = default_schema[prop_name]
                current_prop = current_schema[prop_name + '-property']

                default_type = default_prop['widget_type']
                current_type = current_prop.__class__.__name__[:-len('Widget')]
                if default_type != 'URL':
                    continue

                self.log.debug('migrating %s objects property %s',
                               meta_type, prop_name)
                for brain in portal_catalog(meta_type=meta_type):
                    ob = brain.getObject()
                    if not hasattr(ob.aq_base, prop_name):
                        continue
                    old_value = getattr(ob, prop_name)
                    new_value = convert_string_to_URL(old_value)
                    if new_value != old_value:
                        self.log.debug('changing %s %s from %s to %s',
                                        ob.absolute_url(), prop_name,
                                        old_value, new_value)
                        setattr(ob, prop_name, new_value)
                    #else:
                    #    self.log.debug('not changing %s %s value %s',
                    #                    ob.absolute_url(), prop_name,
                    #                    old_value)


                if current_type == 'URL':
                    continue

                self.log.debug('%s property %s migrating from %s to %s',
                               meta_type, prop_name,
                               current_type, default_type)

                # replace widget
                current_schema.manage_delObjects([prop_name + '-property'])
                current_schema.addWidget(prop_name,
                                         widget_type='URL')
                new_prop = current_schema[prop_name + '-property']

                # copy object attributes from the old widget
                for attr, value in current_prop.__dict__.items():
                    if attr.startswith('_'):
                        continue
                    setattr(new_prop, attr, value)

        return True
