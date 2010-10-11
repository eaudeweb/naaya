from Products.naayaUpdater.updates import UpdateScript

class UpdateTitles(UpdateScript):
    """  """
    title='Update Titles when both LocalAttribute and attribute is present'
    description='There is a bug that seems to happen in the semide site, both'
    'LocalAttributes and attributes are present'

    def _update(self, portal):
        """ """
        if hasattr(portal, 'zoai'):
            catalog = portal.getCatalogTool()
            brains = catalog(path='/')
            for brain in brains:
                obj = brain.getObject()
                if ('title' in obj.__dict__ and
                    (obj.__dict__['title'] == u'' or
                     obj.__dict__['title'] == '') and

                    '_local_properties' in obj.__dict__ and
                    'title' in obj.__dict__['_local_properties'] and
                    len(obj.__dict__['_local_properties']['title'])):
                    del obj.title
                    self.log.info("Deleted title attribute from %r" %
                                  obj.absolute_url())
        return True
