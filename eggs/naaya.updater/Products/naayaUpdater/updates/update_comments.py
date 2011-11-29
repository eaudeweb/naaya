from Products.naayaUpdater.updates import UpdateScript
from utils import physical_path

class UpdateComments(UpdateScript):
    """ Migration script from Naaya Comments """
    title = 'Migration script from Naaya Comments'
    authors = ['Cornel Nitu']
    description = 'Revision 15440'
    creation_date = 'Oct 4, 2010'

    def _update(self, portal):
        self.log.debug(physical_path(portal))

        for obj in list_obsolete_comented_objects(portal):
            migrate_comments(obj, self.log)
        delete_index(portal)
        return True

def migrate_comments(obj, log):
    try:
        for c in obj._NyComments__comments_collection.values():
            obj._comment_add(c.title, c.body, c.author, c.date)
            log.info('%s: %s' % (obj.absolute_url(), c.id))
        del obj._NyComments__comments_collection
        obj._p_changed = 1
    except AttributeError:
        log.info('Mising __comments_collection on %s' % obj.absolute_url())

def list_obsolete_comented_objects(portal):
    catalog = portal.getCatalogTool()
    result = set()
    for brain in catalog.getCatalogTool()({'submitted': 1, 'has_comments': 1}):
        result.add(catalog.getobject(brain.data_record_id_))
    return result

def delete_index(portal):
    catalog = portal.getCatalogTool()
    try:
        catalog.getCatalogTool().manage_delIndex(['has_comments'])
    except:
        pass
