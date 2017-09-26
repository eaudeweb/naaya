from Products.NaayaCore.EmailTool import EmailTool
from Products.naayaUpdater.updates import UpdateScript


class MigrateGeoTypeProperty(UpdateScript):
    """ Migrate the geo_type property to the new attributes

    category-organization
    category-marketplace
    category-supporting-solutions
    """

    title = 'Destinet: migrate the geotype property to new storage'
    creation_date = 'Dec 17, 2013'
    authors = ['Tiberiu Ichim']
    description = ('Migrates the geo_type property to category-organization, '
                   'category-marketplace, and category-supporting-solutions')

    def _update(self, portal):

        cat = portal['portal_catalog']
        contacts = cat.searchResults(meta_type="Naaya Contact")

        map_tool = portal['portal_map']
        mgsc = map_tool.getSymbolChildren
        mgpt = map_tool.getParentByTitle
        tfs = lambda s:map_tool.getSymbol(s).title

        #import pdb; pdb.set_trace()
        organizations_symbols = [s.id for s in mgsc(mgpt("ORGANIZATIONS").id)]
        market_symbols = [s.id for s in mgsc(mgpt("MARKET PLACE").id)]
        solutions_symbols = [s.id for s in mgsc(mgpt("MARKET SOLUTIONS").id)]
        businesses = map_tool.getSymbolByTitle("Businesses").id

        self.log.info("Migration: start migration of geo_types")
        EmailTool.divert_mail()

        counter = 0
        for brain in contacts:
            contact = brain.getObject()
            symbol = contact.geo_type
            if symbol:
                self.log.info("Migrating contact %s", contact.absolute_url())
                if symbol in market_symbols:
                    contact.__dict__['category-organization'] = businesses
                    contact.__dict__['category-marketplace'] = symbol
                    contact.__dict__['category-supporting-solutions'] = ''
                    self.log.info("Set category-marketplace to (marketplace) %s", tfs(symbol))
                elif symbol in solutions_symbols:
                    contact.__dict__['category-organization'] = businesses
                    contact.__dict__['category-marketplace'] = ''
                    contact.__dict__['category-supporting-solutions'] = symbol
                    self.log.info("Set category-supporting-solutions to (solutions) %s", tfs(symbol))
                elif symbol in organizations_symbols:
                    contact.__dict__['category-organization'] = symbol
                    contact.__dict__['category-marketplace'] = ''
                    contact.__dict__['category-supporting-solutions'] = ''
                    self.log.info("Set category-organization to (organizations) %s", tfs(symbol))
                else:
                    self.log.info("Symbol without parent: %s", tfs(symbol))

                contact._p_changed = True
                counter += 1

        EmailTool.divert_mail(False)
        self.log.info("Migration: end migration")
        return True

