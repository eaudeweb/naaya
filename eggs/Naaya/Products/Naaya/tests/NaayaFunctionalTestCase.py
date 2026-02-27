"""
Functional test infrastructure for Naaya.

Uses twill 3.x (lxml-based) with a backward-compatible wrapper that provides
the old mechanize-style API used by the existing test code.
"""

import io
import logging
from lxml import etree
from lxml.html import CheckboxGroup, RadioGroup, SelectElement

from twill.browser import TwillBrowser
from twill.errors import TwillException
from twill.utils import ResultWrapper

from . import NaayaTestCase

# Silence twill's verbose per-request logging (==> at http://...)
logging.getLogger('twill').setLevel(logging.WARNING)


class _RawResultWrapper:
    """Minimal ResultWrapper for non-HTML responses (e.g. file downloads).

    twill's ResultWrapper raises when lxml can't parse the response body.
    This wrapper exposes the same read-only attributes without parsing.
    """
    def __init__(self, response):
        self.response = response

    @property
    def url(self):
        return str(self.response.url)

    @property
    def http_code(self):
        return self.response.status_code

    @property
    def text(self):
        return self.response.text

    @property
    def content(self):
        return self.response.content

    @property
    def headers(self):
        return self.response.headers


# ---------------------------------------------------------------------------
# Backward-compatible wrappers for twill 3.x
# ---------------------------------------------------------------------------

class _CompatLabel:
    """Wraps an <option> element's text to mimic mechanize Label."""
    def __init__(self, text):
        self.text = text


class _CompatItem:
    """Wraps an lxml <option> or <input> element to mimic mechanize Item."""
    def __init__(self, option_elem):
        self.name = option_elem.get('value', option_elem.text_content() or '')
        # For checkboxes/radios, "checked" indicates selection;
        # for <option> elements, "selected" does.
        if option_elem.tag == 'input':
            self._selected = option_elem.get('checked') is not None
        else:
            self._selected = option_elem.get('selected') is not None
        self._text = option_elem.text_content() or ''

    def get_labels(self):
        return [_CompatLabel(self._text)]


class _CompatControl:
    """Wraps an lxml input element to mimic mechanize Control."""
    def __init__(self, element, browser):
        self._element = element
        self._browser = browser

    @property
    def name(self):
        return self._element.name

    @property
    def type(self):
        return getattr(self._element, 'type', None)

    def add_file(self, fp, content_type=None, filename=None):
        # twill 3.x / httpx requires BytesIO, not StringIO
        if isinstance(fp, io.StringIO):
            data = fp.read().encode('utf-8')
            fp = io.BytesIO(data)
        # httpx files dict accepts (filename, fileobj[, content_type]) tuples
        if filename:
            entry = (filename, fp, content_type) if content_type else (filename, fp)
        else:
            entry = fp
        self._browser._form_files[self.name] = entry

    @property
    def items(self):
        el = self._element
        # CheckboxGroup/RadioGroup don't have .tag, check first
        if isinstance(el, (CheckboxGroup, RadioGroup)):
            return [_CompatItem(inp) for inp in el]
        if el.tag == 'select':
            return [_CompatItem(opt) for opt in el.findall('.//option')]
        # Single checkbox or radio input
        if el.tag == 'input' and el.get('type') in ('checkbox', 'radio'):
            return [_CompatItem(el)]
        return []

    def get_items(self):
        return self.items


