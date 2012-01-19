from naaya.core.zope2util import is_descendant_of, path_in_site, ofs_path

from Products.naayaUpdater.updates import UpdateScript

from destinet.publishing.subscribers import place_pointers


class RebuildPointers(UpdateScript):
    """
    Removes all pointers and re-links with new pointers
    the data published in certain destinet locations

    """
    title = 'Destinet: rebuild Naaya Pointers to objects'
    creation_date = 'Dec 12, 2011'
    authors = ['Mihnea Simian']
    description = ('Removes all pointers and re-links with new pointers '
                   'the data published in certain destinet locations')

    def _update(self, portal):
        countries_dir = portal['countries']
        topics_dir = portal['topics']
        who_dir = portal['who-who']
        resources_dir = portal['resources']
        market_place_dir = portal['market-place']
        events_dir = portal['events']
        news_dir = portal['News']
        cat = portal.getCatalogTool()
        pointers = map(lambda x: x.getObject(),
                  cat.search({'meta_type': 'Naaya Pointer',
                              'path': [ofs_path(countries_dir),
                                       ofs_path(topics_dir),
                                       ofs_path(who_dir)]}))
        count = 0
        for p in pointers:
            if not is_descendant_of(p, countries_dir):
                if len(p.getPhysicalPath()) <= 6:
                    #self.log.debug("Cleaning pointer: %s" % ofs_path(p))
                    count += 1
                    p.aq_parent._delObject(p.id)
            else:
                #self.log.debug("Cleaning pointer: %s" % ofs_path(p))
                count += 1
                p.aq_parent._delObject(p.id)
        self.log.debug("Cleaned %d pointers" % count)

        objects = []
        objects.extend(map(lambda x: x.getObject(),
                           cat.search({'meta_type': 'Naaya Event',
                                       'path': ofs_path(events_dir)})
                           ))
        objects.extend(map(lambda x: x.getObject(),
                           cat.search({'meta_type': 'Naaya News',
                                       'path': ofs_path(news_dir)})
                           ))
        objects.extend(map(lambda x: x.getObject(),
                           cat.search({'meta_type': ['Naaya File', 'Naaya Media File',
                                                     'Naaya URL', 'Naaya Publication'],
                                       'path': ofs_path(resources_dir)})
                           ))
        count = len(objects)
        for obj in objects:
            place_pointers(obj)
        objects = []
        objects.extend(map(lambda x: x.getObject(),
                           cat.search({'meta_type': 'Naaya Publication',
                                       'path': ofs_path(market_place_dir)})
                           ))
        objects.extend(map(lambda x: x.getObject(),
                           cat.search({'meta_type': 'Naaya Contact',
                                       'path': [ofs_path(market_place_dir),
                                                ofs_path(who_dir)]})
                           ))
        count += len(objects)
        for obj in objects:
            place_pointers(obj, exclude=['target-groups'])
        pointers = cat.search({'meta_type': 'Naaya Pointer',
                              'path': [ofs_path(countries_dir),
                                       ofs_path(topics_dir),
                                       ofs_path(who_dir)]})
        self.log.debug("Finished placing %d pointers for %d objects" %
                       (len(pointers), count))

        return True
