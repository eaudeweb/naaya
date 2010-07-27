from Products.naayaUpdater.updates import UpdateScript

class UpdateNewsEventsPathsUpdateScript(UpdateScript):
    """  """
    id = 'update_newsevents_paths'
    title='Fix paths news and events folders'
    description='Paths like 2007/07/2007/07 are broken and should be fixed'
    categories = ['semide']

    def _update(self, portal):
        """ """
        if portal.id == 'semide':
            news_folder = portal.thematicdirs.news
            #events_folder = portal.thematicdirs.events
            news_items = news_folder.getCatalogedObjects('Naaya Semide News',
                                            path=news_folder.absolute_url(1))

            for news_item in news_items:
                news_item_path = news_item.absolute_url(1).split('/')
                if len(news_item_path) > 6:
                    month_dir = getattr(getattr(
                                    news_folder, news_item_path[-3]),
                                    news_item_path[-2])
                    data = news_item.aq_parent.manage_cutObjects([news_item.id])
                    month_dir.manage_pasteObjects(data)
                    self.log.debug("Moved %r to %r" % (
                        news_item.absolute_url(1), month_dir.absolute_url(1)))
            #Delete empty dirs
            news_folders = news_folder.getCatalogedObjects('Naaya Folder',
                                            path=news_folder.absolute_url(1))
            for news_folder in news_folders:
                if not len(news_folder.getCatalogedObjects('Naaya Semide News',
                                        path=news_folder.absolute_url(1))):
                    news_folder.aq_parent.manage_delObjects(news_folder.id)
                    self.log.debug(
                        "Deleted empty %r" %
                        news_folder.absolute_url(1)
                    )
            return True
