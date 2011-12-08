from naaya.core.zope2util import ofs_walk
from Products.naayaUpdater.updates import UpdateScript
from naaya.core.utils import force_to_unicode
from Products.Naaya.interfaces import INySite
from Products.Naaya.NyFolder import addNyFolder


class CountriesFoldersFromGlossary(UpdateScript):
    """
    Removes empty translations or empty languages in
    local properties implementation

    """
    title = 'Destinet: create folders for countries in glossary'
    creation_date = 'Dec 08, 2011'
    authors = ['Mihnea Simian']
    description = ('Iterates continents and countries in countries_glossary'
                   ' and creates the corresponding folders in `countries`')

    def _update(self, portal):
        glossary = portal['countries_glossary']
        countriesdir = portal['countries']
        existing = {}

        for continent in countriesdir.objectValues('Naaya Folder'):
            existing[continent.title] = continent

        for continent in glossary.objectIds('Naaya Glossary Folder'):
            if continent not in existing:
                c_id = addNyFolder(countriesdir, '', title=continent)
                continentdir = countriesdir[c_id]
                self.log.debug("CONTINENT CREATED %s" % continentdir.absolute_url())
            else:
                continentdir = existing[continent]
                self.log.debug("Continent found: %s" % continentdir.absolute_url())

            existing_countries = map(lambda x: getattr(x, 'title'),
                                     continentdir.objectValues('Naaya Folder'))

            for country in glossary[continent].objectValues('Naaya Glossary Element'):
                # country is glossary el., continentdir is nyfolder
                if country.title not in existing_countries:
                    c_id = addNyFolder(continentdir, '', title=country.title)
                    countrydir = continentdir[c_id]
                    self.log.debug("COUNTRY CREATED %s" % countrydir.absolute_url())
                else:
                    self.log.debug("Country found: %s in %s" %
                                   (country.title, continentdir.absolute_url()))

        return True
