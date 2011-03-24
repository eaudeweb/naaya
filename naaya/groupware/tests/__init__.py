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
        """ Create a groupware site and return the portal_id.

        XXX: Create a script that adds all zope customizations
        """

        import os
        import transaction
        from Products.PageTemplates.ZopePageTemplate import (
            manage_addPageTemplate)
        from Products.PythonScripts.PythonScript import manage_addPythonScript
        from naaya.groupware.groupware_site import manage_addGroupwareSite
        from naaya.gwapplications.applications import GWApplications

        portal_id = 'gw_portal'
        #Adding groupware site
        manage_addGroupwareSite(app, portal_id , 'Groupware Test Site')


        #
        # This *things* bellow should be added automatically somehow on site
        # creation.
        #

        #Zope customization path
        zope_customisation = os.path.join(os.path.dirname(__file__), '..',
                                          'zope_customisation')

        def get_content(filename):
            return open(os.path.join(zope_customisation,
                                     filename), 'rb').read()
        #index_html
        app._delObject('index_html')
        manage_addPageTemplate(app, 'index_html', '')
        app.index_html.write(get_content('index.html'))

        #gw_macro
        manage_addPageTemplate(app, 'gw_macro', '')
        app.gw_macro.write(get_content('gw_macro.zpt'))

        #groupedIGs
        manage_addPythonScript(app, 'groupedIGs')
        app.groupedIGs.write(get_content('groupedIGs.py'))

        """
        Not required:

        #GWApplications
        #appid, title, admin_mail, mail_from
        app._setObject('applications', GWApplications('applications',
                                                      'Applications',
                                                      'admin@email.com',
                                                      'admin@email.com'))
        """
        return portal_id
