import os
from unittest.mock import Mock

from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.flowplayer import resources

PLAYER_DIR = os.path.join(os.path.dirname(resources.__file__), 'player')


class FlowPlayerResourcesTest(NaayaTestCase):

    def afterSetUp(self):
        # the publisher marks real requests with the browser layer
        alsoProvides(self.portal.REQUEST, IDefaultBrowserLayer)

    def test_resource_views(self):
        views = [cls for cls in vars(resources).values()
                 if isinstance(cls, type) and
                 issubclass(cls, resources.FlowPlayerBase) and
                 cls is not resources.FlowPlayerBase]
        self.assertGreater(len(views), 10)
        for cls in views:
            view = cls(self.portal, self.portal.REQUEST)
            prefix = '/++resource++flowplayer/'
            self.assertTrue(view.resource.startswith(prefix), cls)
            path = os.path.join(PLAYER_DIR, view.resource[len(prefix):])
            with open(path, 'rb') as f:
                expected = f.read()
            data = view()
            if isinstance(data, str):
                data = data.encode('utf-8')
            self.assertEqual(data, expected, cls)

    def test_registered_views(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name='flowplayer.js')
        self.assertIsInstance(view, resources.FlowPlayerJs)

    def test_subrip(self):
        ob = Mock(subtitle='1\n00:00:01,000 --> 00:00:02,000\nHi\n')
        request = Mock()
        self.assertEqual(resources.SubRip(ob, request)(), ob.subtitle)
        request.response.setHeader.assert_called_once_with(
            'content-type', 'application/octet-stream')
