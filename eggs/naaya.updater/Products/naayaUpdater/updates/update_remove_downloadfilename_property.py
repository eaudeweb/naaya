from Products.naayaUpdater.updates import UpdateScript
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
import traceback

# this is for compatibility with older versions of Zope (< 2.9)
try:
    import transaction
    begin_transaction = transaction.begin
    get_transaction = transaction.get
except:
    begin_transaction = get_transaction().begin

class RemoveDownloadfilenameProperty(UpdateScript):
    """
    Script to remove 'downloadfilename' property from old ExFile objects
    """

    title = "Remove 'downloadfilename' property from ExFile objects"
    authors = ['Valentin Dumitru']
    creation_date = 'Nov 22, 2011'
    description = "Remove 'downloadfilename' property from ExFile objects"

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        for ob in portal.getCatalogedObjectsCheckView(
            meta_type=['Naaya File', 'Naaya Extended File']):
            try:
                delattr(ob, 'downloadfilename')
                self.log.debug('"downloadfilename" property deleted from object %s at %s' % (ob.title_or_id(), ob.absolute_url()))
            except AttributeError:
                pass
        return True
