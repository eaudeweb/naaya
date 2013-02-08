from Products.Naaya.tests.NaayaTestCase import (NaayaPortalTestPlugin,
                                                NaayaTestCase)
from Products.Naaya.tests.NaayaFunctionalTestCase import (
    NaayaFunctionalTestCase)

class GWFunctionalTestCase(NaayaFunctionalTestCase):
    """ Generic class for Groupware tests """

    _naaya_plugin = 'GWPortalTestPlugin'

    def browser_do_login(self, username, password):
        """ GW login process is somewhat different """
        self.browser.go(self.portal.absolute_url() + '/login_html')
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, '__ac_name')
        self.browser.clicked(form, field)
        form['__ac_name'] = username
        form['__ac_password'] = password
        self.browser.submit()
        self.assertTrue('Logout (%s)' % username in self.browser.get_html())

class GWTestCase(NaayaTestCase):
    """ Generic class for Groupware tests """

    _naaya_plugin = 'GWPortalTestPlugin'

class GWPortalTestPlugin(NaayaPortalTestPlugin):
    """ Nose plugin that prepares the environment for a Groupware site to run

    """
    name = 'naaya-groupware'

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
        from Products.CookieCrumbler.CookieCrumbler import manage_addCC

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
        #index_html, now registered as simpleView
        app._delObject('index_html')

        #gw_macro
        manage_addPageTemplate(app, 'gw_macro', '')
        app.gw_macro.write(get_content('gw_macro.zpt'))

        #CookieCrumbler
        manage_addCC(app, 'login')
        #login_form
        manage_addPageTemplate(app.login, 'login_form', '')
        app.login.login_form.write(
            get_content('cookie_crumbler/login_form.zpt'))

        manage_addPythonScript(app.login, 'index_html')
        app.login.index_html.write(
            get_content('cookie_crumbler/index_html.py'))

        manage_addPythonScript(app.login, 'logged_in')
        app.login.logged_in.write(
            get_content('cookie_crumbler/logged_in.py'))

        manage_addPythonScript(app.login, 'logged_out')
        app.login.logged_out.write(
            get_content('cookie_crumbler/logged_out.py'))

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
