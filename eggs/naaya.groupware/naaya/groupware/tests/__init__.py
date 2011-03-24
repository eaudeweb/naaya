from Products.Naaya.tests.NaayaTestCase import (NaayaPortalTestPlugin,
                                                NaayaTestCase)
from Products.Naaya.tests.NaayaFunctionalTestCase import (
    NaayaFunctionalTestCase)

class GWFunctionalTestCase(NaayaFunctionalTestCase):
    """ Generic class for Groupware tests """

    _naaya_plugin = 'GWPortalTestPlugin'

class GWTestCase(NaayaTestCase):
    """ Generic class for Groupware tests """

    _naaya_plugin = 'GWPortalTestPlugin'

class GWPortalTestPlugin(NaayaPortalTestPlugin):
    """ Nose plugin that prepares the environment for a Groupware site to run

    """

    def portal_fixture(self, app):
        """ Create a groupware site and return the portal_id """

        from naaya.groupware.groupware_site import manage_addGroupwareSite
        portal_id = 'gw_portal'
        manage_addGroupwareSite(app, portal_id , 'Groupware Test Site')
        return portal_id
