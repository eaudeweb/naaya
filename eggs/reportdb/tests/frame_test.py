import unittest
from mock import patch
import flask
from common import create_mock_app


def setUpModule():
    global frame
    import frame


class FrameTest(unittest.TestCase):

    def setUp(self):
        self.app, cleanup_app = create_mock_app()
        self.app.config['FRAME_URL'] = 'ze_frame_url'
        self.addCleanup(cleanup_app)
        requests_patch = patch('frame.requests')
        self.mock_requests = requests_patch.start()
        self.addCleanup(requests_patch.stop)
        self.mock_requests.get.return_value.status_code = 200
        self.mock_requests.get.return_value.headers = {
            'content-type': 'application/json'}
        self._set_frame_response({'frame_html': "hello framed page!"})

    def _set_frame_response(self, value):
        self.mock_requests.get.return_value.text = flask.json.dumps(value)

    def test_frame_html(self):
        with self.app.test_request_context():
            frame.get_frame_before_request()
            html = flask.render_template('frame.html')
            self.assertEqual(html, 'hello framed page!')

    def test_reports_page_has_frame(self):
        self._set_frame_response({
            'frame_html': "hello framed page! <!-- block_content -->",
        })
        client = self.app.test_client()
        response = client.get('/reports/')
        self.assertIn("hello framed page!", response.data)
        self.assertIn("No reports yet", response.data)

    def test_frame_not_called_if_url_blank(self):
        self.app.config['FRAME_URL'] = None
        with self.app.test_request_context():
            frame.get_frame_before_request()
            self.assertEqual(self.mock_requests.get.call_count, 0)

    def test_ignore_error_frame_response(self):
        self._set_frame_response({})
        self.mock_requests.get.return_value.status_code = 500
        client = self.app.test_client()
        response = client.get('/reports/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("No reports yet", response.data)

    def test_forwarded_cookies(self):
        self.app.config['FRAME_COOKIES'] = ['my-cookie-thing']
        client = self.app.test_client()
        client.set_cookie('/', 'my-cookie-thing', 'some-zope-id')
        client.get('/reports/')
        self.mock_requests.get.assert_called_once_with(
            "ze_frame_url", cookies={'my-cookie-thing': 'some-zope-id'})

    def test_get_user_id(self):
        self._set_frame_response({'user_id': 'smith'})
        with self.app.test_request_context():
            frame.get_frame_before_request()
            self.assertEqual(flask.g.user_id, 'smith')

    def test_get_user_roles(self):
        self._set_frame_response({'user_roles': ['Anonymous', 'Contributor']})
        with self.app.test_request_context():
            frame.get_frame_before_request()
            self.assertEqual(flask.g.user_roles, ['Anonymous', 'Contributor'])
