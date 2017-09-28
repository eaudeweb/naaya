import re
from copy import deepcopy

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class PublicationMixin(object):
    """ testing mix-in that installs the Naaya Publication content type """

    publication_metatype = 'Naaya Publication'
    publication_permission = 'Naaya - Add Naaya Publication objects'

    def publication_install(self):
        self.portal.manage_install_pluggableitem(self.publication_metatype)

    def publication_uninstall(self):
        self.portal.manage_uninstall_pluggableitem(self.publication_metatype)


class NyPublicationFunctionalTestCase(NaayaFunctionalTestCase, PublicationMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.publication_install()
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaContent.NyPublication.NyPublication import addNyPublication
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyPublication(self.portal.myfolder, id='mypublication', title='My publication',
            locator='http://www.eaudeweb.ro', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.publication_uninstall()
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/publication_add_html')
        self.failUnless('<h1>Submit Publication</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'locator:utf8:ustring',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.failUnlessEqual(form['sortorder:utf8:ustring'], '100')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_publication'
        form['description:utf8:ustring'] = 'test_publication_description'
        form['coverage:utf8:ustring'] = 'test_publication_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'
        form['locator:utf8:ustring'] = 'http://www.eaudeweb.ro'
        form['original_title:utf8:ustring'] = 'test_publication_original'

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Thank you for your submission</h1>' in html)

        self.portal.myfolder.test_publication.approveThis()

        self.browser.go('http://localhost/portal/myfolder/test_publication')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_publication.*</h1>', html, re.DOTALL))
        self.failUnless('test_publication_description' in html)
        self.failUnless('test_publication_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)
        self.failUnless('http://www.eaudeweb.ro' in html)
        self.failUnless('test_publication_original' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/publication_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mypublication/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My publication')

        form['title:utf8:ustring'] = 'new_publication_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mypublication.title, 'new_publication_title')

        self.browser.go('http://localhost/portal/myfolder/mypublication/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        form['locator:utf8:ustring'] = 'http://www.eaudeweb.ro/?lang=fr'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mypublication.title, 'new_publication_title')
        self.failUnlessEqual(self.portal.myfolder.mypublication.locator, 'http://www.eaudeweb.ro')
        self.failUnlessEqual(self.portal.myfolder.mypublication.getLocalProperty('title', 'fr'), 'french_title')
        self.failUnlessEqual(self.portal.myfolder.mypublication.getLocalProperty('locator', 'fr'), 'http://www.eaudeweb.ro/?lang=fr')

        self.browser_do_logout()

    def test_edit_error(self):
        return # this test is disabled
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mypublication/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        form['title:utf8:ustring'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_manage(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mypublication/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My publication')
        form['title:utf8:ustring'] = 'new_publication_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mypublication.title, 'new_publication_title')

        self.browser_do_logout()

