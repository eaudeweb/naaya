import unittest2 as unittest


class ReportCrudTest(unittest.TestCase):

    def setUp(self):
        from common import create_mock_app
        self.app, app_teardown = create_mock_app()
        self.addCleanup(app_teardown)

    def test_add(self):
        client = self.app.test_client()
        post_response = client.post('/reports/new/', data={
            'format_availability_paper_or_web': 'paper only',
            'header_uploader': 'Report Guru',
            'format_lang_of_pub': 'ro',
            'details_original_name': 'Teh new report',
            'format_availability_costs': 'free',
            'header_country': 'Romania',
            'details_original_language': 'ro',
            'global_level': 'on',
        })
        list_response = client.get('/reports/')
        self.assertIn("Teh new report", list_response.data)
