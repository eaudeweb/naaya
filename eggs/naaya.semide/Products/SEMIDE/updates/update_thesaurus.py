from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaThesaurus.ThesaurusCatalog import manage_addThesaurusCatalog
class UpdateThesaurus(UpdateScript):
    """  """
    id = 'update_thesaurus'
    title='Removes useless alias in thesaurus'
    description='Removes catalog property of the portal_thesaurus and renames'
    '``thesaurus_catalog`` to ``catalog``'

    def _update(self, portal):
        """ """
        portal.portal_thesaurus.manage_delObjects(['catalog','thesaurus_catalog'])
        manage_addThesaurusCatalog(portal.portal_thesaurus)
        update_script = portal.portal_thesaurus.update_catalog
        update_script.ZPythonScript_edit('', update_script.read().replace('.thesaurus_catalog', '.catalog'))
        update_script()
        return True
