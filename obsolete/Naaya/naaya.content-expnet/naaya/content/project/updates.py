from Products.naayaUpdater.updates import UpdateScript

from Products.CHM2.CHMSite import add_terms_property_to_schema

class ChmTermsSeparator(UpdateScript):
    title = 'chm_terms separator change & title change'
    authors = ('Andrei Laza',)
    creation_date = 'Aug 22, 2011'
    description = 'migrate chm_terms separator from "," to "|"'

    chm_term_titles = {
            'NyProject': 'Main topics covered',
            'NyOrganisation': 'Main topics covered',
            'NyExpert': 'Main areas of expertise',
            }

    def is_chm_term(self, glossary, term, lang):
        lang_name = glossary.gl_get_language_name(lang)

        for gfolder in glossary.objectValues('Naaya Glossary Folder'):
            if gfolder.get_translation_by_language(lang_name) == term:
                return True
            for gelement in gfolder.objectValues('Naaya Glossary Element'):
                if gelement.get_translation_by_language(lang_name) == term:
                    return True
        return False

    def match_glossary_terms(self, glossary, value, lang):
        if not value:
            self.log.debug('empty value "%r"', value)
            return []

        migrations = {
                'Impact assesment':
                    'Impact assessment',
                'Trophic integrity of terrestrrial and freshwater ecosystems':
                    'Trophic integrity of terrestrial and freshwater ecosystems',
                'Island biodiversity':
                    'Island Biodiversity',
                    }

        ret = []
        l = value.split(',')
        self.log.debug('items found: %r', l)
        while l:
            for i in range(1, len(l) + 1):
                term = (','.join(l[:i])).strip()
                if term in migrations:
                    term = migrations[term]
                if self.is_chm_term(glossary, term, lang):
                    self.log.debug('matched "%s"', term)
                    ret.append(term)
                    l = l[i:]
                    break

                term = (', '.join(l[:i])).strip()
                if term in migrations:
                    term = migrations[term]
                if self.is_chm_term(glossary, term, lang):
                    self.log.debug('matched "%s"', term)
                    ret.append(term)
                    l = l[i:]
                    break
            else:
                self.log.warn('consuming "%s"', l[0])
                l = l[1:]
        return ret

    def update_type(self, portal, naaya_name, meta_type):
        self.log.debug('Start updating meta type %s', meta_type)
        schema_tool = portal.getSchemaTool()

        schema_ob = schema_tool._getOb(naaya_name, default=None)
        if schema_ob is None: # no schema
            self.log.debug('%s not in schema - skip it', naaya_name)
            return True
        self.log.debug('%s has schema', naaya_name)

        chm_terms_prop = schema_ob._getOb('chm_terms-property', default=None)
        if chm_terms_prop is None:
            self.log.debug('No chm_terms property for %s'
                           ' (probably not installed)' % naaya_name)
            return True

        if (naaya_name not in self.chm_term_titles
                or chm_terms_prop.title == self.chm_term_titles[naaya_name]):
            self.log.debug('No need to update title for %s', naaya_name)
        else:
            chm_terms_prop.title = self.chm_term_titles[naaya_name]
            self.log.debug('Changed title for %s to "%s"', naaya_name,
                                        self.chm_term_titles[naaya_name])

        if chm_terms_prop.separator == '|':
            self.log.debug('No need to update separator for %s', meta_type)
            return True
        if chm_terms_prop.separator != ',':
            self.log.error('Expected "," for %s and found %r', meta_type,
                    chm_terms_prop.separator)
        assert chm_terms_prop.separator == ','

        # update objects
        lang_map = portal.gl_get_languages_map()
        glossary = portal.chm_terms
        portal_catalog = portal.getCatalogTool()
        for brain in portal_catalog(meta_type=meta_type):
            ob = brain.getObject()
            self.log.debug('Updating %s at %s', meta_type, ob.absolute_url())
            for lang in lang_map:
                value = ob.getLocalProperty('chm_terms', lang['id'])
                value_list = self.match_glossary_terms(glossary, value, lang['id'])

                value = '|'.join(value_list)
                ob._setLocalPropValue('chm_terms', lang['id'], value)

        chm_terms_prop.separator = '|'
        return True

    def _update(self, portal):
        schema_tool = portal.getSchemaTool()
        schemas = schema_tool.listSchemas()

        ret = True
        for meta_type in schemas:
            schema_ob = schemas[meta_type]
            naaya_name = schema_ob.id
            if not self.update_type(portal, naaya_name, meta_type):
                ret = False
        return ret


