# -*- coding=utf-8 -*-

from AccessControl import ClassSecurityInfo
from Products.naayaUpdater.updates import UpdateScript, PRIORITY
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class ModifyLocalProperties(UpdateScript):
    title = 'Update object properties and localized properties'
    creation_date = 'Feb 21, 2012'
    authors = [u'Bogdan Tănase']
    priority = PRIORITY['LOW']
    description = ("Delete object property/Copy value to object's localized "
                  "properties")
    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        form = self.REQUEST.form
        prop_name = form.get('property', None)

        if prop_name:
            save_to_local = form.get('save_to_local', None)
            languages = portal.gl_get_languages()

            for ob in portal.getCatalogedObjectsA():
                if ob.__dict__.has_key(prop_name):
                    local_values = {}
                    for lang in languages:
                        local_values[lang] = ob.getLocalProperty(prop_name, lang)

                    property_in_local = reduce(lambda x, y:x or y,
                                               local_values.values())

                    if(save_to_local and not property_in_local):
                        value = ob.__dict__[prop_name] or ''
                        for lang in languages:
                            ob.set_localpropvalue(prop_name, lang, value)
                            self.log.debug('Saving "%s" value for "%s" local '
                                           'property (%s)' %
                                           (value, prop_name, lang))

                    delattr(ob, prop_name)
                    self.log.debug('Deleted property "%s" for %s' %
                                    (prop_name, ob.absolute_url()))

                    ob.recatalogNyObject(ob)
                    self.log.debug('Reindexed object %s' %
                            (ob.absolute_url()))

            return True
        else:
            self.log.debug('No property selected!')
            return False

    update_template = PageTemplateFile('zpt/update_modify_local_properties',
                                       globals())
    update_template.default = UpdateScript.update_template
