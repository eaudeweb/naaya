#Python imports
from unittest import TestSuite, makeSuite

#Zope imports
from Testing import ZopeTestCase

#Naaya imports
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaSurvey.SurveyTool import manage_addSurveyTool, SurveyTool
from Products.NaayaSurvey.MegaSurvey import manage_addMegaSurvey

#Meeting imports
from naaya.content.meeting import PARTICIPANT_ROLE

def addPortalMeetingParticipant(portal):
    portal.acl_users._doAddUser('test_participant', 'participant', [], '', '', '', '')

def removePortalMeetingParticipant(portal):
    portal.acl_users._doDelUsers(['test_participant'])

class NyMeetingCreateTestCase(NaayaFunctionalTestCase):
    """ CreateTestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        self.portal.myfolder.approveThis()
        self.portal.myfolder.folder_meta_types.append('Naaya Meeting')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_add(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/meeting_add_html')
        self.assertTrue('<h1>Submit Meeting</h1>' in self.browser.get_html())

        form = self.browser.get_form('frmAdd')
        expected_controls = set(['title:utf8:ustring', 'geo_location.address:utf8:ustring',
            'releasedate', 'start_date', 'end_date',
            'agenda_pointer:utf8:ustring', 'minutes_pointer:utf8:ustring', 'survey_pointer:utf8:ustring',
            'contact_person:utf8:ustring', 'contact_email:utf8:ustring'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls, 
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'MyMeeting'
        form['geo_location.address:utf8:ustring'] = 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark'
        form['releasedate'] = '16/06/2010'
        form['start_date'] = '20/06/2010'
        form['end_date'] = '25/06/2010'
        form['contact_person:utf8:ustring'] = 'My Name'
        form['contact_email:utf8:ustring'] = 'my.email@my.domain'
        self.browser.submit()
        self.assertTrue(hasattr(self.portal.myfolder, 'mymeeting'))

        self.portal.myfolder.mymeeting.approveThis()
        self.browser.go('http://localhost/portal/myfolder/mymeeting')
        html = self.browser.get_html()
        self.assertTrue('MyMeeting' in html)
        self.assertTrue('[20/06/2010 - 25/06/2010]' in html)
        self.assertTrue('My Name' in html)
        self.assertTrue('mailto:my.email@my.domain' in html)
        self.assertTrue('http://localhost/portal/myfolder/mymeeting/get_ics' in html)
        self.assertTrue('16/06/2010' in html)
        self.assertTrue('admin' in html)
        self.assertTrue('Kogens Nytorv 6, 1050 Copenhagen K, Denmark' in html)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/meeting_add_html')
        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()
        self.assertTrue('The form contains errors' in self.browser.get_html())
        self.assertTrue('Value required for' in self.browser.get_html())

        self.browser_do_logout()

    def test_manage_add(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/manage_addProduct/Naaya/manage_addNyMeeting')
        self.assertTrue('Add Naaya Meeting' in self.browser.get_html())

        form = self.browser.get_form('frmAdd')
        expected_controls = set(['title:utf8:ustring', 'geo_location.address:utf8:ustring',
            'releasedate', 'start_date', 'end_date',
            'agenda_pointer:utf8:ustring', 'minutes_pointer:utf8:ustring', 'survey_pointer:utf8:ustring',
            'contact_person:utf8:ustring', 'contact_email:utf8:ustring'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls, 
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'MyMeeting2'
        form['geo_location.address:utf8:ustring'] = 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark'
        form['releasedate'] = '16/06/2010'
        form['start_date'] = '20/06/2010'
        form['end_date'] = '25/06/2010'
        form['contact_person:utf8:ustring'] = 'My Name'
        form['contact_email:utf8:ustring'] = 'my.email@my.domain'
        self.browser.submit()
        self.assertTrue(hasattr(self.portal.myfolder, 'mymeeting2'))

        self.browser.go('http://localhost/portal/myfolder/mymeeting2')
        html = self.browser.get_html()
        self.assertTrue('MyMeeting2' in html)
        self.assertTrue('[20/06/2010 - 25/06/2010]' in html)
        self.assertTrue('My Name' in html)
        self.assertTrue('mailto:my.email@my.domain' in html)
        self.assertTrue('http://localhost/portal/myfolder/mymeeting2/get_ics' in html)
        self.assertTrue('16/06/2010' in html)
        self.assertTrue('admin' in html)
        self.assertTrue('Kogens Nytorv 6, 1050 Copenhagen K, Denmark' in html)

        self.browser_do_logout()


class NyMeetingEditingTestCase(NaayaFunctionalTestCase):
    """ EditingTestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        location = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark'}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting',
            releasedate='16/06/2010', start_date='20/06/2010', end_date='25/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain', **location)
        addNyMeeting(self.portal.info, 'mymeeting2', contributor='contributor', submitted=1,
            title='MyMeeting',
            releasedate='16/06/2010', start_date='20/06/2010', end_date='25/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain', **location)
        self.portal.info.mymeeting.approveThis()
        self.portal.info.mymeeting2.approveThis()
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['mymeeting', 'mymeeting2'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_edit(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))
        
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        self.assertTrue('<h1>Edit Meeting</h1>' in self.browser.get_html())

        form = self.browser.get_form('frmEdit')
        self.assertEqual(form['title:utf8:ustring'], 'MyMeeting')
        self.assertEqual(form['geo_location.address:utf8:ustring'], 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark')
        self.assertEqual(form['releasedate'], '16/06/2010')
        self.assertEqual(form['start_date'], '20/06/2010')
        self.assertEqual(form['end_date'], '25/06/2010')
        self.assertEqual(form['contact_person:utf8:ustring'], 'My Name')
        self.assertEqual(form['contact_email:utf8:ustring'], 'my.email@my.domain')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'MyEditedMeeting'
        form['geo_location.address:utf8:ustring'] = 'Kogens Nytorv 8, 1050 Copenhagen K, Denmark'
        form['releasedate'] = '17/06/2010'
        form['start_date'] = '21/06/2010'
        form['end_date'] = '26/06/2010'
        form['contact_person:utf8:ustring'] = 'My Edited Name'
        form['contact_email:utf8:ustring'] = 'my.edited.email@my.domain'
        self.browser.submit()
        self.browser.go('http://localhost/portal/info/mymeeting')
        html = self.browser.get_html()
        self.assertTrue('MyEditedMeeting' in html)
        self.assertTrue('[21/06/2010 - 26/06/2010]' in html)
        self.assertTrue('My Edited Name' in html)
        self.assertTrue('mailto:my.edited.email@my.domain' in html)
        self.assertTrue('http://localhost/portal/info/mymeeting/get_ics' in html)
        self.assertTrue('17/06/2010' in html)
        self.assertTrue('contributor' in html)
        self.assertTrue('Kogens Nytorv 8, 1050 Copenhagen K, Denmark' in html)

        self.browser_do_logout()

    def test_edit_error(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))
        
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        form['title:utf8:ustring'] = ''
        self.browser.submit()
        html = self.browser.get_html()
        self.assertTrue('The form contains errors' in html)
        self.assertTrue('Value required for "Title"' in html)

        self.browser_do_logout()

    def test_manage_edit(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting2'))
        
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting2/manage_edit_html')
        self.assertTrue('Naaya Meeting' in self.browser.get_html())

        form = self.browser.get_form('frmEdit')
        self.assertEqual(form['title:utf8:ustring'], 'MyMeeting')
        self.assertEqual(form['geo_location.address:utf8:ustring'], 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark')
        self.assertEqual(form['releasedate'], '16/06/2010')
        self.assertEqual(form['start_date'], '20/06/2010')
        self.assertEqual(form['end_date'], '25/06/2010')
        self.assertEqual(form['contact_person:utf8:ustring'], 'My Name')
        self.assertEqual(form['contact_email:utf8:ustring'], 'my.email@my.domain')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'MyEditedMeeting'
        form['geo_location.address:utf8:ustring'] = 'Kogens Nytorv 8, 1050 Copenhagen K, Denmark'
        form['releasedate'] = '17/06/2010'
        form['start_date'] = '21/06/2010'
        form['end_date'] = '26/06/2010'
        form['contact_person:utf8:ustring'] = 'My Edited Name'
        form['contact_email:utf8:ustring'] = 'my.edited.email@my.domain'
        self.browser.submit()
        self.browser.go('http://localhost/portal/info/mymeeting2')
        html = self.browser.get_html()
        self.assertTrue('MyEditedMeeting' in html)
        self.assertTrue('[21/06/2010 - 26/06/2010]' in html)
        self.assertTrue('My Edited Name' in html)
        self.assertTrue('mailto:my.edited.email@my.domain' in html)
        self.assertTrue('http://localhost/portal/info/mymeeting2/get_ics' in html)
        self.assertTrue('17/06/2010' in html)
        self.assertTrue('contributor' in html)
        self.assertTrue('Kogens Nytorv 8, 1050 Copenhagen K, Denmark' in html)

        self.browser_do_logout()


class NyMeetingFunctionalTestCase(NaayaFunctionalTestCase):
    """ FunctionalTestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        location = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark'}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting',
            releasedate='16/06/2010', start_date='20/06/2010', end_date='25/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain', **location)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)
        addPortalMeetingParticipant(self.portal)
        self.portal.info.mymeeting.participants._add_user('test_participant')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        removePortalMeetingParticipant(self.portal)
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_index(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))

        self.browser_do_login('test_participant', 'participant')
        self.browser.go('http://localhost/portal/info/mymeeting')
        html = self.browser.get_html()
        self.assertTrue('MyMeeting' in html)
        self.assertTrue('[20/06/2010 - 25/06/2010]' in html)
        self.assertTrue('My Name' in html)
        self.assertTrue('mailto:my.email@my.domain' in html)
        self.assertTrue('http://localhost/portal/info/mymeeting/get_ics' in html)
        self.assertTrue('16/06/2010' in html)
        self.assertTrue('contributor' in html)
        self.assertTrue('Kogens Nytorv 6, 1050 Copenhagen K, Denmark' in html)

        self.browser_do_logout()

    def test_feed(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))

        self.browser_do_login('test_participant', 'participant')
        self.browser.go('http://localhost/portal/portal_syndication/latestuploads_rdf')
        html = self.browser.get_html()
        self.assertTrue('MyMeeting' in html)
        self.assertTrue('http://localhost/portal/info/mymeeting' in html)
        self.assertTrue('Kogens Nytorv 6, 1050 Copenhagen K, Denmark' in html)
        self.assertTrue('My Name' in html)

        self.browser_do_logout()

    def test_search_for_new_participants(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertTrue('http://localhost/portal/info/mymeeting/participants' in self.browser.get_html())

        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formSearchUsers')
        expected_controls = set(['search_param', 'search_term:utf8:ustring', 'search_user'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'search_term:utf8:ustring'))
        form['search_param'] = ['uid']
        form['search_term:utf8:ustring'] = 'contributor'
        self.browser.submit()

        form = self.browser.get_form('formAddUsers')
        expected_controls = set(['uids:list', 'add_users'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser_do_logout()

    def test_newsletter_page(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertTrue('http://localhost/portal/info/mymeeting/newsletter_html' in self.browser.get_html())

        self.browser.go('http://localhost/portal/info/mymeeting/newsletter_html')
        form = self.browser.get_form('formSendNewsletter')
        expected_controls = set(['subject:utf8:ustring', 'body_text:utf8:ustring'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser_do_logout()

    def test_manage_options(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/manage_main')
        html = self.browser.get_html()
        self.assertTrue('Naaya Meeting' in html)
        self.assertTrue('Contents' in html)
        self.assertTrue('View' in html)
        self.assertTrue('Properties' in html)
        self.assertTrue('Subobjects' in html)
        self.assertTrue('Dynamic properties' in html)
        self.assertTrue('Security' in html)
        self.assertTrue('Undo' in html)

        self.browser_do_logout()

    def test_reports(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))
        self.assertTrue(PARTICIPANT_ROLE in self.portal.getAuthenticationTool().list_all_roles())

        self.browser.go('http://localhost/portal/meeting_reports/report_meeting_participants')
        html = self.browser.get_html()
        self.assertTrue('Meeting Reports' in html)
        self.assertTrue('jstree' in html)

        self.browser.go('http://localhost/portal/meeting_reports/report_meeting_organisations')
        html = self.browser.get_html()
        self.assertTrue('Meeting Reports' in html)
        self.assertTrue('jstree' in html)

    def test_meeting_administrator(self):
        def assert_participant_access():
            self.browser_do_login('test_participant', 'participant')
            self.browser.go('http://localhost/portal/info/mymeeting')
            html = self.browser.get_html()
            self.assertTrue('Access denied' not in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/participants' in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' not in html)
            self.browser_do_logout()
        def assert_admin_access():
            self.browser_do_login('test_participant', 'participant')
            self.browser.go('http://localhost/portal/info/mymeeting')
            html = self.browser.get_html()
            self.assertTrue('Access denied' not in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/participants' in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' in html)
            self.browser_do_logout()


        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))
        self.assertTrue(PARTICIPANT_ROLE in self.portal.getAuthenticationTool().list_all_roles())

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formSetAdministrator')
        expected_controls = set(['uid', 'set_administrator'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser_do_logout()
        assert_participant_access()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formSetAdministrator')
        self.browser.clicked(form, self.browser.get_form_field(form, 'uid'))
        form['uid'] = ['test_participant']
        self.browser.submit()
        self.browser_do_logout()
        assert_admin_access()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formSetAdministrator')
        self.browser.clicked(form, self.browser.get_form_field(form, 'uid'))
        form['uid'] = ['']
        self.browser.submit()
        self.browser_do_logout()
        assert_participant_access()


class NyMeetingParticipantsTestCase(NaayaFunctionalTestCase):
    """ ParticipantsTestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        location = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark'}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting',
            releasedate='16/06/2010', start_date='20/06/2010', end_date='25/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain', **location)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)

        addPortalMeetingParticipant(self.portal)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        removePortalMeetingParticipant(self.portal)
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_add_participants(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))
        self.assertTrue(PARTICIPANT_ROLE in self.portal.getAuthenticationTool().list_all_roles())

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formSearchUsers')
        self.assertTrue('test_participant' not in self.browser.get_html())

        self.browser.clicked(form, self.browser.get_form_field(form, 'search_term:utf8:ustring'))
        form['search_param'] = ['uid']
        form['search_term:utf8:ustring'] = 'test_participant'
        self.browser.submit()
        form = self.browser.get_form('formAddUsers')
        expected_controls = set(['uids:list', 'add_users'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))
        self.assertTrue('test_participant' in self.browser.get_html())

        self.browser.clicked(form, self.browser.get_form_field(form, 'uids:list'))
        form['uids:list'] = ['test_participant']
        self.browser.submit()

        form = self.browser.get_form('formDeleteUsers')
        expected_controls = set(['uids:list', 'remove_users'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))
        self.assertTrue('test_participant' in self.browser.get_html())

        self.browser.clicked(form, self.browser.get_form_field(form, 'uids:list'))
        form['uids:list'] = ['test_participant']
        self.browser.submit()
        self.assertTrue('test_participant' not in self.browser.get_html())

        self.browser_do_logout()

    def test_participant_rights(self):
        def assert_access():
            self.browser_do_login('test_participant', 'participant')
            self.browser.go('http://localhost/portal/info/mymeeting')
            self.assertTrue('Access denied' not in self.browser.get_html()) 
            self.browser_do_logout()
        def assert_no_access():
            self.browser_do_login('test_participant', 'participant')
            self.browser.go('http://localhost/portal/info/mymeeting')
            self.assertTrue('Access denied' in self.browser.get_html()) 
            self.browser_do_logout()

        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))
        self.assertTrue(PARTICIPANT_ROLE in self.portal.getAuthenticationTool().list_all_roles())

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        self.assertTrue('test_participant' not in self.browser.get_html())
        self.browser_do_logout()
        assert_no_access()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formSearchUsers')
        self.browser.clicked(form, self.browser.get_form_field(form, 'search_term:utf8:ustring'))
        form['search_param'] = ['uid']
        form['search_term:utf8:ustring'] = 'test_participant'
        self.browser.submit()
        form = self.browser.get_form('formAddUsers')
        self.browser.clicked(form, self.browser.get_form_field(form, 'uids:list'))
        form['uids:list'] = ['test_participant']
        self.browser.submit()
        self.browser_do_logout()
        assert_access()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formDeleteUsers')
        self.browser.clicked(form, self.browser.get_form_field(form, 'uids:list'))
        form['uids:list'] = ['test_participant']
        self.browser.submit()
        self.browser_do_logout()
        assert_no_access()

