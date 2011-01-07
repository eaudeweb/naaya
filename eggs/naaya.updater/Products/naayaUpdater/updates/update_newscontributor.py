from DateTime import DateTime
from Products.naayaUpdater.updates import UpdateScript

class UpdateNewsContributor(UpdateScript):
    """ """
    title = 'Update news contributor'
    creation_date = 'Jan 6, 2011'
    authors = ['Alexandru Plugaru']
    description = 'Update contributors for chm_nl/nieuws/'

    def _update(self, portal):
        if portal.id == 'chm_nl':
            for news_item in portal.nieuws.objectValues('Naaya News'):
                if news_item.contributor == 'LVN':
                     news_item.contributor = 'LNV'
        return True
