from mock import Mock, patch
from zope import component, interface
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase

from Products.NaayaCore.SyndicationTool.RemoteChannel import manage_addRemoteChannel
from Products.NaayaBase.interfaces import INyFeedHarvester

class CustomHarvester(object):
    interface.implements(INyFeedHarvester)
    def harvest_feed(self, feed):
        return {
            'feed': Mock(),
            'status': 200,
            'version': Mock(),
            'encoding': Mock(),
            'etag': None,
            'modified': None,
            'entries': ['value one', 'value two'],
        }

class CustomHarvesterTest(NaayaTestCase):
    def setUp(self):
        manage_addRemoteChannel(self.portal['portal_syndication'],
                                id='test_channel', url="http://example.com")

    @patch('Products.NaayaBase.NyFeed.feedparser')
    def test_normal_parser(self, mock_feedparser):
        mock_result = Mock()
        mock_result.status = 200
        mock_result.etag = ''
        mock_result.entries = ['asdf', 'qwer']
        mock_feedparser.parse.return_value = mock_result
        channel = self.portal['portal_syndication']['test_channel']

        channel.updateChannel(self.portal.get_site_uid())

        self.assertEqual(channel.get_feed_items(), ['asdf', 'qwer'])

    def test_custom_harvester(self):
        channel = self.portal['portal_syndication']['test_channel']
        channel.harvester_name = 'test-harvester'
        gsm = component.getGlobalSiteManager()

        harvester = CustomHarvester()
        gsm.registerUtility(harvester, name=channel.harvester_name)
        try:
            channel.updateChannel(self.portal.get_site_uid())
        finally:
            gsm.unregisterUtility(harvester, name=channel.harvester_name)

        self.assertEqual(channel.get_feed_items(), ['value one', 'value two'])
