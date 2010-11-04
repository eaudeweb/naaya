from datetime import datetime

from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaBase.NyGadflyContainer import NyGadflyContainer
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

class ZGadFlyMigration(UpdateScript):
    title = 'Migrate ZGadFly stats to naaya.sql'
    authors = ['Alexandru Plugaru']
    creation_date = 'Oct 15, 2010'

    def _update(self, portal):
        topics_stats = {}
        catalog = portal.getCatalogTool()
        for brain in catalog(meta_type='Naaya Forum'):
            forum = brain.getObject()
            self.log.debug('Found forum at %r' % forum.absolute_url(1))
            stats_container = forum._getStatisticsContainer()
            if isinstance(stats_container, NyGadflyContainer):
                self.log.debug('Migrating statistics data from %r' %
                           forum.absolute_url(1))
                for topic in forum.get_topics():
                    try:
                        topics_stats[topic.id] = stats_container.get(
                            'HITS', topic=topic.absolute_url(1))[0]['HITS']
                    except:
                        topics_stats[topic.id] = 0

                forum._removeStatisticsContainer()
                stats_container = forum._getStatisticsContainer()

                for topic in forum.get_topics():
                    forum.setTopicHits(topic.id, topics_stats.get(topic.id, 0))
        return True