ZopeTestCase.installProduct('NaayaWidgets')
ZopeTestCase.installProduct('NaayaSurvey')

class NyMeetingSurveyTestCase(NaayaFunctionalTestCase):
    """ SurveyTestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        location = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark'}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting',
            releasedate='16/06/2010', start_date='20/06/2010', end_date='25/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain', **location)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)

        addPortalMeetingParticipant(self.portal)
        self.portal.info.mymeeting.participants._add_user('test_participant')

        try:
            manage_addSurveyTool(self.portal)
        except:
            pass
        meeting = self.portal.info.mymeeting
        manage_addMegaSurvey(meeting, title='MySurvey')
        meeting.survey_pointer = 'info/mymeeting/mysurvey'
        import transaction; transaction.commit()

    def beforeTearDown(self):
        removePortalMeetingParticipant(self.portal)
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_survey_not_required(self):
        self.portal.info.mymeeting.survey_required = False
        import transaction; transaction.commit()

        self.browser_do_login('test_participant', 'participant')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info/mymeeting')
        self.assertTrue('Take the survey' in self.browser.get_html())
        self.browser_do_logout()

    def test_survey_required(self):
        self.portal.info.mymeeting.survey_required = True
        import transaction; transaction.commit()

        self.browser_do_login('test_participant', 'participant')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info/mymeeting/mysurvey')
        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyMeetingCreateTestCase))
    suite.addTest(makeSuite(NyMeetingEditingTestCase))
    suite.addTest(makeSuite(NyMeetingFunctionalTestCase))
    suite.addTest(makeSuite(NyMeetingParticipantsTestCase))
    suite.addTest(makeSuite(NyMeetingSurveyTestCase))
    return suite