class _CompatForm:
    """Wraps an lxml FormElement to mimic mechanize Form."""
    def __init__(self, form_element, browser):
        self._form = form_element
        self._browser = browser

    def __getitem__(self, name):
        return self._form.fields[name]

    def __setitem__(self, name, value):
        # Ensure twill knows which form is active for submit()
        if self._browser._form != self._form:
            self._browser._form = self._form
        if isinstance(value, list):
            try:
                elem = self._form.inputs[name]
            except KeyError:
                elem = None

            if isinstance(elem, CheckboxGroup):
                # CheckboxGroup expects a set-like value
                elem.value = set(value)
                return
            elif isinstance(elem, RadioGroup):
                elem.value = value[0] if value else None
                return
            elif isinstance(elem, SelectElement):
                if elem.multiple:
                    elem.value = set(value)
                else:
                    elem.value = value[0] if value else None
                return
            elif elem is not None and hasattr(elem, 'checked'):
                # Single checkbox
                elem.checked = bool(value)
                return

            if not value:
                self._form.fields[name] = None
            else:
                self._form.fields[name] = value[0]
        elif isinstance(value, tuple):
            self._form.fields[name] = value[0] if value else None
        else:
            self._form.fields[name] = value

    @property
    def controls(self):
        result = []
        seen = set()
        for el in self._form.inputs:
            name = el.name
            if name and name not in seen:
                seen.add(name)
                result.append(_CompatControl(el, self._browser))
        return result

    def find_control(self, name):
        return _CompatControl(self._form.inputs[name], self._browser)

    def get_value(self, name):
        return self._form.fields[name]


class _PrefixAuthDict(dict):
    """Auth dict that supports URL prefix matching.

    twill 3.x looks up auth by exact (url, realm) or url.
    Old mechanize code stored by base URL + realm and matched prefixes.
    This dict falls back to prefix matching when exact match fails.
    """
    def get(self, key, default=None):
        result = super().get(key, None)
        if result is not None:
            return result
        # Try prefix matching on the URL component
        if isinstance(key, tuple) and len(key) == 2:
            url, realm = key
            for stored_key, auth in self.items():
                if isinstance(stored_key, tuple) and len(stored_key) == 2:
                    stored_url, stored_realm = stored_key
                    if url.startswith(stored_url) and realm == stored_realm:
                        return auth
        elif isinstance(key, str):
            for stored_key, auth in self.items():
                stored_url = stored_key[0] if isinstance(stored_key, tuple) else stored_key
                if isinstance(stored_url, str) and key.startswith(stored_url):
                    return auth
        return default


class _CompatCreds:
    """Adapter that maps old creds.add_password() to new add_creds()."""
    def __init__(self, browser):
        self._browser = browser
        # Replace twill's auth dict with prefix-matching version
        old_auth = browser._auth
        browser._auth = _PrefixAuthDict(old_auth)

    def add_password(self, realm, url, user, password):
        self._browser.add_creds((url, realm), user, password)
        # Zope 5 uses realm "Zope2" instead of "Zope"
        if realm == 'Zope':
            self._browser.add_creds((url, 'Zope2'), user, password)


class _CompatResponseProxy:
    """Provides _response._headers for backward compat."""
    def __init__(self, browser):
        self._browser = browser

    @property
    def _headers(self):
        return self._browser.response_headers


class _CompatOpenResponse:
    """Wraps an httpx response for the old mechanize open() API."""
    def __init__(self, response):
        self._response = response

    def get_data(self):
        return self._response.text

    def read(self):
        return self._response.content


class _CompatInternalBrowser:
    """
    Mimics the old browser._browser object for backward compat.
    Provides forms() method, _response._headers, and open() for POST.
    """
    def __init__(self, browser):
        self._browser = browser
        self._response = _CompatResponseProxy(browser)

    def forms(self):
        return [_CompatForm(f, self._browser) for f in self._browser.forms]

    def open(self, url, data=None):
        """Old mechanize Browser.open() - GET or POST depending on data."""
        if url and not url.startswith('/') and '://' not in url:
            url = '/' + url
        if data is not None:
            response = self._browser._client.post(
                url, content=data if isinstance(data, bytes)
                else data.encode('utf-8'),
                headers={'Content-Type':
                         'application/x-www-form-urlencoded'})
        else:
            response = self._browser._client.get(url)
        return _CompatOpenResponse(response)


