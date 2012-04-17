from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

def load_file(filename):
    import os
    from StringIO import StringIO
    from Globals import package_home
    filename = os.path.sep.join([package_home(globals()), filename])
    data = StringIO(open(filename, 'rb').read())
    data.filename = os.path.basename(filename)
    return data


class LayoutToolFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for the PhotoArchive product"""

    def test_add_logo(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/admin_logos_html')
        form = self.browser.get_form('frmAdd')
        expected_controls = set(['left_logo', 'right_logo', 'del_leftlogo'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        form['del_leftlogo'] = ['on']

        self.browser.clicked(form,
                self.browser.get_form_field(form, 'del_leftlogo'))
        self.browser.submit()

        form = self.browser.get_form('frmAdd')
        found_controls = set(c.name for c in form.controls)
        self.assertFalse('del_leftlogo' in found_controls,
            'Delete checkbox for left logo present in form')

        picture = load_file('data/test.gif')
        form.find_control('left_logo').add_file(picture,
                filename="left_logo.gif", content_type='image/gif')
        self.browser.clicked(form, self.browser.get_form_field(form, 'left_logo'))
        self.browser.submit()

        form = self.browser.get_form('frmAdd')
        expected_controls = set(['left_logo', 'right_logo', 'del_leftlogo'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser_do_logout()
