from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
import lxml.html

class UpdateConvertInternalScripts(UpdateScript):
    title = ("Convert internal links to new site location")
    description = ("Convert internal links to new site location")
    authors = ['Tiberiu Ichim']
    creation_date = 'Jul 09, 2014'

    def _update(self, portal):
        catalog = portal.portal_catalog
        all_objects = catalog.searchResults(something=True)
        schemas = {}
        portal_name = portal.id

        self.log.info('Start migration of internal links')

        for brain in all_objects:

            if not brain.meta_type in schemas:
                helper = get_schema_helper_for_metatype(portal, brain.meta_type)
                schemas[brain.meta_type] = helper.schema
            schema = schemas[brain.meta_type]
            if not schema:
                self.log.debug("No schema for %s", brain.meta_type)
                continue

            for field in schema.objectValues():
                if field.meta_type == "Naaya Schema Text Area Widget":
                    field_id = field.prop_name()
                    obj = brain.getObject()
                    self.log.debug("Checking field %s for %s", field_id, obj.absolute_url())
                    prop = getattr(obj, field_id, None)

                    if prop:
                        changed = False
                        etree = lxml.html.fromstring(prop)

                        for selector, attr in [('//a', 'href'), ('//img', 'src')]:
                            elements = etree.xpath(selector)
                            for el in elements:
                                old_value = el.get(attr)
                                if not old_value:
                                    continue
                                split = filter(None, old_value.split('/'))
                                if split[0] in ['http:', 'https:', 'mailto:']:
                                    continue
                                if not portal_name == split[0]:
                                    new_value = "/".join(['', portal_name] + split)
                                    el.set(attr, new_value)
                                    changed = True
                                    self.log.debug("Fixing %s, %s => %s", selector, old_value, el.get(attr))

                        if changed:
                            setattr(obj, field_id, lxml.html.tostring(etree))
                            self.log.info("Migrated links for %s", obj.absolute_url())

            obj = brain.getObject()

        self.log.info('Finished migration of internal links')
        return True
