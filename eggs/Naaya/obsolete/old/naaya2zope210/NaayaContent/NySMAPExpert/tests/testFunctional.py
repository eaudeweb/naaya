# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

import re
from unittest import TestSuite, makeSuite
from StringIO import StringIO

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

def add_zodb_script(portal, script_id, params='', body=''):
    from Products.PythonScripts.PythonScript import manage_addPythonScript
    manage_addPythonScript(portal, id=script_id)
    portal[script_id].ZPythonScript_edit(params, body)

def add_selection_list(portal, id, values):
    from Products.NaayaCore.PortletsTool.RefList import manage_addRefList
    manage_addRefList(portal.portal_portlets, id=id)
    for key, value in values.iteritems():
        portal.portal_portlets[id].manage_add_item(key, value)

def setUp_EW_test_data(portal):
    add_zodb_script(portal, 'checkSessionSubTopics', 'maintopic, subtopic, session',
        'for sb in container.utConvertToList(session):\n'
        '  if sb == "%s|@|%s" % (maintopic, subtopic):\n'
        '    return True\n'
        'return False\n')
    add_zodb_script(portal, 'getCountriesList', '',
        'values = ["Egypt", "Lybia", "Tunisia"]\n'
        'class item: id = ""; title = ""\n'
        'def mk_item(id, title): d = item(); d.id = id; d.title = title; return d\n'
        'return list(mk_item(id=v, title=v) for v in values)\n')
    add_zodb_script(portal, 'getExpFocusesTypesList', 'priority_id',
        'id = str(priority_id)[:3]\n'
        'values = ["Focus1"+id, "Focus2"+id, "Focus3"+id]\n'
        'class item: id = ""; title = ""\n'
        'def mk_item(id, title): d = item(); d.id = id; d.title = title; return d\n'
        'return list(mk_item(id=v, title=v) for v in values)\n')
    add_zodb_script(portal, 'getExpPrioritiesTypesList', '',
        'values = ["Biodiversity", "Desertification", "Polluted Areas"]\n'
        'class item: id = ""; title = ""\n'
        'def mk_item(id, title): d = item(); d.id = id; d.title = title; return d\n'
        'return list(mk_item(id=v, title=v) for v in values)\n')
    add_zodb_script(portal, 'getExpFocusTitle', 'focus_id, priority_area_id',
        'focus_list_id = "focuses_%s_exp" % priority_area_id[:3]\n'
        'try:\n'
        '    return context.getPortletsTool().getRefListById(focus_list_id.lower()).get_item(focus_id).title\n'
        'except:\n'
        '    return ""\n')
    add_zodb_script(portal, 'getCountryName', 'id', 'return id\n')
    add_zodb_script(portal, 'getExpPriorityTitle', 'id',
        'try:\n'
        '    return context.getPortletsTool().getRefListById("priorities_types_exp").get_item(id).title\n'
        'except:\n'
        '    return ""\n')
    add_zodb_script(portal, 'getSessionMainTopics', 'topic',
        'return [x.split("|@|")[0] for x in container.utConvertToList(topic)]\n')
    add_zodb_script(portal, 'getPrioritiesTypesList', '',
        'return context.getPortletsTool().getRefListById("priorities_types").get_list()\n')
    add_zodb_script(portal, 'getFocusesTypesList', 'priority_id',
        'id = str(priority_id)[:3]\n'
        'values = ["Biodiversity", "Desertification", "Polluted Areas"]\n'
        'class item: id = ""; title = ""\n'
        'def mk_item(id, title): d = item(); d.id = id; d.title = title; return d\n'
        'return list(mk_item(id=v, title=v) for v in values)\n')
    add_zodb_script(portal, 'getPriorityTitle', 'id',
        'try:\n'
        '    return self.getPortletsTool().getRefListById("priorities_types").get_item(id).title\n'
        'except:\n'
        '    return ""\n')
    add_zodb_script(portal, 'getFocusTitle', 'id',
        'return "[focus title]"\n')

    add_selection_list(portal, 'countries',
        dict((k,k) for k in ["Egypt", "Lybia", "Tunisia"]))
    add_selection_list(portal, 'priorities_types_exp',
        dict((k,k) for k in ["Biodiversity", "Desertification", "Polluted Areas"]))
    add_selection_list(portal, 'priorities_types',
        dict((k,k) for k in ["Biodiversity", "Desertification", "Polluted Areas"]))


