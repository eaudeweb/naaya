import unittest
from unittest import mock

import feedparser

from Products.NaayaBase.NyFeed import NyFeed

RSS = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel><title>Channel</title><link>http://example.com</link>
<item><title>First &amp; ș</title><link>http://example.com/1</link>
<description>Text</description></item>
</channel></rss>"""


class DummyFeed(NyFeed):

    def get_feed_url(self):
        return 'http://example.com/rss'


class NyFeedTest(unittest.TestCase):

    def harvest(self):
        parsed = feedparser.parse(RSS)
        parsed['status'] = 200
        feed = DummyFeed()
        with mock.patch.object(feedparser, 'parse', return_value=parsed):
            feed.harvest_feed()
        return feed

    def test_harvest(self):
        feed = self.harvest()
        self.assertEqual(feed.get_feed_status(), 200)
        self.assertEqual(feed.count_feed_items(), 1)
        item = feed.get_feed_items()[0]
        self.assertEqual(feed.get_feed_item_title(item), 'First & ș')
        self.assertEqual(feed.get_feed_item_link(item), 'http://example.com/1')

    def test_item_keys(self):
        feed = self.harvest()
        item = feed.get_feed_items()[0]
        keys = feed.get_feed_item_keys(item)
        self.assertNotIn('title', keys)
        self.assertNotIn('link', keys)
        self.assertIn('summary', keys)
        self.assertEqual(feed.get_feed_item_value(item, 'summary'), 'Text')
