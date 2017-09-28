import re
import transaction
from unittest import TestSuite, makeSuite

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

def add_selection_list(portal, id, values):
    from Products.NaayaCore.PortletsTool.RefList import manage_addRefList
    manage_addRefList(portal.portal_portlets, id=id)
    for key, value in values.iteritems():
        portal.portal_portlets[id].manage_add_item(key, value)

class NyProjectFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.install_content_type('Naaya Project')
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.project.project_item import addNyProject
        from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyProject(self.portal.myfolder, id='myproject', title='My project', submitted=1, contributor='contributor')
        manage_addGlossaryCentre(self.portal, 'chm_terms')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder', 'chm_terms'])
        self.remove_content_type('Naaya Project')
        transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/project_add_html')
        self.failUnless('<h1>Submit Project</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'title:utf8:ustring', 'details:utf8:ustring', 'lang',
            'geo_location.lat:utf8:ustring', 'geo_location.lon:utf8:ustring',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'sample project'
        form['description:utf8:ustring'] = 'project description'

        self.browser.submit()
        html = self.browser.get_html()

        self.failUnless('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        project_id = (set(self.portal.myfolder.objectIds()) - set(['myproject'])).pop()
        self.browser.go('http://localhost/portal/myfolder/' + project_id)
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*sample project.*</h1>', html, re.DOTALL))

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/project_add_html')

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

        self.browser.go('http://localhost/portal/myfolder/myproject/edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My project')
        form['title:utf8:ustring'] = 'new_project_name'
        self.browser.clicked(form, form.find_control('title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myproject.title, 'new_project_name')

        html = self.browser.get_html()
        self.failUnless('<h1>Edit Project</h1>' in html)

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/myproject/edit_html')

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
        self.browser.go('http://localhost/portal/myfolder/projects_list')

        #Fail to find the unapproved project added
        form = self.browser.get_form('frmSearch')
        form['q'] = 'My project'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.assertTrue('My project</a></h3>' not in html)

        #Find the project after approval
        myproject = self.portal.myfolder.myproject
        myproject.approveThis()
        self.portal.recatalogNyObject(myproject)
        transaction.commit()

        form = self.browser.get_form('frmSearch')
        form['q'] = 'My project'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('My project</a></h3>' in html)

        #Fail to find a nonexistend string
        form = self.browser.get_form('frmSearch')
        form['q'] = 'No results'
        self.browser.clicked(form, form.find_control('search'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('No projects found for this query.' in html)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyProjectFunctionalTestCase))
    return suite