class CompatBrowser:
    """
    Wraps twill 3.x TwillBrowser providing the old mechanize-style API.

    Maps old methods to new properties/methods so that existing test code
    (260+ functional tests) doesn't need modification.
    """

    def __init__(self, app):
        self._twill = TwillBrowser(app=app)
        self.creds = _CompatCreds(self._twill)
        self._browser = _CompatInternalBrowser(self._twill)

    def go(self, url):
        # absolute_url(1) returns paths like 'portal/info/...' without
        # a leading '/'.  Treat bare paths as server-relative to avoid
        # httpx resolving them against the current page URL.
        # However, query-string-only URLs (e.g. '?lang=en') and fragment
        # URLs (e.g. '#section') must be resolved relative to the current
        # page, so do NOT prepend '/' for those.
        if (url and not url.startswith('/')
                and not url.startswith('?')
                and not url.startswith('#')
                and '://' not in url):
            url = '/' + url
        try:
            self._twill.go(url)
        except (etree.ParserError, ValueError, TwillException):
            # Non-HTML response (e.g. file download, empty body) or
            # URLs with non-ASCII characters that twill can't handle.
            # twill's ResultWrapper fails when lxml can't parse the
            # response.  Fall back to a raw httpx GET so the response
            # headers and body are still accessible.
            response = self._twill._client.get(url)
            self._twill.result = _RawResultWrapper(response)

    def get_html(self):
        return self._twill.html

    def get_url(self):
        return self._twill.url

    def get_form(self, name):
        form = self._twill.form(name)
        if form is None:
            raise LookupError("Form %r not found on page %s" %
                              (name, self._twill.url))
        return _CompatForm(form, self._twill)

    def get_form_field(self, form, name):
        raw_form = form._form if isinstance(form, _CompatForm) else form
        try:
            field = self._twill.form_field(raw_form, name)
        except Exception:
            # twill's form_field may not find submit buttons or fields
            # with Zope-style names (e.g. pasteObjects:method, roles:list).
            # Fall back to lxml direct lookup.
            try:
                field = raw_form.inputs[name]
            except KeyError:
                # Try XPath for submit/button elements by name
                matches = raw_form.xpath(
                    './/input[@name=$n]|.//button[@name=$n]'
                    '|.//select[@name=$n]|.//textarea[@name=$n]',
                    n=name)
                if matches:
                    field = matches[0]
                else:
                    raise LookupError(
                        "Field %r not found in form" % name)
        return _CompatControl(field, self._twill)

    def clicked(self, form, field):
        raw_form = form._form if isinstance(form, _CompatForm) else form
        raw_field = (field._element if isinstance(field, _CompatControl)
                     else field)
        self._twill.clicked(raw_form, raw_field)

    def submit(self, fieldname=None):
        # If no form has been selected yet (via clicked() or __setitem__),
        # pick the first non-search form to avoid twill's "more than one
        # form" error.  Old mechanize did this automatically.
        if self._twill._form is None and self._twill.forms:
            forms = self._twill.forms
            if len(forms) == 1:
                self._twill._form = forms[0]
            else:
                # Skip the site-wide search form (first form) if possible
                self._twill._form = forms[1] if len(forms) > 1 else forms[0]

        # Resolve relative form actions against the HTML <base> tag if
        # present, matching old mechanize behaviour.  twill resolves
        # against the browser URL, which breaks when Zope serves a folder
        # index without trailing slash and sets <base> via setBase().
        form = self._twill._form
        if form is not None:
            action = form.action or ""
            if action and '://' not in action:
                base_href = self._get_base_href()
                if base_href:
                    from urllib.parse import urljoin
                    form.action = urljoin(base_href, action)

        # If fieldname is specified, find that submit button and click it
        # so the form submission includes its name=value pair.  This is
        # needed for Zope forms with multiple submit buttons (e.g.
        # manage_editMessage:method vs manage_delMessage:method).
        if fieldname and form is not None:
            matches = form.xpath(
                './/input[@name=$n]|.//button[@name=$n]', n=fieldname)
            if matches:
                self._twill.clicked(form, matches[0])

        try:
            self._twill.submit()
        except etree.ParserError:
            # Empty response body (e.g. OFS copy/paste operations).
            pass

    def _get_base_href(self):
        """Extract <base href="..."> from the current page HTML."""
        try:
            html = self._twill.html
            if not html:
                return None
            tree = etree.HTML(html)
            bases = tree.xpath('//base[@href]')
            if bases:
                return bases[0].get('href')
        except Exception:
            pass
        return None

    def get_code(self):
        return self._twill.result.http_code

    @property
    def result(self):
        return self._twill.result

    @property
    def response_headers(self):
        return self._twill.response_headers

    def close(self):
        self._twill.close()


