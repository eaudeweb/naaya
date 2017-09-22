from lxml.cssselect import CSSSelector
from lxml.html import fromstring
from urllib2 import urlopen
from datetime import datetime
import time

def get_content(el, css):
    sel = CSSSelector(css)
    content = sel(el)[0]
    return content.text_content().strip()

def get_url(el):
    links = el.cssselect('span a')
    return links[0].get('href')

def convert_datestring(d):
    #convert date strings like '12 June 2011' to '2011-06-12'.
    return datetime(*(time.strptime(d, '%d %B %Y')[0:6])).strftime('%Y-%m-%d')

class Harvester(object):

    max_items = 20

    def harvest_feed(self, feed):
        """
            Extracts the first 20 news (title, date, url and description)
            from http://www.euractiv.com/en/tag/biodiversity
        """
        fp = urlopen(feed.get_feed_url())
        tree = fromstring(fp.read())

        selector = CSSSelector('div#right_one_left div.view-content')
        content_area = selector(tree)

        entries = []
        for item in content_area[0].getchildren()[:self.max_items]:
            #get only the items with the type News
            if get_content(item, css='span.views-field-type') == 'News':
                entry = {}
                entry['author'] = ''
                entry['id'] = get_url(item)
                entry['modified'] = convert_datestring(get_content(item, css='span.views-field-created'))
                entry['link'] = 'http://www.euractiv.com%s' % get_url(item)
                entry['summary'] = get_content(item, css='div.views-field-field-short-abstract-value')
                entry['title'] = get_content(item, css='span.views-field-title')
                entries.append(entry)

        return {
            'feed': {
                'link': feed.get_feed_url(),
                'title': feed.title_or_id(),
            },
            'status': fp.code,
            'version': fp.headers.getparam('content-type'),
            'encoding': fp.headers.getparam('charset'),
            'etag': None,
            'modified': fp.headers.getparam('date'),
            'entries': entries,
        }