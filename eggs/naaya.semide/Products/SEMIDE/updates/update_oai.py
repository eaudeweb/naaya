from Products.naayaUpdater.updates import UpdateScript

class UpdateOAI(UpdateScript):
    """  """
    id = 'update_oai'
    title='Update OAI Server Catalog indexes'
    description='Update current indexes of the OAIServer\'s ZCatalog'

    def _update(self, portal):
        """ """
        if hasattr(portal, 'zoai'):
            catalog = portal.zoai.getCatalog()
            catalog.manage_delIndex(catalog.indexes())
            catalog.manage_delColumn(catalog.schema())
            portal.zoai.add_indexes(catalog)
            portal.zoai.add_metadata(catalog)
            #portal.zoai.update(True)
        return True
