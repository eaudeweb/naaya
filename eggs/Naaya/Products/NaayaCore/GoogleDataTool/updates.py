from Products.naayaUpdater.updates import UpdateScript


class RemoveGdataObjects(UpdateScript):
    title = 'Remove gdata objects from Statistics Tool'
    authors = ['Alex Morega']
    creation_date = 'Dec 17, 2012'

    def _update(self, portal):
        tool = portal['portal_statistics']
        for name in ['ga_service', 'gd_service']:
            if hasattr(tool.aq_base, name):
                self.log.info('%r: removing %s', portal, name)
                delattr(tool.aq_base, name)
        return True
