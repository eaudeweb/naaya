import unittest2 as unittest


class SerisReviewCrudTest(unittest.TestCase):

    def setUp(self):
        from common import create_mock_app
        self.app, app_teardown = create_mock_app()
        self.addCleanup(app_teardown)

        client = self.app.test_client()
        post_response = client.post('/reports', data={
            'title': u"Teh new report",
        })

    def test_add(self):
        client = self.app.test_client()
        post_response = client.post('/reports/1/seris_reviews', data={
            'links_global': 'on',
        })

        list_response = client.get('/reports/1/seris_reviews')
        self.assertIn('href="/reports/1/seris_reviews/1"', list_response.data)
