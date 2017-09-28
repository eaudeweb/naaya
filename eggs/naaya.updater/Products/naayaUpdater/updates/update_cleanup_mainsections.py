from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateCleanupMainsections(UpdateScript):
    title = 'Cleanup main sections'
    authors = ['Andrei Laza']
    creation_date = 'May 26, 2011'
    priority = PRIORITY['LOW']
    description = "This removes main sections that are not in the database (If you get 'Saving positons failed. New order list and old list have different length'). This happens if you remove a folder without removing it from mainsections list."

    def _update(self, portal):
        used_mainsections = portal.getMainTopics()
        main_sections = portal.maintopics
        if len(used_mainsections) != len(main_sections):
            portal.maintopics = [path for path in portal.maintopics if portal.utGetObject(path) is not None]
            self.log.debug('Updated main topics: %s' % portal.maintopics)
        else:
            self.log.debug('No need to update')
        return True
