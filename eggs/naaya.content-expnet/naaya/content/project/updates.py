from Products.naayaUpdater.updates import UpdateScript

class MainTopicsToChmTerms(UpdateScript):
    title = 'Dutch CHM portal - pick lists and chm_terms glossary'
    authors = ('Stanciu Gabriel', )
    description = '#618 The Dutch CHM portal has the new CHM terms glossary, and also a pick-list with the same content, used for the "main topics covered" property of "Project" objects. Remove the second property from the schema, and its pick list, and merge the values into the new chm_terms property. '
    creation_date = 'Aug 9, 2011'

    def _update(self, portal):
        def traversal(x):
            l = []
            if translate(x['ob'].title)=='':
                l.append(x['ob'].title)
            for i in x['children']:
                l.extend(traversal(i))
            return l

        def translate(title):
            if title == 'Topics for experts network': return True
            for i in portal.chm_terms.objectValues('Naaya Glossary Folder'):
                if title.lower() == i.English.lower(): return i.Dutch
                if title.replace('biological diversity', 'biodiversity') == i.English: return i.Dutch
                for j in i.objectValues('Naaya Glossary Element'):
                    if title.lower() == j.English.lower():  return j.Dutch
                    if title.replace('tourism', ' tourism') == j.English: return j.Dutch
                    if title.replace('terrestrrial', 'terrestrial') == j.English: return j.Dutch
            return ''

        def update(arg, mtype):
            for brain in portal_catalog(meta_type=mtype):
                ob = brain.getObject()
                str_en=''
                str_nl=''
                for i in ob.main_topics:
                    x = expnet_topics ._getOb(i)
                    str_en=str_en+x.title+', '
                    str_nl=str_nl+translate(x.title)+', '
                ob._setLocalPropValue('chm_terms', 'en', str_en[:-2])
                ob._setLocalPropValue('chm_terms', 'nl', str_nl[:-2])

        schema_tool = portal.getSchemaTool()
        expnet_topics = portal.getPortletsTool()._getOb('expnet_topics', default=None)
        portal_catalog = portal.getCatalogTool()

        nyproject = schema_tool._getOb('NyProject')
        main_topicsP = nyproject._getOb('main_topics-property', default=None)
        if main_topicsP is not None: update(nyproject, 'Naaya Project')

        nyorganisation = schema_tool._getOb('NyOrganisation')
        main_topicsO = nyorganisation._getOb('main_topics-property', default=None)
        if main_topicsO is not None: update(nyorganisation, 'Naaya Organisation')

        nyexpert = schema_tool._getOb('NyExpert')
        main_topicsE = nyorganisation._getOb('main_topics-property', default=None)
        if main_topicsE is not None: update(nyexpert, 'Naaya Expert')

        if main_topicsP is not None and main_topicsO is not None and main_topicsE is not None:
            l = traversal(expnet_topics.get_nodes_as_tree())
            if l == []:
                nyproject._getOb('chm_terms-property').visible = True
                self.log.debug('Made the CHM terms property visible for NyProject')
                nyorganisation._getOb('chm_terms-property').visible = True
                self.log.debug('Made the CHM terms property visible for NyOrganisation')
                nyexpert._getOb('chm_terms-property').visible = True
                self.log.debug('Made the CHM terms property visible for NyExpert')

                nyproject.manage_delObjects(['main_topics-property'])
                self.log.debug('Deleted main_topics-property for NyProject')
                nyorganisation.manage_delObjects(['main_topics-property'])
                self.log.debug('Deleted main_topics-property for NyOrganisation')
                nyexpert.manage_delObjects(['main_topics-property'])
                self.log.debug('Deleted main_topics-property for NyExpert')

                portal.getPortletsTool().manage_delObjects('expnet_topics')
                self.log.debug('Deleted expnet_topics')
                return True
            else:
                self.log.error("Pick items that didn't match: %r", l)
                return False
        else:
            self.log.debug('Nothing to update')
            return True

class FixTypo(UpdateScript):
    title = 'Fix typo in CHM terms'
    authors = ('Stanciu Gabriel', )
    creation_date = 'Aug 9, 2011'

    def _update(self, portal):
        ob = portal.chm_terms._getOb('04')._getOb('04_10')
        old_title = ob.title
        if ob.title == 'Biodiversity and  tourism':
            ob.title = ob.title.replace(' tourism', 'tourism')
            self.log.debug('"%s" is now: "%s"'%(old_title,ob.title))
        return True