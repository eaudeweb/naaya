import unittest2 as unittest
import random 
import string
import database
import schema
import re
import logging
import common

logging.basicConfig(level=logging.DEBUG)

class ReportCrudTest(unittest.TestCase):

    def setUp(self):
        from common import create_mock_app
        self.app, app_teardown = create_mock_app()
        self.addCleanup(app_teardown)
        self.report_data = {}
        self.report_data.update(schema.ReportSchema.from_defaults().flatten())
        self.report_data.update(schema.SerisReviewSchema.from_defaults().flatten())
        data = {
            u'format_availability_paper_or_web': u'paper only',
            u'format_lang_of_pub': u'ro',
            u'format_availability_costs': u'free',
            u'details_original_name': u'asds3923x.@',
            u'details_original_language': u'ro',
            u'header_country': u'Romania',
            u'header_uploader': u'Report Guru',
            u'links_reference_global_level': u'on'
        }
        self.report_data.update(data)


    def test_create(self):
        client = self.app.test_client()
        post_response = client.post('/reports/new/', 
                                    data= self.report_data,
                                    follow_redirects=True)
        self.assertIn('Report saved.', post_response.data)
        list_response = client.get('/reports/')
        self.assertIn(self.report_data[u'details_original_name'], list_response.data)

        
    def test_update(self):
        #NOTE this tests both report and seris

        client = self.app.test_client()
        with self.app.test_request_context():
            session = database.get_session()
            row = database.ReportRow()
            row.update(self.report_data)
            session.save(row)
            session.commit()

            # clone self.report_data dict
            data = dict(self.report_data)

            #add additional info
            data.update({u'format_no_of_pages': u'2303445'})

            #update existing info
            data.update({u'header_uploader': u'Jerry Seinfeld'})

            #remove info
            del data[u'links_reference_global_level']

            edit_response = client.post('/reports/%s/edit/' %row.id, 
                            data = data,
                            follow_redirects=True)

            # checking correct flash message
            self.assertIn("Report saved.", edit_response.data)

            # checking additional info
            self.assertIn("2303445", edit_response.data)

            # checking existing info update
            self.assertIn("Jerry Seinfeld", edit_response.data)

            # checking now if the checkbox has changed to No
            label = "Global-level SOER.+s?"
            value = 'No'
            self.assertTrue(common.search_label_value(label, value, edit_response.data))


    def test_delete(self):
        client = self.app.test_client()
        with self.app.test_request_context():
            session = database.get_session()
            row = database.ReportRow(name="v323x,3240543#%")
            session.save(row)
            session.commit()

        post_response = client.post("reports/%s/delete/" %row.id)
        list_response = client.get('/reports/')
        self.assertFalse( "v323x,3240543#%" in list_response.data)
        self.assertIn("Report deleted.", list_response.data)


    def test_view_widgets(self):
        # this test 3 valued widgets where valid values are 'yes', 'no' or '-'
        # '-' is shown when no value given

        client = self.app.test_client()
        with self.app.test_request_context():
            session = database.get_session()
            row = database.ReportRow()
            row.update(self.report_data)
            session.save(row)
            session.commit()

        view_response = client.get('/reports/%s/' %row.id)
        
        # clone self.report_data dict
        data = dict(self.report_data)
        
        del data[u'details_publisher']
        with self.app.test_request_context():
            session = database.get_session()
            row.update(data)
            session.save(row)
            session.commit()

        # no value given, look for '-'
        label = 'Published by'
        value = '-'
        self.assertTrue(common.search_label_value(label, value, view_response.data))
