"""
This module contains the class that implements functionality for grabbing
RDF/RSS/Atom feeds.

It is based on the I{Universal Feed Parser} python module available at
U{http://feedparser.org/}.
"""

import feedparser
from copy import deepcopy
import urllib2

from zope.component import getUtility

from interfaces import INyFeedHarvester
from naaya.core.utils import unescape_html_entities

class NyFeed:
    """
    Class that implements functionality for grabbing RDF/RSS/Atom feeds.
    """

    def __init__(self):
        """
        Initialize variables:

        B{__feed_gone} - flag that signals that the feed URL no longer exists

        B{__feed_feed} - contains all the feed parsed data

        B{__feed_status} - HTTP status code returned when the feed was grabbed

        B{__feed_version} - feed version

        B{__feed_bozo_exception} - stores the caught exception if any

        B{__feed_encoding} - feed character encoding

        B{__feed_etag} - HTTP ETag header value

        B{__feed_modified} - HTTP last-modified date of the feed

        B{__feed_entries} - feed items
        """
        self.__feed_gone = 0
        self.__feed_feed = None
        self.__feed_status = None
        self.__feed_version = None
        self.__feed_bozo_exception = None
        self.__feed_encoding = None
        self.__feed_etag = None
        self.__feed_modified = None
        self.__feed_entries = []
        self.__feed_lang = None

    def __set_feed(self, gone=0, feed=None, status=None, version=None,
                   bozo_exception=None, encoding=None, etag=None,
                   modified=None, entries=None):
        """
        Set feed data after the feed was parsed.
        """

        self.__feed_gone = gone
        if feed is not None: self.__feed_feed = deepcopy(feed)
        else: self.__feed_feed = None
        self.__feed_status = status
        self.__feed_version = version
        self.__feed_bozo_exception = bozo_exception
        self.__feed_encoding = encoding
        self.__feed_etag = etag
        self.__feed_modified = modified
        if entries is not None:
            for entry in entries:
                if isinstance(entry, dict) and entry.has_key('title'):
                    entry['title'] = unescape_html_entities(entry['title'])
            self.__feed_entries = deepcopy(entries)
        else: self.__feed_entries = []
        self._p_changed = 1

    #api
    def get_feed_feed(self):
        """ Getter for __feed_feed """

        return self.__feed_feed
    def get_feed_gone(self):
        """ Getter for I{__feed_gone}. """

        return self.__feed_gone
    def get_feed_status(self):
        """ Getter for I{__feed_status}. """

        return self.__feed_status
    def get_feed_version(self):
        """ Getter for I{__feed_version}. """

        return self.__feed_version
    def get_feed_bozo_exception(self):
        """ Getter for I{__feed_bozo_exception}. """

        return self.__feed_bozo_exception
    def get_feed_encoding(self):
        """ Getter for I{__feed_encoding}. """

        return self.__feed_encoding
    def get_feed_etag(self):
        """ Getter for I{__feed_etag}. """

        return self.__feed_etag
    def get_feed_modified(self):
        """ Getter for I{__feed_modified}. """

        return self.__feed_modified
    def get_feed_title(self):
        """ Getter for feed title. """

        try: return self.__feed_feed.title
        except: return ''
    def get_feed_lang(self):
        """ Getter for feed language. """

        try:
            return self.__feed_feed.language.lower()
        except AttributeError:
            return None

    def get_feed_url(self):
        """
        Returns the value of the feed url (this can be stored in whatever object
        variable).

        B{Abstract method; this should be implemented by the class who extends
        I{NyFeed}.}
        """

        raise NotImplementedError, 'get_feed_url'

    def set_new_feed_url(self):
        """
        After receiving a 301 status code, the feed url must be changed.

        B{Abstract method; this should be implemented by the class who extends
        I{NyFeed}.}
        """

        raise NotImplementedError, 'set_new_feed_url'

    def get_feed_items(self):
        """ Getter for I{__feed_entries}. """

        return self.__feed_entries
    def count_feed_items(self):
        """ Returns the number of items. """

        return len(self.__feed_entries)

    def get_feed_item_title(self, item):
        """
        Returns the title of an item.
        @param item: feed item
        """

        return item['title']
    def get_feed_item_link(self, item):
        """
        Returns the URL of an item.
        @param item: feed item
        """

        return item['link']
    def get_feed_item_keys(self, item):
        """
        Returns all item keys without I{title} and I{link}.
        @param item: feed item
        """

        l_keys = item.keys()
        if 'title' in l_keys: l_keys.remove('title')
        if 'link' in l_keys: l_keys.remove('link')
        return l_keys
    def get_feed_item_value(self, item, key):
        """
        Returns an item's key value.
        @param item: feed item
        @param key: key name
        """

        value = item.get(key, None)
        if type(value) == type(u''): value = value
        return value

    def harvest_feed(self, http_proxy=None, harvester_name=None):
        """
        Handles the feed grabbing and parsing.
        """

        if harvester_name is not None:
            # Don't use the default parser; we are configured to use a custom
            # one. Let's see if we can grab it.
            try:
                harvester = getUtility(INyFeedHarvester, context=self,
                                       name=harvester_name)
            except:
                self.log_current_error()
                return

            # OK, custom parser found, run it.
            result = harvester.harvest_feed(self)
            self.__set_feed(**result)
            return

        # Default parser
        if http_proxy:
            proxy = urllib2.ProxyHandler({"http":http_proxy})
            p = feedparser.parse(self.get_feed_url(), etag=self.__feed_etag,
                                 modified=self.__feed_modified,
                                 handlers = [proxy])
        else:
            p = feedparser.parse(self.get_feed_url(), etag=self.__feed_etag,
                                 modified=self.__feed_modified)

        if p.get('bozo', 0) == 1:
            #some error occurred
            if p.has_key('status'):
                if p.status == 304:
                    #the feed was not modified; do nothing
                    self.__feed_status = p.status
                    self._p_changed = 1
                elif p.status == 301:
                    #the feed was permanently moved to a new location
                    #update the new location and also store feed stuff
                    self.set_new_feed_url(p.url)
                    if p.etag != '': etag = p.etag
                    else: etag = None
                    if p.has_key('modified'): modified = p.modified
                    else: modified = None
                    self.__set_feed(feed=p.feed, status=p.status,
                                    version=p.version, encoding=p.encoding,
                                    etag=etag,
                        modified=modified, entries=p.entries)
                elif p.status == 200:
                    #the feed was harvested but with a warning
                    #store feed stuff
                    if p.etag != '': etag = p.etag
                    else: etag = None
                    if p.has_key('modified'): modified = p.modified
                    else: modified = None
                    self.__set_feed(feed=p.feed, status=p.status,
                                    version=p.version, encoding=p.encoding,
                                    etag=etag,
                        modified=modified, entries=p.entries)
                else:
                    #don't know how to handle this; set it as error
                    error = str(p.bozo_exception)
                    self.__set_feed(bozo_exception=error)
            else:
                error = str(p.bozo_exception)
                self.__set_feed(bozo_exception=error)
        else:
            #no error; check for status
            if p.has_key('status'):
                if p.status == 301:
                    #the feed was permanently moved to a new location
                    #update the new location and also store feed stuff
                    self.set_new_feed_url(p.url)
                    if p.etag != '': etag = p.etag
                    else: etag = None
                    if p.has_key('modified'): modified = p.modified
                    else: modified = None
                    self.__set_feed(feed=p.feed, status=p.status,
                                    version=p.version, encoding=p.encoding,
                                    etag=etag,
                        modified=modified, entries=p.entries)
                elif p.status == 302:
                    #the feed was temporarily moved to a new location
                    #store feed stuff
                    if p.etag != '': etag = p.etag
                    else: etag = None
                    if p.has_key('modified'): modified = p.modified
                    else: modified = None
                    self.__set_feed(feed=p.feed, status=p.status,
                                    version=p.version, encoding=p.encoding,
                                    etag=etag,
                        modified=modified, entries=p.entries)
                elif p.status == 304:
                    #the feed was not modified; do nothing
                    self.__feed_status = p.status
                    self._p_changed = 1
                elif p.status == 200:
                    #everything is OK
                    #store feed stuff
                    if p.etag != '': etag = p.etag
                    else: etag = None
                    if p.has_key('modified'): modified = p.modified
                    else: modified = None
                    self.__set_feed(feed=p.feed, status=p.status,
                            version=p.version, encoding=p.encoding,
                            etag=etag,
                        modified=modified, entries=p.entries)
                elif p.status == 410:
                    #the feed is gone; DO NOT HARVEST ANYMORE!!!
                    self.set_new_feed_url('')
                    error = 'The feed is gone. Do not harvest it anymore!'
                    self.__set_feed(gone=1, bozo_exception=error)
                else:
                    #don't know how to handle this; set it as error
                    error = 'Don\'t know how to handle this status %s' % p.status
                    self.__set_feed(bozo_exception=error, status=p.status)
            else:
                #don't know how to handle this; set it as error
                error = 'Don\'t know how to handle this, missing status'
                self.__set_feed(bozo_exception=error)
        p = None
