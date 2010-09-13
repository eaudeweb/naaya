from datetime import datetime

from Products.naayaUpdater.updates import UpdateScript

class AddForumReleaseDate(UpdateScript):
    title = 'Add release date to NyForum'
    authors = ['Andrei Laza']
    creation_date = 'Sep 13, 2010'

    def _update(self, portal):
        forums = portal.searchCatalog({'meta_type': 'Naaya Forum'}, None, None)
        for forum in forums:
            self.log.debug('Found forum at %s' % forum.absolute_url(1))
            if not hasattr(forum, 'releasedate'):
                forum.releasedate = forum.bobobase_modification_time()
                portal.recatalogNyObject(forum)
                self.log.debug('Added releasedate attribute for forum at %s' %
                        forum.absolute_url(1))
        return True

