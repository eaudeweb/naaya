#from pyquery import PyQuery

#Zope imports
from Testing import ZopeTestCase

#Naaya imports
from DateTime import DateTime
from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.EmailTool.EmailTool import divert_mail
from Products.NaayaSurvey.MegaSurvey import manage_addMegaSurvey
from Products.Naaya.adapters import FolderMetaTypes

#Meeting imports
from naaya.content.meeting import ADMINISTRATOR_ROLE, PARTICIPANT_ROLE, OBSERVER_ROLE

def addPortalMeetingUsers(portal):
    portal.acl_users._doAddUser('test_observer', 'observer', [OBSERVER_ROLE], '', '', '', '')
    portal.acl_users._doAddUser('test_participant1', 'participant', [], '', '', '', '')
    portal.acl_users._doAddUser('test_participant2', 'participant', [], '', '', '', '')
    portal.acl_users._doAddUser('test_admin', 'admin', [], '', '', '', '')

def removePortalMeetingUsers(portal):
    portal.acl_users._doDelUsers(['test_observer', 'test_participant1', 'test_participant2', 'test_admin'])

class NyMeetingCreateTestCase(NaayaFunctionalTestCase):
    """ CreateTestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        self.portal.myfolder.approveThis()
        FolderMetaTypes(self.portal.myfolder).add('Naaya Meeting')
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
            'releasedate', 'interval.start_date', 'interval.end_date',
            'interval.start_time', 'interval.end_time',
            'interval.all_day:boolean', 'agenda_pointer:utf8:ustring',
            'minutes_pointer:utf8:ustring', 'survey_pointer:utf8:ustring',
            'contact_person:utf8:ustring', 'contact_email:utf8:ustring'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'MyMeeting'
        form['geo_location.address:utf8:ustring'] = 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark'
        form['releasedate'] = '16/06/2010'
        form['interval.start_date'] = '20/06/2010'
        form['interval.end_date'] = '25/06/2010'
        form['interval.all_day:boolean'] = ['on']
        form['contact_person:utf8:ustring'] = 'My Name'
        form['contact_email:utf8:ustring'] = 'my.email@my.domain'
        self.browser.submit()
        self.assertTrue(hasattr(self.portal.myfolder, 'mymeeting'))

        self.portal.myfolder.mymeeting.approveThis()
        self.browser.go('http://localhost/portal/myfolder/mymeeting')
        html = self.browser.get_html()
        self.assertTrue('MyMeeting' in html)
        self.assertTrue('20 - 25 Jun 2010' in html)
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
            'releasedate', 'interval.start_date', 'interval.end_date',
            'interval.start_time', 'interval.end_time', 'interval.all_day:boolean',
            'agenda_pointer:utf8:ustring', 'minutes_pointer:utf8:ustring', 'survey_pointer:utf8:ustring',
            'contact_person:utf8:ustring', 'contact_email:utf8:ustring'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'MyMeeting2'
        form['geo_location.address:utf8:ustring'] = 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark'
        form['releasedate'] = '16/06/2010'
        form['interval.start_date'] = '20/06/2010'
        form['interval.end_date'] = '25/06/2010'
        form['interval.start_time'] = '10:30'
        form['interval.end_time'] = '20:00'
        form['contact_person:utf8:ustring'] = 'My Name'
        form['contact_email:utf8:ustring'] = 'my.email@my.domain'
        self.browser.submit()
        self.assertTrue(hasattr(self.portal.myfolder, 'mymeeting2'))

        self.browser.go('http://localhost/portal/myfolder/mymeeting2')
        html = self.browser.get_html()
        self.assertTrue('MyMeeting2' in html)
        self.assertTrue('20/06/2010, 10:30 - 25/06/2010, 20:00' in html)
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
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.end_date': '25/06/2010',
                      'interval.all_day': True}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor',
                     submitted=1, title='MyMeeting', releasedate='16/06/2010',
                     contact_person='My Name', contact_email='my.email@my.domain',
                     allow_register=True, restrict_items=True, **extra_args)
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.start_time': '10:30',
                      'interval.end_date': '25/06/2010',
                      'interval.end_time': '20:00',
                      'interval.all_day': False}
        addNyMeeting(self.portal.info, 'mymeeting2', contributor='contributor',
                     submitted=1, title='MyMeeting', contact_person='My Name',
                     contact_email='my.email@my.domain', releasedate='16/06/2010',
                     allow_register=True, restrict_items=True, **extra_args)
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
        self.assertEqual(form['interval.start_date'], '20/06/2010')
        self.assertEqual(form['interval.end_date'], '25/06/2010')
        self.assertEqual(form['contact_person:utf8:ustring'], 'My Name')
        self.assertEqual(form['contact_email:utf8:ustring'], 'my.email@my.domain')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'MyEditedMeeting'
        form['geo_location.address:utf8:ustring'] = 'Kogens Nytorv 8, 1050 Copenhagen K, Denmark'
        form['releasedate'] = '17/06/2010'
        form['interval.start_date'] = '21/06/2010'
        form['interval.end_date'] = '26/06/2010'
        form['interval.all_day:boolean'] = []
        form['interval.start_time'] = '10:30'
        form['interval.end_time'] = '20:00'
        form['contact_person:utf8:ustring'] = 'My Edited Name'
        form['contact_email:utf8:ustring'] = 'my.edited.email@my.domain'
        self.browser.submit()
        self.browser.go('http://localhost/portal/info/mymeeting')
        html = self.browser.get_html()
        self.assertTrue('MyEditedMeeting' in html)
        self.assertTrue('21/06/2010, 10:30 - 26/06/2010, 20:00' in html)
        self.assertTrue('My Edited Name' in html)
        self.assertTrue('mailto:my.edited.email@my.domain' in html)
        self.assertTrue('http://localhost/portal/info/mymeeting/get_ics' in html)
        self.assertTrue('17/06/2010' in html)
        #self.assertTrue('contributor' in html)
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
        self.assertEqual(form['interval.start_date'], '20/06/2010')
        self.assertEqual(form['interval.end_date'], '25/06/2010')
        self.assertEqual(form['interval.start_time'], '10:30')
        self.assertEqual(form['interval.end_time'], '20:00')
        self.assertEqual(form['contact_person:utf8:ustring'], 'My Name')
        self.assertEqual(form['contact_email:utf8:ustring'], 'my.email@my.domain')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'MyEditedMeeting'
        form['geo_location.address:utf8:ustring'] = 'Kogens Nytorv 8, 1050 Copenhagen K, Denmark'
        form['releasedate'] = '17/06/2010'
        form['interval.start_date'] = '21/06/2010'
        form['interval.end_date'] = '26/06/2010'
        form['interval.start_time'] = '11:00'
        form['interval.end_time'] = '21:00'
        form['contact_person:utf8:ustring'] = 'My Edited Name'
        form['contact_email:utf8:ustring'] = 'my.edited.email@my.domain'
        self.browser.submit()
        self.browser.go('http://localhost/portal/info/mymeeting2')
        html = self.browser.get_html()
        self.assertTrue('MyEditedMeeting' in html)
        self.assertTrue('21/06/2010, 11:00 - 26/06/2010, 21:00' in html)
        self.assertTrue('My Edited Name' in html)
        self.assertTrue('mailto:my.edited.email@my.domain' in html)
        self.assertTrue('http://localhost/portal/info/mymeeting2/get_ics' in html)
        self.assertTrue('17/06/2010' in html)
        #self.assertTrue('contributor' in html)
        self.assertTrue('Kogens Nytorv 8, 1050 Copenhagen K, Denmark' in html)

        self.browser_do_logout()


class NyMeetingFunctionalTestCase(NaayaFunctionalTestCase):
    """ FunctionalTestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.start_time': '10:00',
                      'interval.end_date': '25/06/2010',
                      'interval.end_time': '20:00',
                      'interval.all_day': False}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting', max_participants='10', releasedate='16/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain',
            allow_register=True, restrict_items=True, **extra_args)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)
        addPortalMeetingUsers(self.portal)
        self.portal.info.mymeeting.participants._set_attendee('test_participant1', PARTICIPANT_ROLE)
        self.diverted_mail = divert_mail(True)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        divert_mail(False)
        removePortalMeetingUsers(self.portal)
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_index(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))

        self.browser_do_login('test_participant1', 'participant')
        self.browser.go('http://localhost/portal/info/mymeeting')
        html = self.browser.get_html()
        self.assertTrue('MyMeeting' in html)
        self.assertTrue('20/06/2010, 10:00 - 25/06/2010, 20:00' in html)
        self.assertTrue('My Name' in html)
        self.assertTrue('mailto:my.email@my.domain' in html)
        self.assertTrue('http://localhost/portal/info/mymeeting/get_ics' in html)
        self.assertTrue('16/06/2010' in html)
        #self.assertTrue('contributor' in html)
        self.assertTrue('Kogens Nytorv 6, 1050 Copenhagen K, Denmark' in html)

        self.browser_do_logout()

    def test_feed(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))

        self.browser_do_login('test_participant1', 'participant')
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

    def test_saved_emails(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertTrue('http://localhost/portal/info/mymeeting/email_sender' in self.browser.get_html())

        self.browser.go('http://localhost/portal/info/mymeeting/email_sender')
        self.assertTrue('http://localhost/portal/info/mymeeting/email_sender/saved_emails' in self.browser.get_html())

        #self.browser.go('http://localhost/portal/info/mymeeting/email_sender/saved_emails')
        #pq = PyQuery(self.browser.get_html())
        #goto_archive_page = pq('td>a:contains("Test subject")')
        #self.assertTrue(len(goto_archive_page) >= 1)
        #goto_archive_page = goto_archive_page[0]
        #self.assertTrue(goto_archive_page.attrib.get('href'))

        #self.browser.go(goto_archive_page.attrib['href'])
        ## TODO this is where some js/ajax kicks in; how do we test that?
        #pq = PyQuery(self.browser.get_html())
        #recipients_cell = pq("td#recipients-cell>a")
        #self.assertTrue(recipients_cell)
        #recipients_cell = recipients_cell[0]
        #href = recipients_cell.attrib.get("href")
        #title = recipients_cell.attrib.get("title")
        #self.assertTrue(href)
        #self.assertTrue(title)
        #self.assertTrue(href.startswith("mailto:"))
        #self.assertTrue(title.startswith("Send email to"))

    def test_send_emails_page(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertTrue('http://localhost/portal/info/mymeeting/email_sender' in self.browser.get_html())

        self.browser.go('http://localhost/portal/info/mymeeting/email_sender')
        form = self.browser.get_form('formSendEmail')
        expected_controls = set(['from_email:utf8:ustring', 'to_uids:list', 'subject:utf8:ustring', 'body_text:utf8:ustring', 'send_email'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'send_email'))
        form['subject:utf8:ustring'] = 'Test subject'
        form['body_text:utf8:ustring'] = 'Test body'
        self.browser.submit()
        html = self.browser.get_html()
        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info/mymeeting/email_sender/send_email')
        self.assertTrue('http://localhost/portal/info/mymeeting' in html)
        self.assertTrue('There was an error sending the email.' in html)

        self.assertEqual(len(self.diverted_mail), 0)

        self.browser.go('http://localhost/portal/info/mymeeting/email_sender')
        form = self.browser.get_form('formSendEmail')
        self.browser.clicked(form, self.browser.get_form_field(form, 'send_email'))
        form['to_uids:list'] = ['test_participant1']
        form['subject:utf8:ustring'] = 'Test subject'
        form['body_text:utf8:ustring'] = 'Test body'
        self.browser.submit()
        html = self.browser.get_html()
        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info/mymeeting/email_sender/send_email')
        self.assertTrue('http://localhost/portal/info/mymeeting' in html)
        self.assertTrue('Your email was sent successfully.' in html)

        self.assertEqual(len(self.diverted_mail), 1)

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
        self.assertTrue('Security' in html)
        self.assertTrue('Undo' in html)

        self.browser_do_logout()

    def test_reports(self):
        self.browser_do_login('test_participant1', 'participant')
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))
        self.assertTrue(PARTICIPANT_ROLE in self.portal.info.mymeeting.__ac_roles__)

        self.browser.go('http://localhost/portal/meeting_reports/report_meeting_participants')
        html = self.browser.get_html()
        self.assertTrue('Meeting Reports' in html)
        self.assertTrue('jstree' in html)

        self.browser.go('http://localhost/portal/meeting_reports/report_meeting_organizations')
        html = self.browser.get_html()
        self.assertTrue('Meeting Reports' in html)
        self.assertTrue('jstree' in html)

    def test_meeting_administrator(self):
        def assert_participant_access():
            self.browser_do_login('test_participant1', 'participant')
            self.browser.go('http://localhost/portal/info/mymeeting')
            html = self.browser.get_html()
            self.assertTrue('Access denied' not in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/participants' in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' not in html)
            self.browser_do_logout()
        def assert_admin_access():
            self.browser_do_login('test_participant1', 'participant')
            self.browser.go('http://localhost/portal/info/mymeeting')
            html = self.browser.get_html()
            self.assertTrue('Access denied' not in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/participants' in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' in html)
            self.browser_do_logout()


        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))
        self.assertTrue(PARTICIPANT_ROLE in self.portal.info.mymeeting.__ac_roles__)

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formOnAttendees')
        expected_controls = set(['uids:list', 'set_administrators'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser_do_logout()
        assert_participant_access()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formOnAttendees')
        self.browser.clicked(form, self.browser.get_form_field(form, 'set_administrators'))
        form['uids:list'] = ['test_participant1']
        self.browser.submit()
        self.browser_do_logout()
        assert_admin_access()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formOnAttendees')
        self.browser.clicked(form, self.browser.get_form_field(form, 'set_participants'))
        form['uids:list'] = ['test_participant1']
        self.browser.submit()
        self.browser_do_logout()
        assert_participant_access()


class NyMeetingParticipantsTestCase(NaayaFunctionalTestCase):
    """ ParticipantsTestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.end_date': '25/06/2010',
                      'interval.all_day': True}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting', max_participants='1', releasedate='16/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain',
            allow_register=True, restrict_items=True, **extra_args)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)

        addPortalMeetingUsers(self.portal)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        removePortalMeetingUsers(self.portal)
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_add_participants(self):
        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))
        self.assertTrue(PARTICIPANT_ROLE in self.portal.info.mymeeting.__ac_roles__)

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formSearchUsers')
        self.assertTrue('test_participant1' not in self.browser.get_html())

        self.browser.clicked(form, self.browser.get_form_field(form, 'search_term:utf8:ustring'))
        form['search_param'] = ['uid']
        form['search_term:utf8:ustring'] = 'test_participant'
        self.browser.submit()
        form = self.browser.get_form('formAddUsers')
        expected_controls = set(['uids:list', 'add_users'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))
        self.assertTrue('test_participant1' in self.browser.get_html())

        self.browser.clicked(form, self.browser.get_form_field(form, 'uids:list'))
        form['uids:list'] = ['test_participant1', 'test_participant2']
        self.browser.submit()

        form = self.browser.get_form('formOnAttendees')
        expected_controls = set(['uids:list', 'del_attendees'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))
        html = self.browser.get_html()
        self.assertTrue('test_participant1' in html)
        self.assertTrue('test_participant2' in html)
        self.assertTrue('Participant' in html)
        self.assertTrue('Waiting List' in html)

        self.browser.clicked(form, self.browser.get_form_field(form, 'del_attendees'))
        form['uids:list'] = ['test_participant1']
        self.browser.submit()
        self.assertTrue('test_participant1' not in self.browser.get_html())

        self.browser_do_logout()

    def test_participant_rights(self):
        def assert_access():
            self.browser_do_login('test_participant1', 'participant')
            self.browser.go('http://localhost/portal/info/mymeeting')
            self.assertTrue('Register another user' in self.browser.get_html())
            self.browser_do_logout()
        def assert_no_access():
            self.browser_do_login('test_participant1', 'participant')
            self.browser.go('http://localhost/portal/info/mymeeting')
            self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe' in self.browser.get_html())
            self.browser_do_logout()

        self.assertTrue(hasattr(self.portal.info, 'mymeeting'))
        self.assertTrue(PARTICIPANT_ROLE in self.portal.info.mymeeting.__ac_roles__)

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        self.assertTrue('test_participant1' not in self.browser.get_html())
        self.browser_do_logout()
        assert_no_access()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formSearchUsers')
        self.browser.clicked(form, self.browser.get_form_field(form, 'search_term:utf8:ustring'))
        form['search_param'] = ['uid']
        form['search_term:utf8:ustring'] = 'test_participant1'
        self.browser.submit()
        form = self.browser.get_form('formAddUsers')
        self.browser.clicked(form, self.browser.get_form_field(form, 'uids:list'))
        form['uids:list'] = ['test_participant1']
        self.browser.submit()
        self.browser_do_logout()
        assert_access()

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formOnAttendees')
        self.browser.clicked(form, self.browser.get_form_field(form, 'uids:list'))
        form['uids:list'] = ['test_participant1']
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
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.end_date': '25/06/2010',
                      'interval.all_day': True}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting', max_participants='1', releasedate='16/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain',
            allow_register=True, restrict_items=True, **extra_args)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)

        addPortalMeetingUsers(self.portal)
        self.portal.info.mymeeting.participants._set_attendee('test_participant1', PARTICIPANT_ROLE)

        meeting = self.portal.info.mymeeting
        manage_addMegaSurvey(meeting, title='MySurvey')
        meeting.survey_pointer = 'info/mymeeting/mysurvey'
        import transaction; transaction.commit()

    def beforeTearDown(self):
        removePortalMeetingUsers(self.portal)
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_survey_not_required(self):
        self.portal.info.mymeeting.survey_required = False
        import transaction; transaction.commit()

        self.browser_do_login('test_participant1', 'participant')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info/mymeeting')
        self.assertTrue('Survey' in self.browser.get_html())
        self.browser_do_logout()

    def test_survey_required(self):
        self.portal.info.mymeeting.survey_required = True
        import transaction; transaction.commit()

        self.browser_do_login('test_participant1', 'participant')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info/mymeeting/mysurvey')
        self.browser_do_logout()

class NyMeetingSignupTestCase(NaayaFunctionalTestCase):
    """ SignupTestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.end_date': '25/06/2010',
                      'interval.all_day': True}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting', max_participants='1', releasedate='16/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain',
            allow_register=True, restrict_items=True, **extra_args)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)
        self.diverted_mail = divert_mail(True)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        divert_mail(False)
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def testSignupLink(self):
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe' in self.browser.get_html())

    def testSubscriptionsLink(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions' in self.browser.get_html())
        self.browser_do_logout()

    def testSignupValidation(self):
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe')
        self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/signup' in self.browser.get_html())
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/signup')

        form = self.browser.get_form('formSignup')
        expected_controls = set(['first_name:utf8:ustring', 'last_name:utf8:ustring', 'email:utf8:ustring', 'organization:utf8:ustring', 'phone:utf8:ustring', 'add_signup'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'add_signup'))
        form['first_name:utf8:ustring'] = 'test_first_name'
        form['last_name:utf8:ustring'] = 'test_last_name'
        self.browser.submit()

        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info/mymeeting/participants/subscriptions/signup')
        html = self.browser.get_html()
        self.assertTrue('This field is mandatory' in html)
        self.assertTrue('test_first_name' in html)
        self.assertTrue('test_last_name' in html)

        form = self.browser.get_form('formSignup')
        self.browser.clicked(form, self.browser.get_form_field(form, 'add_signup'))
        form['email:utf8:ustring'] = 'test_email'
        form['organization:utf8:ustring'] = 'test_organization'
        form['phone:utf8:ustring'] = 'test_phone'
        self.browser.submit()

        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info/mymeeting/participants/subscriptions/signup')
        html = self.browser.get_html()
        self.assertTrue('This field is mandatory' not in html)
        self.assertTrue('An email address must contain a single @' in html)
        self.assertTrue('test_first_name' in html)
        self.assertTrue('test_last_name' in html)
        self.assertTrue('test_email' in html)

        form = self.browser.get_form('formSignup')
        self.browser.clicked(form, self.browser.get_form_field(form, 'add_signup'))
        form['email:utf8:ustring'] = 'test_email@email.com'
        self.browser.submit()

        self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info/mymeeting/participants/subscriptions/signup_successful')

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions')
        html = self.browser.get_html()
        self.assertTrue('test_first_name test_last_name' in html)
        self.assertTrue('mailto:test_email@email.com' in html)
        self.assertTrue('new' in html)

        self.browser_do_logout()

    def testSignupLogin(self):
        def assert_admin_access(key):
            self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome?key=' + key)
            html = self.browser.get_html()
            self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome?logout=' in html)

            self.browser.go('http://localhost/portal/info/mymeeting')
            html = self.browser.get_html()
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe' not in html)

            self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome?logout=')
            self.assertEqual('http://localhost/portal/info/mymeeting', self.browser.get_url())
            html = self.browser.get_html()
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' not in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe' in html)

        def assert_access(key):
            self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome?key=' + key)
            html = self.browser.get_html()
            self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome?logout=' in html)

            self.browser.go('http://localhost/portal/info/mymeeting')
            html = self.browser.get_html()
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' not in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe' not in html)

            self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome?logout=')
            html = self.browser.get_html()
            self.assertEqual('http://localhost/portal/info/mymeeting', self.browser.get_url())
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' not in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe' in html)

        def assert_rejected(key):
            self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome?key=' + key)
            html = self.browser.get_html()
            self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome?logout=' not in html)
            self.assertTrue('You were rejected.' in html)

            self.browser.go('http://localhost/portal/info/mymeeting')
            html = self.browser.get_html()
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' not in html)
            self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe' in html)

        # submit the signup
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe')
        self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/signup' in self.browser.get_html())
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/signup')

        form = self.browser.get_form('formSignup')
        self.browser.clicked(form, self.browser.get_form_field(form, 'add_signup'))
        form['first_name:utf8:ustring'] = 'test_first_name'
        form['last_name:utf8:ustring'] = 'test_last_name'
        form['email:utf8:ustring'] = 'test_email@email.com'
        form['organization:utf8:ustring'] = 'test_organization'
        form['phone:utf8:ustring'] = 'test_phone'
        self.browser.submit()

        self.assertEqual(len(self.diverted_mail), 1)
        body, addr_to, addr_cc, addr_from, subject = self.diverted_mail[0]
        self.assertTrue('http://localhost/portal/info/mymeeting' in body)
        self.assertEqual(addr_to, ['my.email@my.domain'])
        self.assertEqual(subject, 'Signup notification - MyMeeting')

        # accept the signup
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions')
        html = self.browser.get_html()
        self.assertTrue('test_first_name test_last_name' in html)
        self.assertTrue('mailto:test_email@email.com' in html)
        self.assertTrue('new' in html)

        form = self.browser.get_form('formManageSignups')
        expected_controls = set(['keys:list', 'accept', 'reject'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.assertTrue(form.controls[1].name == 'keys:list')
        key = form.controls[1]._value
        self.browser.clicked(form, self.browser.get_form_field(form, 'accept'))
        form['keys:list'] = [key]
        self.browser.submit()
        self.browser_do_logout()
        assert_access(key)
        self.assertEqual(len(self.diverted_mail), 2)
        body, addr_to, addr_cc, addr_from, subject = self.diverted_mail[1]
        self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome?key=' + key in body)
        self.assertEqual(addr_to, ['test_email@email.com'])
        self.assertEqual(addr_from, 'my.email@my.domain')
        self.assertEqual(subject, 'Signup notification - MyMeeting')

        # give admin rights
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formOnAttendees')
        self.browser.clicked(form, self.browser.get_form_field(form, 'set_administrators'))
        form['uids:list'] = [key]
        self.browser.submit()
        self.browser_do_logout()
        assert_admin_access(key)

        # reject rights
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions')
        form = self.browser.get_form('formManageSignups')
        self.browser.clicked(form, self.browser.get_form_field(form, 'reject'))
        form['keys:list'] = [key]
        self.browser.submit()
        self.browser_do_logout()
        assert_rejected(key)

class NyMeetingAccountSubscriptionTestCase(NaayaFunctionalTestCase):
    """ AccountSubscriptionTestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.end_date': '25/06/2010',
                      'interval.all_day': True}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting', max_participants='1', releasedate='16/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain',
            allow_register=True, restrict_items=True, **extra_args)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)
        self.diverted_mail = divert_mail(True)
        addPortalMeetingUsers(self.portal)
        import transaction; transaction.commit()

    def beforeTearDown(self):
        removePortalMeetingUsers(self.portal)
        divert_mail(False)
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def testSubscriptionsLink(self):
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe' in self.browser.get_html())

    def testSubscriptionsAcceptLink(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions' in self.browser.get_html())
        self.browser_do_logout()

    def testAccountLogin(self):
        def assert_admin_access():
            self.browser_do_login('test_participant1', 'participant')
            self.browser.go('http://localhost/portal/info/mymeeting')
            html = self.browser.get_html()
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' in html)
            self.assertTrue('Register another user' in html)
            self.browser_do_logout()

        def assert_access():
            self.browser_do_login('test_participant1', 'participant')
            self.browser.go('http://localhost/portal/info/mymeeting')
            html = self.browser.get_html()
            self.assertTrue('http://localhost/portal/info/mymeeting/edit_html' not in html)
            self.assertTrue('Register another user' in html)
            self.browser_do_logout()

        # submit the subscription
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe')
        self.assertTrue('http://localhost/portal/login_html?came_from=http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe' in self.browser.get_html())
        self.browser_do_login('test_participant1', 'participant')
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe')
        self.assertTrue('http://localhost/portal/login_html?came_from=http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe_my_account' not in self.browser.get_html())
        self.assertTrue('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe_my_account' in self.browser.get_html())
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe_my_account')

        self.assertEqual(len(self.diverted_mail), 1)
        body, addr_to, addr_cc, addr_from, subject = self.diverted_mail[0]
        self.assertTrue('http://localhost/portal/info/mymeeting' in body)
        self.assertEqual(addr_to, ['my.email@my.domain'])
        self.assertEqual(subject, 'Account subscription notification - MyMeeting')
        self.browser_do_logout()

        # accept the signup
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions')
        html = self.browser.get_html()
        self.assertTrue('test_participant1' in html)

        form = self.browser.get_form('formManageAccountSubscriptions')
        expected_controls = set(['uids:list', 'accept', 'reject'])
        found_controls = set(c.name for c in form.controls)
        self.assertTrue(expected_controls <= found_controls,
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.assertTrue(form.controls[1].name == 'uids:list')
        self.browser.clicked(form, self.browser.get_form_field(form, 'accept'))
        form['uids:list'] = ['test_participant1']
        self.browser.submit()
        self.browser_do_logout()

        assert_access()

        self.assertEqual(len(self.diverted_mail), 2)
        body, addr_to, addr_cc, addr_from, subject = self.diverted_mail[1]
        self.assertTrue('http://localhost/portal/info/mymeeting' in body)
        self.assertTrue('test_participant1' in body)
        self.assertEqual(addr_from, 'my.email@my.domain')
        self.assertEqual(subject, 'Account subscription notification - MyMeeting')

        # give admin rights
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        form = self.browser.get_form('formOnAttendees')
        self.browser.clicked(form, self.browser.get_form_field(form, 'set_administrators'))
        form['uids:list'] = ['test_participant1']
        self.browser.submit()
        self.browser_do_logout()
        assert_admin_access()


class NyMeetingReleaseDateAccess(NaayaFunctionalTestCase):
    """ Access based on releaseddate TestCase for NyMeeting object """

    def setUp(self):
        super(NyMeetingReleaseDateAccess, self).setUp()
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.end_date': '25/06/2010',
                      'interval.all_day': True}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting', max_participants='2', releasedate='16/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain',
            allow_register=True, restrict_items=True, **extra_args)

        self.meeting = self.portal['info']['mymeeting']
        self.meeting_url = self.meeting.absolute_url()
        import transaction; transaction.commit()

    def test_approve(self):
        """ Automatically approve when release date is in the past
        """
        meeting = self.portal.info.mymeeting
        # release date is in the past
        assert meeting.releasedate < DateTime()
        assert bool(meeting.approved) == False
        self.browser.go(self.meeting.absolute_url())
        assert bool(meeting.approved) == True

    def test_unapprove(self):
        """ Automatically unapprove when release date is in the future
        """
        # release date is in the future
        self.browser.go(self.meeting.absolute_url())

        self.meeting.releasedate = DateTime() + 10
        self.meeting.approveThis(True)
        import transaction; transaction.commit()

        self.browser.go(self.meeting.absolute_url())
        assert 'login_html' in self.browser.get_url()


class NyMeetingAccess(NaayaFunctionalTestCase):
    """ Access TestCase for NyMeeting object """

    def setUp(self):
        super(NyMeetingAccess, self).setUp()
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.end_date': '25/06/2010',
                      'interval.all_day': True}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting', max_participants='2', releasedate='16/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain',
            allow_register=True, restrict_items=True, **extra_args)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)
        self.diverted_mail = divert_mail(True)
        addPortalMeetingUsers(self.portal)
        self.portal.info.mymeeting.manage_setLocalRoles('test_admin', [ADMINISTRATOR_ROLE])
        self.portal.info.mymeeting.manage_setLocalRoles('test_participant1', [PARTICIPANT_ROLE])
        self.portal.info.mymeeting.manage_setLocalRoles('test_participant2', [PARTICIPANT_ROLE])

        meeting = self.portal.info.mymeeting
        manage_addMegaSurvey(meeting, title='MySurvey')
        meeting.survey_pointer = 'info/mymeeting/mysurvey'

        import transaction; transaction.commit()

    def tearDown(self):
        removePortalMeetingUsers(self.portal)
        divert_mail(False)
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()
        super(NyMeetingAccess, self).tearDown()

    def testAnonymous(self):
        # no login
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/email_sender')
        self.assertAccessDenied()
        #self.browser.go('http://localhost/portal/info/mymeeting/mysurvey')
        #self.assertAccessDenied()

        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        self.assertAccessDenied()

        self.browser.go('http://localhost/portal/info/mymeeting/participants/get_participants')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/participants/getAttendees')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/participants/getAttendeeInfo?uid=test_admin')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/participants/pickrole_html')
        self.assertAccessDenied()

        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/signup')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getSignups')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getSignup')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getAccountSubscriptions')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getAccountSubscription')
        self.assertAccessDenied()
        # no logout

    def testObserver(self):
        self.browser_do_login('test_observer', 'observer')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/email_sender')
        self.assertAccessDenied()
        #self.browser.go('http://localhost/portal/info/mymeeting/mysurvey')
        #self.assertAccessDenied(False)

        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        self.assertAccessDenied()

        self.browser.go('http://localhost/portal/info/mymeeting/participants/get_participants')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/getAttendees')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/getAttendeeInfo?uid=test_admin')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/pickrole_html')
        self.assertAccessDenied()

        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/signup')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getSignups')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getSignup')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getAccountSubscriptions')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getAccountSubscription')
        self.assertAccessDenied()
        self.browser_do_logout()

    def testParticipant(self):
        self.browser_do_login('test_participant1', 'participant')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/email_sender')
        self.assertAccessDenied()
        #self.browser.go('http://localhost/portal/info/mymeeting/mysurvey')
        #self.assertAccessDenied(False)

        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        self.assertAccessDenied()

        self.browser.go('http://localhost/portal/info/mymeeting/participants/get_participants')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/getAttendees')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/getAttendeeInfo?uid=test_admin')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/pickrole_html')
        self.assertAccessDenied()

        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/signup')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getSignups')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getSignup')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getAccountSubscriptions')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getAccountSubscription')
        self.assertAccessDenied()
        self.browser_do_logout()

    def testWaitingList(self):
        self.browser_do_login('test_participant2', 'participant')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/email_sender')
        self.assertAccessDenied()
        #self.browser.go('http://localhost/portal/info/mymeeting/mysurvey')
        #self.assertAccessDenied(False)

        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        self.assertAccessDenied()

        self.browser.go('http://localhost/portal/info/mymeeting/participants/get_participants')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/getAttendees')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/getAttendeeInfo?uid=test_admin')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/pickrole_html')
        self.assertAccessDenied()

        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/signup')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getSignups')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getSignup')
        self.assertAccessDenied()
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getAccountSubscriptions')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getAccountSubscription')
        self.assertAccessDenied()
        self.browser_do_logout()

    def testAdmin(self):
        self.browser_do_login('test_admin', 'admin')
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/email_sender')
        self.assertAccessDenied(False)
        #self.browser.go('http://localhost/portal/info/mymeeting/mysurvey')
        #self.assertAccessDenied(False)

        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        self.assertAccessDenied(False)

        self.browser.go('http://localhost/portal/info/mymeeting/participants/get_participants')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/getAttendees')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/getAttendeeInfo?uid=test_admin')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/pickrole_html')
        self.assertAccessDenied(False)

        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/subscribe')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/signup')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/welcome')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getSignups')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getSignup')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getAccountSubscriptions')
        self.assertAccessDenied(False)
        self.browser.go('http://localhost/portal/info/mymeeting/participants/subscriptions/getAccountSubscription')
        self.assertAccessDenied(False)
        self.browser_do_logout()

class NyMeetingRegisterNotAllowed(NaayaFunctionalTestCase):
    """ Not allowed register TestCase for NyMeeting object """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.end_date': '25/06/2010',
                      'interval.all_day': True}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting', max_participants='2', releasedate='16/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain',
            allow_register=False, restrict_items=True, **extra_args)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)
        #meeting = self.portal.info.mymeeting
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_register_not_allowed(self):
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.assertTrue('/participants/subscriptions/subscribe' not in self.browser.get_html())

        base_url = 'http://localhost/portal/info/mymeeting/participants/subscriptions/'
        for rel_url in ['subscribe', 'signup', 'subscribe_my_account']:
            self.browser.go(base_url + rel_url)
            self.assertEqual(self.browser.get_url(), 'http://localhost/portal/info/mymeeting/participants/subscriptions/subscription_not_allowed')

class NyMeetingItemsRestrictedButAgenda(NaayaFunctionalTestCase):
    """ All items inside a meeting are restricted except the agenda """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.end_date': '25/06/2010',
                      'interval.all_day': True}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting', max_participants='2', releasedate='16/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain',
            allow_register=False, restrict_items=True, **extra_args)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)
        #meeting = self.portal.info.mymeeting
        import transaction; transaction.commit()
        from naaya.content.document.document_item import addNyDocument
        addNyDocument(self.portal.info.mymeeting, id='mydoc', title='My document', submitted=1, contributor='contributor')
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_make_document_agenda_and_back(self):
        self.browser.go('http://localhost/portal/info/mymeeting/mydoc')
        self.assertTrue('http://localhost/portal/login_html?came_from='
                            in self.browser.get_url())

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['agenda_pointer:utf8:ustring'] = 'info/mymeeting/mydoc'
        self.browser.submit()
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.browser_do_logout()

        self.browser.go('http://localhost/portal/info/mymeeting/mydoc')
        self.assertTrue('http://localhost/portal/login_html?came_from='
                            not in self.browser.get_url())

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['agenda_pointer:utf8:ustring'] = ''
        self.browser.submit()
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.browser_do_logout()

        self.browser.go('http://localhost/portal/info/mymeeting/mydoc')
        self.assertTrue('http://localhost/portal/login_html?came_from='
                            in self.browser.get_url())

class NyMeetingRestrictUnrestrict(NaayaFunctionalTestCase):
    """ """

    def afterSetUp(self):
        self.portal.manage_install_pluggableitem('Naaya Meeting')
        from naaya.content.meeting.meeting import addNyMeeting
        extra_args = {'geo_location.address': 'Kogens Nytorv 6, 1050 Copenhagen K, Denmark',
                      'interval.start_date': '20/06/2010',
                      'interval.end_date': '25/06/2010',
                      'interval.all_day': True}
        addNyMeeting(self.portal.info, 'mymeeting', contributor='contributor', submitted=1,
            title='MyMeeting', max_participants='2', releasedate='16/06/2010',
            contact_person='My Name', contact_email='my.email@my.domain',
            allow_register=False, restrict_items=True, **extra_args)
        self.portal.info.mymeeting.approveThis()
        self.portal.recatalogNyObject(self.portal.info.mymeeting)
        #meeting = self.portal.info.mymeeting
        import transaction; transaction.commit()
        from Products.Naaya.NyFolder import addNyFolder
        addNyFolder(self.portal.info.mymeeting, id='myfolder', title='Folder', submitted=1, contributor='contributor')
        self.portal.info.mymeeting.myfolder.approveThis()
        import transaction; transaction.commit()

    def beforeTearDown(self):
        self.portal.info.manage_delObjects(['mymeeting'])
        self.portal.manage_uninstall_pluggableitem('Naaya Meeting')
        import transaction; transaction.commit()

    def test_make_meeting_restricted_and_back(self):
        folder_url = 'http://localhost/portal/info/mymeeting/myfolder'
        self.browser.go(folder_url)
        self.assertNotEqual(folder_url, self.browser.get_url())

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['restrict_items:boolean'] = []
        self.browser.submit()
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.browser_do_logout()

        self.browser.go(folder_url)
        self.assertEqual(folder_url, self.browser.get_url())

        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/info/mymeeting/edit_html')
        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['restrict_items:boolean'] = ['on']
        self.browser.submit()
        self.browser.go('http://localhost/portal/info/mymeeting')
        self.browser_do_logout()

        self.browser.go(folder_url)
        self.assertNotEqual(folder_url, self.browser.get_url())
