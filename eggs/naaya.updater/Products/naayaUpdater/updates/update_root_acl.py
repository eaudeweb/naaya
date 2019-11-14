from Products.naayaUpdater.updates import UpdateScript
from plone.keyring.interfaces import IKeyManager
from plone.keyring.keymanager import KeyManager
from five.localsitemanager import make_objectmanager_site
from zope.component.hooks import setSite
from Acquisition import aq_base


class UpdateACLPluggableAuth(UpdateScript):
    title = 'Migrate root ACL folder to Pluggable Auth Service'
    descrtiption = 'Migrate root ACL folder to Pluggable Auth Service'

    def _update(self, portal):
        """ """
        app = portal.aq_parent.aq_base
        make_objectmanager_site(app)
        setSite(app)

        # Create the keymanager for the plone_session plugin
        keymanager = KeyManager()
        app.keymanager = keymanager
        app.keymanager.__parent__ = app
        app.keymanager.__name__ = 'keymanager'
        keymanager.__parent__ = aq_base(app)
        app._components.registerUtility(aq_base(keymanager),
                                        IKeyManager,
                                        '')

        return True
