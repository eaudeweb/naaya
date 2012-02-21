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
        property = form.get('property', None)

        if property:
            save_to_local = form.get('save_to_local', None)
            languages = portal.gl_get_languages()

            for ob in portal.getCatalogedObjectsA():
                if ob.__dict__.has_key(property):
                    local_values = {}
                    for lang in languages:
                        local_values[lang] = ob.getLocalProperty(property, lang)

                    property_in_local = reduce(lambda x, y:x or y,
                                               local_values.values())

                    if(save_to_local and not property_in_local):
                        value = ob.__dict__[property] or ''
                        for lang in languages:
                            ob.set_localpropvalue(property, lang, value)
                            self.log.debug('Saving "%s" value for "%s" local '
                                           'property (%s)' %
                                           (value, property, lang))

                    delattr(ob, property)
                    self.log.debug('Deleted property "%s" for %s' %
                                    (property, ob.absolute_url()))

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
