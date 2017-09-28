from Products.naayaUpdater.updates import UpdateScript

class UpdateFindCustomIndexes(UpdateScript):
    """
    Generic script that returns a list with all customised indexes of folders
    """

    title = 'Find customised indexes'
    authors = ['Valentin Dumitru']
    creation_date = 'Oct 10, 2011'
    description = 'Finds customised indexes of folders'

    def _update(self, portal):
        self.find_customised_indexes(portal)
        return True

    def find_customised_indexes(self, portal):
        """ Returns a list with customised indexes of folders """
        folders = portal.getCatalogedObjectsCheckView(meta_type='Naaya Folder')
        for folder in folders:
            templates = [pt for pt in folder.objectValues(['Page Template']) if pt.getId() == 'index']
            if templates:
                for template in templates:
                    template_url = template.absolute_url()
                    self.log.debug(template_url)
                    custom_index = folder.compute_custom_index_value()
                    if not custom_index:
                        custom_index = 'None'
                    self.log.debug('Custom index: %s' % custom_index)
        return True