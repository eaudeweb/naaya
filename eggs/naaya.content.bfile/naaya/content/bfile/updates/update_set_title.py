#python imports
import mimetypes

#Naaya imports
from Products.naayaUpdater.updates import UpdateScript, PRIORITY

class UpdateSetTitle(UpdateScript):
    title = 'Set the title for bfiles with no titles'
    creation_date = 'Iul 18, 2014'
    authors = ['Tiberiu Ichim']
    priority = PRIORITY['HIGH']

    def _update(self, portal):
        catalog = portal.portal_catalog
        for brain in catalog(meta_type='Naaya Blob File'):
            bfile = brain.getObject()
            obj = bfile.aq_inner.aq_self

            if not hasattr(obj, 'title'):
                localprops = getattr(obj, "_local_properties", None)
                if not localprops:
                    self.log.info("No local properties %s", bfile.absolute_url())
                    continue
                obj.title = title = localprops['title']['en'][0]
                self.log.info("Migrated title for %s. New title: %s", bfile.absolute_url(), title)
 
        return True
