import unittest2 as unittest
import random 
import string
import database


class ReportCrudTest(unittest.TestCase):

    def setUp(self):
        from common import create_mock_app
        self.app, app_teardown = create_mock_app()
        self.addCleanup(app_teardown)
        # generate a unique random report name
        self.report_name=''.join(random.choice(string.letters + string.digits) 
                                 for i in xrange(30))

    def test_add(self):
        client = self.app.test_client()
        post_response = client.post('/reports/new/', data={
            'format_availability_paper_or_web': 'paper only',
            'header_uploader': 'Report Guru',
            'format_lang_of_pub': 'ro',
            'details_original_name': self.report_name,
            'format_availability_costs': 'free',
            'header_country': 'Romania',
            'details_original_language': 'ro',
            'global_level': 'on',
        }, follow_redirects=True)
        self.assertIn('Report saved.', post_response.data)
        list_response = client.get('/reports/')
        self.assertIn(self.report_name, list_response.data)


    def test_delete(self):
        client = self.app.test_client()
        with self.app.test_request_context():
            session = database.get_session()
            session.save(database.ReportRow(name="very_nice_and_unique_name"))
            session.commit()

        post_response = client.post("reports/1/delete/")
        list_response = client.get('/reports/')
        self.assertFalse( "very_nice_and_unique_name" in list_response.data)
        self.assertIn("Report deleted.", list_response.data)

        
    def test_edit(self):
        import pdb
        pdb.set_trace()
        client = self.app.test_client()
        with self.app.test_request_context():
            session = database.get_session()
            row = database.ReportRow()
            data = {
                    u'format_availability_paper_or_web': u'paper only',
                    u'format_lang_of_pub_0': u'ro',
                    u'format_availability_costs': u'free',
                    u'details_original_name': u'Test Report',
                    u'details_original_language': u'ro',
                    u'format_availability_paper_or_web': u'paper only', 
                    u'header_country_0': u'Romania',
                    u'header_uploader': u'Report Guru'
                   }
            row.update(data)
            session.save(row)
            session.commit()
            data[u'format_no_of_pages'] =  u'5' #add new field
            edit_response = client.post('/reports/1/edit/',
                            data = {
                            'format_availability_paper_or_web': 'paper only',
                            'header_uploader': 'Report Guru',
                            'format_lang_of_pub': 'ro',
                            'details_original_name': self.report_name,
                            'format_availability_costs': 'free',
                            'header_country': 'Romania',
                            'details_original_language': 'ro',
                            'global_level': 'on'})

            #TODO uncomment when ready
            #self.assertIn("Report saved.", edit_response.data)


