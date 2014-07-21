from Products.Five.browser import BrowserView
from DateTime import DateTime
import os


class ExportUpdatedObjects(BrowserView):
    before = 20     # look behind 20 days
    base = "/tmp/export-obj"

    def __call__(self):
        site = self.context.getSite()
        catalog = site.portal_catalog
        start = DateTime() - self.before
        brains = catalog.searchResults(bobobase_modification_time={'query':start, 'range':'min'})
        if not os.exists(self.base):
            os.mkdirs(self.base)

        for brain in brains:
            ob = brain.getObject()
            f = os.path.join(self.base, '/'.join(ob.getPhysicalPath())) + '.zexp'
            base = os.path.dirname(f)
            if not os.exists(base):
                os.makedirs(base)
            ob._p_jar.exportFile(ob._p_oid, f)

        return "Done"
