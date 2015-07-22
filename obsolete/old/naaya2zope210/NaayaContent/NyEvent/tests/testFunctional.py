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

class NyEventFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        from Products.Naaya.NyFolder import addNyFolder
        from Products.NaayaContent.NyEvent.NyEvent import addNyEvent
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyEvent(self.portal.myfolder, id='myevent', title='My event', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/info/event_add_html')
        self.failUnless('<h1>Submit Event</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'test_event'
        form['description:utf8:ustring'] = 'test_event_description'
        form['coverage:utf8:ustring'] = 'test_event_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'
        form['details:utf8:ustring'] = 'test_event_details'

        event_types = form.find_control('event_type:utf8:ustring').get_items()[1:]
        labels = set(map(lambda e: e.get_labels()[0].text, event_types))
        ids = set(map(lambda e: e.name, event_types))
        self.failUnlessEqual(labels, set(['Conference', 'Other', 'Meeting', 'Event']))
        self.failUnlessEqual(ids, set(['conference', 'other', 'meeting', 'event']))

        form['event_type:utf8:ustring'] = ['conference']

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Thank you for your submission</h1>' in html)

        self.failUnlessEqual(self.portal.info.testevent.event_type, 'conference')
        self.portal.info.testevent.approveThis()

        self.browser.go('http://localhost/portal/info/testevent')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*test_event.*</h1>', html, re.DOTALL))
        self.failUnless('test_event_description' in html)
        self.failUnless('test_event_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)
        self.failUnless('test_event_details' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/event_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/myevent/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My event')

        form['title:utf8:ustring'] = 'new_event_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myevent.title, 'new_event_title')

        self.browser.go('http://localhost/portal/myfolder/myevent/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myevent.title, 'new_event_title')
        self.failUnlessEqual(self.portal.myfolder.myevent.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/myevent/edit_html')

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

        self.browser.go('http://localhost/portal/myfolder/myevent/manage_edit_html')
        form = self.browser.get_form('frmEdit')
        self.failUnlessEqual(form['title:utf8:ustring'], 'My event')
        form['title:utf8:ustring'] = 'new_event_title'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.failUnlessEqual(self.portal.myfolder.myevent.title, 'new_event_title')

        self.browser_do_logout()

class NyEventVersioningFunctionalTestCase(NaayaFunctionalTestCase):
    """ TestCase for NaayaContent object """
    def afterSetUp(self):
        from Products.NaayaContent.NyEvent.NyEvent import addNyEvent
        addNyEvent(self.portal.info, id='ver_event', title='ver_event', submitted=1)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['ver_event'])
        import transaction; transaction.commit()

    def test_start_version(self):
        from Products.NaayaContent.NyEvent.event_item import event_item
        self.browser_do_login('admin', '')
        self.failUnlessEqual(self.portal.info.ver_event.version, None)
        self.browser.go('http://localhost/portal/info/ver_event/startVersion')
        self.failUnless(isinstance(self.portal.info.ver_event.version, event_item))
        self.browser_do_logout()

    def test_edit_version(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/ver_event/startVersion')

        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'ver_event_newtitle'
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        ver_event = self.portal.info.ver_event
        self.failUnlessEqual(ver_event.title, 'ver_event')
        # we can't do ver_event.version.title because version objects don't have the _languages property
        self.failUnlessEqual(ver_event.version.getLocalProperty('title', 'en'), 'ver_event_newtitle')

        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyEventFunctionalTestCase))
    suite.addTest(makeSuite(NyEventVersioningFunctionalTestCase))
    return suite
