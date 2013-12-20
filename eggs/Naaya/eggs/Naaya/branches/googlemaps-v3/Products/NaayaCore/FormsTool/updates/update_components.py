from Products.naayaUpdater.updates import UpdateScript
from Products.NaayaCore.FormsTool.interfaces import ITemplate
from zope.component import getGlobalSiteManager

from naaya.component import bundles

bundle_for_site_cls = {
    'NySite': 'Naaya',
    'CHMSite': 'CHM',
    'EnviroWindowsSite': 'EW',
    'GroupwareSite': 'Groupware',
}

class MigrateToBundles(UpdateScript):
    """
    * Set a portal's bundle to match its class name
    * register all portal_forms templates as ITemplate utilities
    """
    title="Migrate to bundles"
    authors=["Alexandru Plugaru"]
    creation_date = 'Jul 21, 2011'

    def _update(self, portal):
        sm = portal.getSiteManager()

        if sm.__name__ == '++etc++site':
            sm.__name__ = 'database'
            self.log.info("Set name of local site manager to %r", sm.__name__)

        bundle = portal.get_bundle()
        portal_cls_name = portal.__class__.__name__
        if bundle is getGlobalSiteManager() or bundle is bundles.get('Naaya'):
            bundle_name = bundle_for_site_cls.get(portal_cls_name, 'Naaya')
            bundle = bundles.get(bundle_name)
            portal.set_bundle(bundle)
            self.log.info("Portal bundle set to %r", bundle_name)
        else:
            self.log.info("Not changing portal bundle %r", bundle)

        forms_tool = portal.getFormsTool()
        for template in forms_tool.objectValues():
            name = template.getId()
            sm.registerUtility(template, ITemplate, name)
            self.log.info("Registered ITemplate %r", name)

        return True

