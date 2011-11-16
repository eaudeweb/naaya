""" Base test cases
"""
from plone.testing import z2
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
#from plone.app.testing import applyProfile

class EEAFixture(PloneSandboxLayer):
    """ Custom fixture
    """

    def setUpZope(self, app, configurationContext):
        """ Setup Zope
        """
        import eea.aoamap
        self.loadZCML(package=eea.aoamap)
        z2.installProduct(app, 'eea.aoamap')

    def tearDownZope(self, app):
        """ Uninstall Zope
        """
        z2.uninstallProduct(app, 'eea.aoamap')

    def setUpPloneSite(self, portal):
        """ Setup Plone
        """
        #applyProfile(portal, 'eea.aoamap:default')

EEAFIXTURE = EEAFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(EEAFIXTURE,),
            name='EEAAoAMap:Functional')