class MainTopicsToChmTerms(UpdateScript):
    title = 'Dutch CHM portal - pick lists and chm_terms glossary'
    authors = ('Stanciu Gabriel', 'Andrei Laza')
    description = ('#618 The Dutch CHM portal has the new CHM terms glossary, '
                    'and also a pick-list with the same content, used for the '
                    '"main topics covered" property of "Project" objects. '
                    'Remove the second property from the schema, and its '
                    'pick list, and merge the values into the new '
                    'chm_terms property. ')
    creation_date = 'Aug 17, 2011'

    def glossary_match(self, glossary_item, item):
        if item.lower() == glossary_item.English.lower():
            return True
        if item.replace('biological diversity', 'biodiversity') == glossary_item.English:
            return True
        if item.replace('tourism', ' tourism') == glossary_item.English:
            return True
        if item.replace('terrestrrial', 'terrestrial') == glossary_item.English:
            return True
        return False

    def glossary_translation(self, glossary, title, lang_name):
        for gfolder in glossary.objectValues('Naaya Glossary Folder'):
            if self.glossary_match(gfolder, title):
                return gfolder.get_translation_by_language(lang_name)

            for gelement in gfolder.objectValues('Naaya Glossary Element'):
                if self.glossary_match(gelement, title):
                    return gelement.get_translation_by_language(lang_name)

    def glossary_has_item(self, glossary, item):
        for gfolder in glossary.objectValues('Naaya Glossary Folder'):
            if self.glossary_match(gfolder, item):
                return True

            for gelement in gfolder.objectValues('Naaya Glossary Element'):
                if self.glossary_match(gelement, item):
                    return True
        return False

    def values_not_in_glossary(self, glossary, tree):
        ret = []
        title = tree['ob'].title
        if (title != 'Topics for experts network' # root not added
            and not self.glossary_has_item(glossary, title)):
            ret.append(title)

        for subtree in tree['children']:
            ret.extend(self.values_not_in_glossary(glossary, subtree))

        return ret

    def update_objects(self, portal, topics, meta_type):
        lang_map = portal.gl_get_languages_map()
        glossary = portal.chm_terms
        portal_catalog = portal.getCatalogTool()
        for brain in portal_catalog(meta_type=meta_type):
            ob = brain.getObject()
            titles = [topics._getOb(i).title for i in ob.main_topics]
            self.log.debug('Updating %s at %s with main_topics %r', meta_type, ob.absolute_url(), titles)
            for lang in lang_map:
                value = ','.join(self.glossary_translation(glossary, t, lang['title']) for t in titles)
                ob._setLocalPropValue('chm_terms', lang['id'], value)
            if getattr(ob.aq_base, 'main_topics', None) is not None:
                del ob.main_topics

    def log_objects(self, portal, meta_type):
        portal_catalog = portal.getCatalogTool()
        for brain in portal_catalog(meta_type=meta_type):
            ob = brain.getObject()
            self.log.debug('Found %s at %s with main_topics %r', meta_type, ob.absolute_url(), ob.main_topics)

    def has_objects(self, portal, meta_type):
        portal_catalog = portal.getCatalogTool()
        return len(portal_catalog(meta_type=meta_type))

    def make_chm_terms_property_visible(self, schema_ob, naaya_name):
        chm_terms = schema_ob._getOb('chm_terms-property', default=None)
        if chm_terms is None:
            add_terms_property_to_schema(schema_ob)
            self.log.debug('Added chm_terms property for %s', naaya_name)
            chm_terms = schema_ob._getOb('chm_terms-property')

        # make chm_terms properties visible
        if not chm_terms.visible:
            chm_terms.visible = True
            self.log.debug('Made the CHM terms property visible for %s', naaya_name)

    def update_type(self, portal, naaya_name, meta_type):
        schema_tool = portal.getSchemaTool()

        schema_ob = schema_tool._getOb(naaya_name, default=None)
        if schema_ob is None: # no schema
            self.log.debug('%s not in schema - skip it', naaya_name)
            return True
        self.log.debug('%s has schema', naaya_name)

        has_objects = self.has_objects(portal, meta_type)
        if has_objects:
            self.log.info('portal has %s objects', meta_type)
        else:
            self.log.info("portal doesn't have %s objects", meta_type)

        self.make_chm_terms_property_visible(schema_ob, naaya_name)

        main_topics = schema_ob._getOb('main_topics-property', default=None)
        if main_topics is None:
            self.log.debug('No main_topics property for %s - skip it', naaya_name)
            return True

        portlets_tool = portal.getPortletsTool()
        topics_list_id = main_topics.list_id

        topics = portlets_tool._getOb(topics_list_id, default=None)

        if topics is not None:
            tree = topics.get_nodes_as_tree()
            glossary = portal.chm_terms
            ntl = self.values_not_in_glossary(glossary, tree)
            if ntl != []:
                self.log.warn("%s items that didn't match: %r", topics_list_id, ntl)
                # can't update objects - WARN - objects will have no value after update
                self.log.warn("Can't update %s objects - they will have no values after update", meta_type)
                # list objects (for dry run)
                self.log_objects(portal, meta_type)
            else:
                if has_objects: # topics and objects
                    self.update_objects(portal, topics, meta_type)
                else: # topics, but no objects
                    pass
            self.topics_lists_to_remove.add(topics_list_id)
        else: # no topics
            if has_objects: # no topics, but have objects
                # can't update objects - WARN - objects will have no value after update
                self.log.warn("Can't update %s objects - they will have no values after update", meta_type)
                # list objects (for dry run)
                self.log_objects(portal, meta_type)
            else: # no topics no objects
                pass

        # remove main_topics property
        schema_ob.manage_delObjects(['main_topics-property'])
        self.log.debug('Deleted main_topics property for %s', naaya_name)
        return True

    def _update(self, portal):
        self.topics_lists_to_remove = set()

        ret = True
        if not self.update_type(portal, 'NyProject', 'Naaya Project'):
            ret = False
        if not self.update_type(portal, 'NyOrganisation', 'Naaya Organisation'):
            ret = False
        if not self.update_type(portal, 'NyExpert', 'Naaya Expert'):
            ret = False

        portlets_tool = portal.getPortletsTool()
        for topics_list_id in self.topics_lists_to_remove:
            portlets_tool.manage_delObjects([topics_list_id])
            self.log.debug('Deleted %s', topics_list_id)

        portal_catalog = portal.getCatalogTool()
        if 'topics' in portal_catalog.indexes():
            portal_catalog.delIndex('topics')
            self.log.info('Removed old catalog index "topics"')

        try:
            portal_catalog.addIndex('topics', 'KeywordIndex',
                           extra={'indexed_attrs' : 'topics'})
            self.log.info('Added catalog index "topics"')
        except:
            self.log.error('Failed to create topics index. Naaya Expert content '
                            'type may not work properly')

        portal_catalog.manage_reindexIndex(['topics'])
        return ret
