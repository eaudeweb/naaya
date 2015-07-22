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

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyStoryFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaContent.NyStory.NyStory import addNyStory
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyStory(self.portal.myfolder, id='mystory', title='My story', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/info/story_add')
        self.failUnless('<h1>Submit Story</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_story'
        form['description:utf8:ustring'] = 'test_story_description'
        form['coverage:utf8:ustring'] = 'test_story_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'
        form['body:utf8:ustring'] = 'test_story_body'

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Thank you for your submission</h1>' in html)

        self.portal.info.teststory.approveThis()

        self.browser.go('http://localhost/portal/info/teststory')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_story.*</h1>', html, re.DOTALL))
        self.failUnless('test_story_description' in html)
        self.failUnless('test_story_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)
        self.failUnless('test_story_body' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/story_add')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mystory/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My story')

        form['title:utf8:ustring'] = 'new_story_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mystory.title, 'new_story_title')

        self.browser.go('http://localhost/portal/myfolder/mystory/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mystory.title, 'new_story_title')
        self.failUnlessEqual(self.portal.myfolder.mystory.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mystory/edit_html')

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

        self.browser.go('http://localhost/portal/myfolder/mystory/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My story')
        form['title:utf8:ustring'] = 'new_story_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mystory.title, 'new_story_title')

        self.browser_do_logout()

class NyStoryVersioningFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """
    def afterSetUp(self):
        from Products.NaayaContent.NyStory.NyStory import addNyStory
        addNyStory(self.portal.info, id='ver_story', title='ver_story', submitted=1)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['ver_story'])
        import transaction; transaction.commit()

    def test_start_version(self):
        from Products.NaayaContent.NyStory.story_item import story_item
        self.browser_do_login('admin', '')
        self.failUnlessEqual(self.portal.info.ver_story.version, None)
        self.browser.go('http://localhost/portal/info/ver_story/startVersion')
        self.failUnless(isinstance(self.portal.info.ver_story.version, story_item))
        self.browser_do_logout()

    def test_edit_version(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/ver_story/startVersion')

        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'ver_story_newtitle'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        ver_story = self.portal.info.ver_story
        self.failUnlessEqual(ver_story.title, 'ver_story')
        # we can't do ver_story.version.title because version objects don't have the _languages property
        self.failUnlessEqual(ver_story.version.getLocalProperty('title', 'en'), 'ver_story_newtitle')

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyStoryFunctionalTestCase))
    suite.addTest(makeSuite(NyStoryVersioningFunctionalTestCase))
    return suite
