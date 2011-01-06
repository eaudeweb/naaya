from DateTime import DateTime
from Products.naayaUpdater.updates import UpdateScript

news_items_lvn = [
       'hoe-kan-de-afname-van-de-mondiale-biodiversiteit-worden-verminderd',
       '60.000-euro-voor-drie-prijsvragen-biodiversiteit',
       'lnv-stopt-extra-geld-in-gegevensopslag-natuur',
       'verburg-ondersteunt-ondernemers-met-oplossing-op-het-gebied-van-biodiversiteit',
       'congres-over-biodiversiteit-en-economie',
       'openluchttentoonstelling-wild-wonders-of-europe',
       'verburg-organiseert-internationale-conferentie-over-landbouw-voedselzekerheid-en',
       'lnv-start-onderzoek-naar-meest-kansrijke-weidevogelgebieden',
       'nederland-duitsland-en-denemarken-zetten-in-op-klimaatneutrale-wadden',
       'vertoning-film-een-toekomst-voor-weidevogels',
       'minister-verburg-geeft-startschot-programma-naar-een-rijke-waddenzee',
       'nederland-start-internationaal-jaar-van-de-biodiversiteit-met-oprichting-centrum'
    ]

class UpdateNewsContributor(UpdateScript):
    """ """
    title = 'Update news contributor'
    creation_date = 'Jan 6, 2011'
    authors = ['Alexandru Plugaru']
    description = 'Update contributors for chm_nl/nieuws/'

    def _update(self, portal):
        if portal.id == 'chm_nl':
            for news_item in portal.nieuws.objectValues('Naaya News'):
                if news_item.contributor == 'wee':
                    if news_item.releasedate < DateTime('2010/01/01') or news_item.id in news_items_lvn:
                        news_item.contributor = 'LVN'
                        self.log.info('Updated to contributor "LVN" %s', news_item.absolute_url())
                    elif news_item.releasedate >= DateTime('2010/01/01'):
                        news_item.contributor = 'CoalitieBiodiversiteit'
                        self.log.info('Updated to contributor "CoalitieBiodiversiteit"%s', news_item.absolute_url())
        return True
