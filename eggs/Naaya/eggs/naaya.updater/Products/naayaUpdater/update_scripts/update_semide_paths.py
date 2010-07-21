from DateTime import DateTime
from naaya.content.semide.news import semnews_item
from naaya.content.semide.event import semevent_item
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY
from naaya.core.utils import path_in_site

import transaction

class UpdateSemidePaths(UpdateScript):
    """ Update Semide News and Events paths. """
    id = 'update_semide_paths'
    title = 'Update Semide Paths'
    creation_date = DateTime('Jul 21, 2010')
    authors = ['Alexandru Plugaru']
    priority = PRIORITY['HIGH']
    description = 'Find all news/events items in a dir and create a dictionary\
with new and old paths'
    #dependencies = []
    categories = ['semide']

    def _update(self, portal):
        """ """
        catalog = portal.getCatalogTool()
        if portal.id == 'semide':
            news_dir = portal.thematicdirs.news
            events_dir = portal.thematicdirs.events

            news_items = news_dir.getCatalogedObjects(
                meta_type=[semnews_item.config['meta_type']])
            paths = {}
            for news_item in news_items:
                paths[news_item.id] = path_in_site(news_item)
            news_dir.redirect_paths = paths
            news_dir._p_changed = 1

            event_items = events_dir.getCatalogedObjects(
                meta_type=[semevent_item.config['meta_type']])
            paths = {}
            for event_item in event_items:
                paths[event_item.id] = path_in_site(event_item)

            events_dir.redirect_paths = paths
            events_dir._p_changed = 1
            return True
