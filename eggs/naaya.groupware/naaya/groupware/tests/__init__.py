import transaction
from Products.Naaya.tests.NaayaTestCase import (NaayaTestCase, NaayaTestLayer,
                                                wrap_with_request)
from Products.Naaya.tests.NaayaFunctionalTestCase import (
    NaayaFunctionalTestCase)


def gw_portal_fixture(app):
    """ Create a groupware site with the Zope customisations; return its id """
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
    app[portal_id].administrator_email = 'site.admin@example.com'


    #
    # This *things* bellow should be added automatically somehow on site
    # creation.
    #

    #Zope customization path
    zope_customisation = os.path.join(os.path.dirname(__file__), '..',
                                      'zope_customisation')

    def get_content(filename):
        with open(os.path.join(zope_customisation, filename), 'rb') as f:
            return f.read()
    # Root scripts the groupware standard_template uses
    for name, value in [('network_logo_url', '/images/logo.png'),
                        ('network_address', 'Test address')]:
        manage_addPythonScript(app, name)
        app[name].write("return %r" % value)
    for name in ('get_gw_root', 'dropdowns.txt', 'getBreadCrumbTrail'):
        manage_addPythonScript(app, name)
        app[name].ZPythonScript_edit(
            'request' if name == 'getBreadCrumbTrail' else '',
            get_content(name + '.py').decode('utf-8'))

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


class GWTestLayer(NaayaTestLayer):
    """ NaayaTestLayer with a groupware site, which the tests get as portal """

    @classmethod
    def setUp(cls):
        cleanup, db = cls._tzope.db_layer()
        fake_root = wrap_with_request(db.open().root()['Application'])
        app = fake_root.app
        fake_root.REQUEST.AUTHENTICATED_USER = app.acl_users.getUserById('admin')
        cls._gw_portal_id = gw_portal_fixture(app)
        transaction.commit()
        cls._gw_cleanup = cleanup

    @classmethod
    def tearDown(cls):
        cls._gw_cleanup()

    @classmethod
    def testSetUp(cls):
        # NaayaTestLayer.testSetUp already opened the per-test database
        cls._current_app = NaayaTestLayer._current_app
        cls._current_portal = cls._current_app[cls._gw_portal_id]
        cls._current_fake_request = NaayaTestLayer._current_fake_request
        cls._mail_log = NaayaTestLayer._mail_log

    @classmethod
    def testTearDown(cls):
        pass


class GWFunctionalTestCase(NaayaFunctionalTestCase):
    """ Generic class for Groupware tests """

    layer = GWTestLayer

    def browser_do_login(self, username, password):
        """ GW login process is somewhat different """
        self.browser.go(self.portal.absolute_url() + '/login_html')
        form = self.browser.get_form(2)
        field = self.browser.get_form_field(form, '__ac_name')
        self.browser.clicked(form, field)
        form['__ac_name'] = username
        form['__ac_password'] = password
        self.browser.submit()
        html = self.browser.get_html()
        self.assertIn('/login/logout"', html)
        self.assertIn('search_string=%s"' % username, html)

class GWTestCase(NaayaTestCase):
    """ Generic class for Groupware tests """

    layer = GWTestLayer
