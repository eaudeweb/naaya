from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaBase.NyGadflyContainer import NyGadflyContainer
from NyForum import STATISTICS_CONTAINER

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

class ZGadFlyMigration(UpdateScript):
    title = 'Migrate ZGadFly stats to naaya.sql'
    authors = ['Alexandru Plugaru', 'Andrei Laza']
    creation_date = 'Oct 15, 2010'

    def _update(self, portal):
        topics_stats = {}
        catalog = portal.getCatalogTool()
        for brain in catalog(meta_type='Naaya Forum'):
            forum = brain.getObject()
            self.log.debug('Found forum at %r' % forum.absolute_url(1))
            stats_container = getattr(forum, STATISTICS_CONTAINER, None)
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
                stats_container = forum._getStatisticsContainerCursor()

                for topic in forum.get_topics():
                    forum.setTopicHits(topic.id, topics_stats.get(topic.id, 0))
        return True
