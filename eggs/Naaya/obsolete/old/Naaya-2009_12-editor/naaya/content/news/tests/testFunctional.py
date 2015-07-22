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
from BeautifulSoup import BeautifulSoup

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class NyNewsFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.news.news_item import addNyNews
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyNews(self.portal.myfolder, id='mynews', title='My news', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/info/news_add_html')
        self.failUnless('<h1>Submit News</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_news'
        form['description:utf8:ustring'] = 'test_news_description'
        form['coverage:utf8:ustring'] = 'test_news_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'
        form['details:utf8:ustring'] = 'test_news_details'

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('The administrator will analyze your request and you will be notified about the result shortly.' in html)

        self.portal.info.testnews.approveThis()

        self.browser.go('http://localhost/portal/info/testnews')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_news.*</h1>', html, re.DOTALL))
        self.failUnless('test_news_description' in html)
        self.failUnless('test_news_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)
        self.failUnless('test_news_details' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/news_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mynews/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My news')

        form['title:utf8:ustring'] = 'new_news_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mynews.title, 'new_news_title')

        self.browser.go('http://localhost/portal/myfolder/mynews/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mynews.title, 'new_news_title')
        self.failUnlessEqual(self.portal.myfolder.mynews.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mynews/edit_html')

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

        self.browser.go('http://localhost/portal/myfolder/mynews/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My news')
        form['title:utf8:ustring'] = 'new_news_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.mynews.title, 'new_news_title')

        self.browser_do_logout()

    def test_view_in_folder(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder')
        html = self.browser.get_html()
        soup = BeautifulSoup(html)

        tables = soup.findAll('table', id='folderfile_list')
        self.assertTrue(len(tables) == 1)

        links_to_news = tables[0].findAll('a', attrs={'href': 'http://localhost/portal/myfolder/mynews'})
        self.assertTrue(len(links_to_news) == 1)
        self.assertTrue(links_to_news[0].string == 'My news')

        self.browser_do_logout()

class NyNewsVersioningFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """
    def afterSetUp(self):
        from naaya.content.news.news_item import addNyNews
        addNyNews(self.portal.info, id='ver_news', title='ver_news', submitted=1)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['ver_news'])
        import transaction; transaction.commit()

    def test_start_version(self):
        from naaya.content.news.news_item import news_item
        self.browser_do_login('admin', '')
        self.failUnlessEqual(self.portal.info.ver_news.version, None)
        self.browser.go('http://localhost/portal/info/ver_news/startVersion')
        self.failUnless(isinstance(self.portal.info.ver_news.version, news_item))
        self.browser_do_logout()

    def test_edit_version(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/ver_news/startVersion')

        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'ver_news_newtitle'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        ver_news = self.portal.info.ver_news
        self.failUnlessEqual(ver_news.title, 'ver_news')
        # we can't do ver_news.version.title because version objects don't have the _languages property
        self.failUnlessEqual(ver_news.version.getLocalProperty('title', 'en'), 'ver_news_newtitle')

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyNewsFunctionalTestCase))
    suite.addTest(makeSuite(NyNewsVersioningFunctionalTestCase))
    return suite
