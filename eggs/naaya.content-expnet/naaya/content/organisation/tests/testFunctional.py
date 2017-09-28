import re
import transaction
from unittest import TestSuite, makeSuite

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

def add_selection_list(portal, id, values):
    from Products.NaayaCore.PortletsTool.RefList import manage_addRefList
    manage_addRefList(portal.portal_portlets, id=id)
    for key, value in values.iteritems():
        portal.portal_portlets[id].manage_add_item(key, value)

def setUp_EW_data(portal):
    add_selection_list(portal, 'countries',
        dict((k,k) for k in ["Egypt", "Lybia", "Tunisia"]))

def tearDown_EW_data(portal):
    portal.portal_portlets.manage_delObjects(['countries'])

class NyOrganisationFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.install_content_type('Naaya Organisation')
        setUp_EW_data(self.portal)
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.organisation.organisation_item import addNyOrganisation
        from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyOrganisation(self.portal.myfolder, id='myorganisation', title="My Organisation",
                        submitted=1, contributor='contributor')
        manage_addGlossaryCentre(self.portal, 'chm_terms')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder', 'chm_terms'])
        tearDown_EW_data(self.portal)
        self.remove_content_type('Naaya Organisation')
        transaction.commit()

    def test_add(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/organisation_add_html')
        self.failUnless('<h1>Submit Organisation</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')

        self.failUnlessEqual(form['sortorder:utf8:ustring'], '100')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'My New Organisation'

        self.browser.submit()
        html = self.browser.get_html()

        self.failUnless('Item added' in html)

        organisation_id = (set(self.portal.myfolder.objectIds()) - set(['myorganisation'])).pop()
        self.browser.go('http://localhost/portal/myfolder/' + organisation_id)
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*My New Organisation.*</h1>', html, re.DOTALL))

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/organisation_add_html')

        #The object should not be added if the mandatory fields are not all filled
        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myorganisation/edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My Organisation')
        form['title:utf8:ustring'] = 'New Organisation Name'
        self.browser.clicked(form, form.find_control('title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myorganisation.title, 'New Organisation Name')

        html = self.browser.get_html()
        self.failUnless('<h1>Edit Organisation</h1>' in html)

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/myorganisation/edit_html')

        #The object properties should not be saved if the mandatory fields are not all filled
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = ''
        self.browser.clicked(form, form.find_control('title:utf8:ustring'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_search(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/organisations_list')

        #Fail to find the unapproved organisation added
        form = self.browser.get_form('frmSearch')
        form['q'] = 'My Organisation'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('My Organisation</a></h3>' not in html)

        #Find the organisation after approval
        myorganisation = self.portal.myfolder.myorganisation
        myorganisation.approveThis()
        self.portal.recatalogNyObject(myorganisation)
        transaction.commit()

        form = self.browser.get_form('frmSearch')
        form['q'] = 'My Organisation'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('My Organisation</a></h3>' in html)

        #Fail to find a nonexistend string
        form = self.browser.get_form('frmSearch')
        form['q'] = 'No results'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('No organisations found for this query.' in html)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyOrganisationFunctionalTestCase))
    return suite
