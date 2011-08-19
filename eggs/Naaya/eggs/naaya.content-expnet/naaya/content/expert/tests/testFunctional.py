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

class NyExpertFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.install_content_type('Naaya Expert')
        setUp_EW_data(self.portal)
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.expert.expert_item import addNyExpert
        from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyExpert(self.portal.myfolder, id='myexpert', name='My expert',
            surname='Knowitall', submitted=1, contributor='contributor')
        manage_addGlossaryCentre(self.portal, 'chm_terms')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder', 'chm_terms'])
        tearDown_EW_data(self.portal)
        self.remove_content_type('Naaya Expert')
        transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/expert_add_html')
        self.failUnless('<h1>Submit Expert</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'name:utf8:ustring', 'surname:utf8:ustring', 'lang',
            'sortorder:utf8:ustring', 'email:utf8:ustring','instant_messaging:utf8:ustring',
            'ref_lang:utf8:ustring', 'phone:utf8:ustring','mobile:utf8:ustring',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.failUnlessEqual(form['sortorder:utf8:ustring'], '100')

        self.browser.clicked(form, self.browser.get_form_field(form, 'name'))
        form['name:utf8:ustring'] = 'mister expert'
        form['surname:utf8:ustring'] = 'knowitall'
        form['email:utf8:ustring'] = 'expert@example.com'

        self.browser.submit()
        html = self.browser.get_html()

        self.failUnless('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        expert_id = (set(self.portal.myfolder.objectIds()) - set(['myexpert'])).pop()
        self.browser.go('http://localhost/portal/myfolder/' + expert_id)
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*mister expert.*</h1>', html, re.DOTALL))
        self.failUnless('expert at example.com' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/expert_add_html')

        #The object should not be added if the mandatory fields are not all filled
        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'name'))
        form['name:utf8:ustring'] = 'mister expert'
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Surname"' in html)

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'name'))
        form['surname:utf8:ustring'] = 'knowitall'
        form['name:utf8:ustring'] = ''
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Name"' in html)

        self.browser_do_logout()

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myexpert/edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['name:utf8:ustring'], 'My expert')
        form['name:utf8:ustring'] = 'new_expert_name'
        form['surname:utf8:ustring'] = 'his_surname'
        self.browser.clicked(form, form.find_control('name:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myexpert.name, 'new_expert_name')

        html = self.browser.get_html()
        self.failUnless('<h1>Edit Expert</h1>' in html)

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/myexpert/edit_html')

        #The object properties should not be saved if the mandatory fields are not all filled
        form = self.browser.get_form('frmEdit')
        form['name:utf8:ustring'] = ''
        self.browser.clicked(form, form.find_control('name:utf8:ustring'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Name"' in html)

        form = self.browser.get_form('frmEdit')
        form['name:utf8:ustring'] = 'new_expert_name'
        form['surname:utf8:ustring'] = ''
        self.browser.clicked(form, form.find_control('name:utf8:ustring'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Surname"' in html)

        self.browser_do_logout()

    def test_search(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/experts_list')

        #Fail to find a nonexistend string
        form = self.browser.get_form('frmSearch')
        form['q'] = 'No results'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('No experts found for this query.' in html)

        #Find the expert after approval
        myexpert = self.portal.myfolder.myexpert
        myexpert.approveThis()
        self.portal.recatalogNyObject(myexpert)
        transaction.commit()

        form = self.browser.get_form('frmSearch')
        form['q'] = 'Knowitall'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('My expert Knowitall</a></h3>' in html)

        #Find the expert added
        form = self.browser.get_form('frmSearch')
        form['q'] = 'Knowitall'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('My expert Knowitall</a></h3>' in html)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyExpertFunctionalTestCase))
    return suite
