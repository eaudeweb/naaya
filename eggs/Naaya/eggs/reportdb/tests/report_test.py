import unittest2 as unittest


class ReportCrudTest(unittest.TestCase):

    def setUp(self):
        from common import create_mock_app
        self.app, app_teardown = create_mock_app()
        self.addCleanup(app_teardown)

    def test_add(self):
        client = self.app.test_client()
        post_response = client.post('/reports', data={
            'title': u"Teh new report",
        })

        list_response = client.get('/reports')
        self.assertIn("Teh new report", list_response.data)
