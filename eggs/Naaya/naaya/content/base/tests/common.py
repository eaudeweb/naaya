"""
Common content tests
====================

Pluggable content code conforms to a set of interfaces. The tests here are
designed to be subclassed by each content type, to test this common behaviour.
Several classes are provided so that each content type can choose to run a
subset of the tests.
"""

import re

import transaction
from webob import Request
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.NyFolder import addNyFolder
from naaya.core.testutils import parse_html, css


IMAGE_PATH_SPEC = 'Products.Naaya:skel/layout/skin/scheme/trash.gif'

# Zope 5 includes the default port in generated URLs (:80 for http,
# :443 for https) while Zope 2 omitted it. Strip it for comparisons.
_DEFAULT_PORT_RE = re.compile(r'(https?)://([^/:]+):(80|443)(/)')


def _strip_default_port(url):
    return _DEFAULT_PORT_RE.sub(r'\1://\2\4', url)


def _normalize_host(url):
    """Normalize ``nohost`` → ``localhost`` so that URLs obtained from
    Python objects (which use the default Zope test host ``nohost``) can
    be compared with URLs extracted from rendered HTML (where the test
    request sets ``HTTP_HOST: localhost``)."""
    return url.replace('://nohost/', '://localhost/')


class _IconTests(NaayaTestCase):
    """
    Common tests for Naaya content objects

    `ob`
        Object under test. Created by `setUp`.
    """

    def add_object(self, parent):
        """ Create and return an instance of the class to be tested. """
        raise NotImplementedError

    def setUp(self):
        if type(self) is _IconTests:
            self.skipTest('Abstract base class')
        addNyFolder(self.portal, 'box', contributor='contributor', submitted=1)
        self.ob = self.add_object(self.portal['box'])
        transaction.commit()

    def _get_h1_icon_src(self):
        request = Request.blank(self.ob.absolute_url())
        request.environ['HTTP_HOST'] = 'localhost'
        page = parse_html(request.get_response(self.wsgi_request).body)
        return _strip_default_port(css(page, 'h1 img')[0].attrib['src'])

    def _get_folder_icon_src(self):
        request = Request.blank(self.ob.aq_parent.absolute_url())
        request.environ['HTTP_HOST'] = 'localhost'
        request.headers['Authorization'] = 'Basic YWRtaW46'  # admin:
        page = parse_html(request.get_response(self.wsgi_request).body)
        ob_url = _normalize_host(self.ob.absolute_url())
        for tr in css(page, 'table#folderfile_list tr'):
            links = [_strip_default_port(a.attrib['href'])
                     for a in css(tr, 'td a')]
            if ob_url in links:
                break
        else:
            self.fail("Link to object %r not found" % self.ob)

        return _strip_default_port(css(tr, 'td img')[0].attrib['src'])

    def _customize_icon(self):
        scheme = self.portal.getLayoutTool().getCurrentSkinScheme()
        name = self.ob.meta_type.replace(' ', '_')
        scheme.manage_addDiskFile(id=name + '-icon', pathspec=IMAGE_PATH_SPEC)
        return scheme[name + '-icon']

    def _customize_icon_marked(self):
        scheme = self.portal.getLayoutTool().getCurrentSkinScheme()
        name = self.ob.meta_type.replace(' ', '_')
        scheme.manage_addDiskFile(id=name + '-icon-marked', pathspec=IMAGE_PATH_SPEC)
        return scheme[name + '-icon-marked']

    def test_index_page_icon(self):
        self.assertEqual(self._get_h1_icon_src(),
                         _normalize_host(self.ob.icon))

        df = self._customize_icon()
        transaction.commit()
        self.assertEqual(self._get_h1_icon_src(),
                         _normalize_host(df.absolute_url()))

        self.ob.approveThis(0, None)
        transaction.commit()
        self.assertEqual(self._get_h1_icon_src(),
                         _normalize_host(df.absolute_url()))

        df.aq_parent.manage_delObjects([df.getId()])
        transaction.commit()
        self.assertEqual(self._get_h1_icon_src(),
                         _normalize_host(self.ob.icon_marked))

        df_marked = self._customize_icon_marked()
        transaction.commit()
        self.assertEqual(self._get_h1_icon_src(),
                         _normalize_host(df_marked.absolute_url()))

    def test_folder_listing_icon(self):
        self.assertEqual(self._get_folder_icon_src(),
                         _normalize_host(self.ob.icon))

        df = self._customize_icon()
        transaction.commit()
        self.assertEqual(self._get_folder_icon_src(),
                         _normalize_host(df.absolute_url()))

        self.ob.approveThis(0, None)
        transaction.commit()
        self.assertEqual(self._get_folder_icon_src(),
                         _normalize_host(df.absolute_url()))

        df.aq_parent.manage_delObjects([df.getId()])
        transaction.commit()
        self.assertEqual(self._get_folder_icon_src(),
                         _normalize_host(self.ob.icon_marked))

        df_marked = self._customize_icon_marked()
        transaction.commit()
        self.assertEqual(self._get_folder_icon_src(),
                         _normalize_host(df_marked.absolute_url()))
