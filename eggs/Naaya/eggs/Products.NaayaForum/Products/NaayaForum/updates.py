from Products.naayaUpdater.updates import UpdateScript

class AddReleasedate(UpdateScript):
    title="Add releasedate for NaayaForums"
    authors=["Andrei Laza"]
    creation_date = 'Oct 13, 2011'

    def _update(self, portal):
        portal_catalog = portal.getCatalogTool()
        for brain in portal_catalog(meta_type='Naaya Forum'):
            forum = brain.getObject()
            if not hasattr(forum.aq_base, 'releasedate'):
                forum.releasedate = portal.process_releasedate('01/01/2011')
                self.log.debug('Added releasedate for forum at %s' % forum.absolute_url())
            else:
                self.log.debug('No need to update forum at %s' % forum.absolute_url())
        return True
