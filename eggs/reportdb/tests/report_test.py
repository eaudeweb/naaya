import unittest2 as unittest


def create_mock_app():
    from manage import create_app
    app = create_app()
    app.config["TESTING"] = True
    return app, lambda: None


class ReportCrudTest(unittest.TestCase):

    def setUp(self):
        self.app, app_teardown = create_mock_app()
        self.addCleanup(app_teardown)

    @unittest.expectedFailure
    def test_add(self):
        client = self.app.test_client()
        post_response = client.post('/reports', data={
            'title': u"Teh new report",
        }, follow_redirects=True)

        list_response = client.get('/reports')
        self.assertIn("Teh new report", list_response.data)
