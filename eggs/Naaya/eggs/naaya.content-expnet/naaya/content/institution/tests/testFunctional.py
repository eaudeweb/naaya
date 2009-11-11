import re
import transaction
from unittest import TestSuite, makeSuite

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

def add_selection_list(portal, id, values):
    from Products.NaayaCore.PortletsTool.RefList import manage_addRefList
    manage_addRefList(portal.portal_portlets, id=id)
    for key, value in values.iteritems():
        portal.portal_portlets[id].manage_add_item(key, value)

def setUp_EW_test_data(portal):
    add_selection_list(portal, 'countries',
        dict((k,k) for k in ["Egypt", "Lybia", "Tunisia"]))

def tearDown_EW_test_data(portal):
    portal.portal_portlets.manage_delObjects(['countries'])

class NyInstitutionFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.install_content_type('Naaya Institution')
        setUp_EW_test_data(self.portal)
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.institution.institution_item import addNyInstitution
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyInstitution(self.portal.myfolder, id='myinstitution', title="My Institution",
                        submitted=1, contributor='contributor')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        tearDown_EW_test_data(self.portal)
        self.remove_content_type('Naaya Institution')
        transaction.commit()

    def test_add(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/institution_add_html')
        self.failUnless('<h1>Submit Institution</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')

        self.failUnlessEqual(form['sortorder:utf8:ustring'], '100')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'My New Institution'

        self.browser.submit()
        html = self.browser.get_html()

        self.failUnless('Item added' in html)

        institution_id = (set(self.portal.myfolder.objectIds()) - set(['myinstitution'])).pop()
        self.portal.myfolder[institution_id].approveThis()

        self.browser.go('http://localhost/portal/myfolder/' + institution_id)
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*My New Institution.*</h1>', html, re.DOTALL))

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/institution_add_html')

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

        self.browser.go('http://localhost/portal/myfolder/myinstitution/edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My Institution')
        form['title:utf8:ustring'] = 'New Institution Name'
        self.browser.clicked(form, form.find_control('saveProperties:method'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myinstitution.title, 'New Institution Name')

        html = self.browser.get_html()
        self.failUnless('<h1>Edit Institution</h1>' in html)

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/myinstitution/edit_html')

        #The object properties should not be saved if the mandatory fields are not all filled
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = ''
        self.browser.clicked(form, form.find_control('saveProperties:method'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_search(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/institutions_list')

        #Find the institution added
        form = self.browser.get_form('frmSearch')
        form['q'] = 'My Institution'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('My Institution</a></h4>' in html)

        #Fail to find a nonexistend string
        form = self.browser.get_form('frmSearch')
        form['q'] = 'No results'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('No institutions found for this query.' in html)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyInstitutionFunctionalTestCase))
    return suite