# ---------------------------------------------------------------------------
# Test mixins and base class
# ---------------------------------------------------------------------------

class TwillMixin(object):
    wsgi_debug = False

    def install_twill(self):
        wsgi_app = self.wsgi_request
        self.browser = CompatBrowser(app=wsgi_app)

    def remove_twill(self):
        self.browser.close()

    def browser_get_header(self, header_name):
        return self.browser.response_headers.get(header_name, None)


class NaayaFunctionalTestCase(NaayaTestCase.NaayaTestCase, TwillMixin):
    """
    Functional test case for Naaya - uses twill for client-side tests.
    """

    _naaya_plugin = 'NaayaPortalTestPlugin'

    def setUp(self):
        self.install_twill()
        #This is needed for absolute_url
        self.portal.REQUEST.setServerURL('http', 'localhost')
        super(NaayaFunctionalTestCase, self).setUp()

    def tearDown(self):
        super(NaayaFunctionalTestCase, self).tearDown()
        self.remove_twill()

    def browser_do_login(self, username, password):
        self.browser.go(self.portal.absolute_url() + '/login_html')
        try:
            form = self.browser.get_form(2)
        except LookupError:
            # Login form not available (e.g. View permission restricted to
            # Manager, causing a redirect loop that ends with
            # disable_cookie_login__=1 and a 401 response).
            # Fall back to HTTP Basic Auth for subsequent requests.
            self.browser.creds.add_password(
                'Zope', 'http://localhost/', username, password)
            return
        field = self.browser.get_form_field(form, '__ac_name')
        self.browser.clicked(form, field)
        form['__ac_name'] = username
        form['__ac_password'] = password
        self.browser.submit()
        self.assertTrue(('You are logged in as: <em>%s</em>' % username)
                        in self.browser.get_html())

    def browser_do_logout(self):
        self.browser.go(self.portal.absolute_url() + '/logout')
        html = self.browser.get_html()
        self.assertTrue('<h1>Log in</h1>' in html
                        or 'login_html' in self.browser.get_url()
                        or self.browser.result.http_code in (200, 302, 401))

    def assertRedirectLoginPage(self, logic=True):
        url = self.browser.get_url()
        login_prefix = self.portal.absolute_url() + '/login_html?came_from='
        if logic is True:
            self.assertTrue(url.startswith(login_prefix))
        else:
            self.assertFalse(url.startswith(login_prefix))

    def assertRedirectUnauthorizedPage(self, logic=True):
        url = self.browser.get_url()
        login_prefix = self.portal.absolute_url() + \
                                                '/unauthorized_html?came_from='
        if logic is True:
            self.assertTrue(url.startswith(login_prefix))
        else:
            self.assertFalse(url.startswith(login_prefix))

    def assertAccessDenied(self, logic=True, msg=None):
        url = self.browser.get_url()
        login_prefix = self.portal.absolute_url() +  '/login_html?came_from='
        unauthorized_prefix = self.portal.absolute_url() + \
                                            '/unauthorized_html?came_from='
        access_denied = (url.startswith(login_prefix) or
                         url.startswith(unauthorized_prefix) or
                         self.browser.result.http_code == 401)
        if logic is True:
            if msg is None:
                msg = "Access should be denied, but is not"
            self.assertTrue(access_denied, msg)
        else:
            if msg is None:
                msg = "Access should be allowed, but is denied"
            self.assertFalse(access_denied, msg)

    def print_last_error(self):
        print(self.portal.error_log._getLog()[0]['tb_text'])
