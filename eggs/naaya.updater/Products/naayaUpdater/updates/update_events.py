from Products.naayaUpdater.updates import UpdateScript
from utils import physical_path

class UpdateBrokenEvents(UpdateScript):
    """ Update broken NaayaEvent objects """
    title = 'Update broken NaayaEvent objects'
    authors = ['Cornel Nitu']
    description = """
        https://svn.eionet.europa.eu/projects/Naaya/ticket/400
        (Error when editing an item on the NL CHM)
        Revision 15440
        """
    creation_date = 'Sep 29, 2010'

    def _update(self, portal):
        self.log.debug(physical_path(portal))

        for event in list_broken_events(portal):
            event.theme = []
            event.target_group = []
            event._p_changed = 1
            self.log.info(event.absolute_url())
        return True

    def getPortals(self, context=None, meta_types=None):
        if context is None:
            context = self.getPhysicalRoot()
        return [context.chm_nl]

def list_broken_events(portal):
    catalog = portal.getCatalogTool()

    for brain in catalog(meta_type='Naaya Event'):
        event = brain.getObject()
        #theme property
        try:
            if event.theme == ['']:
                yield event
        except AttributeError:
           yield event

        #target_group property
        try:
            if event.target_group == ['']:
                yield event
        except AttributeError:
           yield event
