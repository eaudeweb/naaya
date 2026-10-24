"""Tests in a real browser (Playwright/Chromium) against the test Zope served over HTTP."""
import atexit
import os
import threading
import unittest
from urllib.parse import urlparse

import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


class BrowserTestCase(NaayaTestCase):
    """`self.page` is a Chromium page; `self.url(path)` is the address of the test portal."""

    _browser = None
    _skip_reason = None

    @classmethod
    def _get_browser(cls):
        # started once per process (the test runner does not call setUpClass)
        if BrowserTestCase._browser is None and BrowserTestCase._skip_reason is None:
            if sync_playwright is None:
                BrowserTestCase._skip_reason = 'playwright is not installed'
            else:
                playwright = sync_playwright().start()
                try:
                    BrowserTestCase._browser = playwright.chromium.launch()
                except Exception as e:
                    playwright.stop()
                    BrowserTestCase._skip_reason = 'Chromium does not start: %s' % e
                else:
                    atexit.register(playwright.stop)
                    atexit.register(BrowserTestCase._browser.close)
        if BrowserTestCase._skip_reason:
            # CI sets NAAYA_BROWSER_TESTS=required, so a missing browser fails there
            if os.environ.get('NAAYA_BROWSER_TESTS') == 'required':
                raise RuntimeError(BrowserTestCase._skip_reason)
            raise unittest.SkipTest(BrowserTestCase._skip_reason)
        return BrowserTestCase._browser

    def setUp(self):
        import waitress.server
        browser = self._get_browser()
        self._server = waitress.server.create_server(
            self.wsgi_request, host='127.0.0.1', port=0, threads=2)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()
        self.base_url = 'http://127.0.0.1:%s' % self._server.effective_port
        self.context = browser.new_context()
        # no requests outside the test server (map tiles, fonts, analytics)
        self.context.route('**/*', self._only_local)
        self.page = self.context.new_page()
        self.js_errors = []
        self.page.on('pageerror', lambda error: self.js_errors.append(str(error)))
        try:
            super().setUp()
        except Exception:
            self._stop()
            raise

    def tearDown(self):
        try:
            super().tearDown()
        finally:
            self._stop()

    def _stop(self):
        self.context.close()
        self._server.close()
        self._server.task_dispatcher.shutdown()
        self._thread.join(5)

    def _only_local(self, route):
        if urlparse(route.request.url).hostname == '127.0.0.1':
            route.continue_()
        else:
            route.abort()

    def url(self, path=''):
        return '%s/%s/%s' % (self.base_url, self.portal.getId(), path.lstrip('/'))

    def commit(self):
        transaction.commit()

    def login(self, name='admin', password=''):
        """Log in through the login form; the cookie is kept by the browser context."""
        self.page.goto(self.url('login_html'))
        self.page.fill('input[name="__ac_name"]', name)
        self.page.fill('input[name="__ac_password"]', password)
        self.page.locator('input[name="__ac_password"]').press('Enter')
        self.page.wait_for_load_state()