def tearDown_EW_test_data(portal):
    portal.manage_delObjects(['checkSessionSubTopics', 'getCountriesList',
        'getExpFocusesTypesList', 'getExpPrioritiesTypesList', 'getExpFocusTitle',
        'getCountryName', 'getExpPriorityTitle', 'getSessionMainTopics',
        'getPrioritiesTypesList', 'getFocusesTypesList', 'getPriorityTitle',
        'getFocusTitle'])

    portal.portal_portlets.manage_delObjects(['countries', 'priorities_types_exp',
        'priorities_types'])

class NySMAPExpertFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.install_content_type('Naaya SMAP Expert')
        setUp_EW_test_data(self.portal)
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaContent.NySMAPExpert.NySMAPExpert import addNySMAPExpert
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNySMAPExpert(self.portal.myfolder, id='myexpert', name='My expert',
            surname='Knowitall', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        tearDown_EW_test_data(self.portal)
        self.remove_content_type('Naaya SMAP Expert')
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/expert_add_html')
        self.failUnless('<h1>Submit Expert</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'name:utf8:ustring', 'ref_lang:utf8:ustring', 'country:utf8:ustring',
            'subtopics:list', 'file', 'email:utf8:ustring', 'surname:utf8:ustring'
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'name'))
        form['name:utf8:ustring'] = 'mister expert'
        form['surname:utf8:ustring'] = 'knowitall'
        form['email:utf8:ustring'] = 'expert@example.com'

        TEST_FILE_DATA = 'some data for my data file'
        form.find_control('file').add_file(StringIO(TEST_FILE_DATA),
            filename='testcreatefile.txt', content_type='text/plain')

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Thank you for your submission</h1>' in html)

        expert_id = (set(self.portal.myfolder.objectIds()) - set(['myexpert'])).pop()
        self.portal.myfolder[expert_id].approveThis()

        self.browser.go('http://localhost/portal/myfolder/' + expert_id)
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*mister expert.*</h1>', html, re.DOTALL))
        self.failUnless('expert@example.com' in html)

        self.browser.go('http://localhost/portal/myfolder/%s/download' % expert_id)
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            "attachment; filename*=utf-8''testcreatefile.txt")
        self.failUnlessEqual(html, TEST_FILE_DATA)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/expert_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'name'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Name"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myexpert/edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['name:utf8:ustring'], 'My expert')
        form['name:utf8:ustring'] = 'new_expert_name'
        form['surname:utf8:ustring'] = 'his_surname'
        self.browser.clicked(form, form.find_control('saveProperties:method'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myexpert.name, 'new_expert_name')

        html = self.browser.get_html()
        self.failUnless('<h1>Edit Expert</h1>' in html)
        form = self.browser.get_form('frmEdit')
        TEST_FILE_DATA_2 = 'some new data for my file'
        form.find_control('file').add_file(StringIO(TEST_FILE_DATA_2),
            filename='the_new_file.txt', content_type='text/plain')
        self.browser.clicked(form, form.find_control('saveUpload:method'))
        self.browser.submit()

        self.browser.go('http://localhost/portal/myfolder/myexpert/download')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            "attachment; filename*=utf-8''the_new_file.txt")
        self.failUnlessEqual(html, TEST_FILE_DATA_2)

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/myexpert/edit_html')

        form = self.browser.get_form('frmEdit')
        form['name:utf8:ustring'] = ''
        self.browser.clicked(form, form.find_control('saveProperties:method'))
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Name"' in html)

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NySMAPExpertFunctionalTestCase))
    return suite
