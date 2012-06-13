import unittest
from mock import patch
import flask
from common import create_mock_app


def setUpModule(self):
    import frame; self.frame = frame
    import views; self.views = views


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


class PermissionsTest(unittest.TestCase):

    def setUp(self):
        self.app, cleanup_app = create_mock_app()
        self.app.config['FRAME_URL'] = 'ze_frame_url'
        self.addCleanup(cleanup_app)

    def test_anything_allowed_if_authorization_is_disabled(self):
        self.app.config['SKIP_EDIT_AUTHORIZATION'] = True
        with self.app.test_request_context():
            self.assertTrue(views.edit_is_allowed())

    def test_disallow_if_frame_role_is_anonymous(self):
        with self.app.test_request_context():
            flask.g.user_roles = ['Anonymous']
            self.assertFalse(views.edit_is_allowed())

    def test_allow_if_frame_role_is_contributor(self):
        with self.app.test_request_context():
            flask.g.user_roles = ['Contributor']
            self.assertTrue(views.edit_is_allowed())


class EditPermissionDecoratorTest(unittest.TestCase):

    ok_msg = 'edit is being allowed'

    def setUp(self):
        self.app, cleanup_app = create_mock_app()
        self.addCleanup(cleanup_app)
        self.app.config['SKIP_EDIT_AUTHORIZATION'] = False
        self.mock_roles = []

        @self.app.before_request
        def set_roles():
            flask.g.user_roles = self.mock_roles

        @self.app.route('/edit_permission_test')
        @views.require_edit_permission
        def edit_permission_test():
            return self.ok_msg

    def test_allow_if_permission_available(self):
        self.mock_roles = ['Contributor']
        client = self.app.test_client()
        response = client.get('/edit_permission_test')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.ok_msg)

    def assert_not_allowed(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please log in", response.data)

    def test_disallow_if_permission_not_available(self):
        client = self.app.test_client()
        response = client.get('/edit_permission_test')
        self.assert_not_allowed(response)
        self.assertNotIn(self.ok_msg, response.data)

    def test_views_are_protected(self):
        protected_urls = [('GET', '/reports/new/'),
                          ('POST', '/reports/new/'),
                          ('GET', '/reports/13/edit/'),
                          ('POST', '/reports/13/edit/'),
                          ('POST', '/reports/13/delete/')]
        client = self.app.test_client()
        for method, url in protected_urls:
            response = client.open(url, method=method)
            self.assert_not_allowed(response)
