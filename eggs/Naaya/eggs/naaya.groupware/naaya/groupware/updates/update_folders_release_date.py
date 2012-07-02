from datetime import date
from Products.naayaUpdater.updates import UpdateScript

class UpdateFoldersReleaseDate(UpdateScript):
    """ """
    title = 'Update folders release date for Groupware Sites'
    creation_date = 'Jun 28, 2012'
    authors = ['Bogdan Tanase']
    description = ('Due to CIRCA migration some folders have release date to '
                   'their expiration date. Update their release date to the '
                   'oldest object from folder.')

    def _update(self, portal):
        today = date.today().strftime("%d/%m/%Y")
        catalog_tool = portal.getCatalogTool()
        brains = catalog_tool.query_brains_ex('Naaya Folder',
                                              releasedate=today,
                                              releasedate_range='min')
        for brain in brains:
            ob = brain.getObject()
            subobjects = sorted(ob.objectValues(),
                                key=lambda subob: subob.releasedate)

            if subobjects:
                ob.releasedate = subobjects[0].releasedate
            else:
                ob.setReleaseDate(today)

        return True
