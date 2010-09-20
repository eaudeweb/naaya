#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import re
import optparse

from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase

local_channel_data = {
    'local_title': 'Channel Test',
    'local_description': 'description of channel',
    'local_language': 'Auto-detect',
    'local_type': 'News',
    'local_meta': 'Naaya News',
    'local_no_items': 0,
}
news_data = {
    'news_title': 'Test news',
    'description': 'news description',
    'geo_coverage': 'Region',
    'keywords': 'test,something',
    'comments': True,
    'sort_order': '',
    'release_date': '',  #like dd/mm/yyyy
    'details': '',
    'expiration_date': '',  #like dd/mm/yyyy
    'concerned_url': '',
    'source': '',
}
news_data_2 = {
    'news_title': 'Test news 2',
    'description': 'about testing',
    'geo_coverage': 'OneCountry',
    'keywords': 'test,something,python,selenium',
    'comments': True,
    'sort_order': '',
    'release_date': '',  #like dd/mm/yyyy
    'details': '',
    'expiration_date': '',  #like dd/mm/yyyy
    'concerned_url': '',
    'source': '',
}


class NaayaChannelsTest(SeleniumTestCase):
    #This test case verifies the features:
    #1. Adding a local channel
    #2. Arranging the local channel's portlet on 'info'
    #3. the display of the channels portlet and the news added
    def selenium_initialize_local(self, news_data, news_data_2):
        """Initializing..."""
        self.login_user('admin', '')
        self.selenium_add_news(news_data)
        self.selenium_add_news(news_data_2)

    def test_local_channel(self):
        self.selenium_initialize_local(news_data, news_data_2)
        self.selenium_add_local_channel(local_channel_data)
        channel_portlet_data = {
            'portlet': 'Local channel',
            'position_label': 'left',  #can be left,center,right
            'display_url': 'info',
        }
        channel_portlet_data['title'] = local_channel_data['local_title']
        self.selenium_arrange_folder_portlet(channel_portlet_data)
        self.selenium_verify_display(channel_portlet_data)

    def selenium_add_local_channel(self, local_channel_data):
        selen = self.selenium
        selen.open("/portal/admin_localchannels_html", True)

        selen.type("title", local_channel_data['local_title'])
        selen.type("description", local_channel_data['local_description'])
        selen.select("//select[@name='language']", 
                    "label=%s" % local_channel_data['local_language'])
        selen.select("type", "label=%s" % local_channel_data['local_type'])
        selen.add_selection("objmetatype", 
                            "label=%s" % local_channel_data['local_meta'])
        selen.type("numberofitems", local_channel_data['local_no_items'])
        selen.click("//input[@value='Add']")
        selen.wait_for_page_to_load("30000")

    def selenium_arrange_folder_portlet(self, channel_portlet_data):
        selen = self.selenium
        selen.click("link=Arrange")
        selen.wait_for_page_to_load("30000")

        self.failUnless(selen.is_element_present
                ("//div[@id='center_content']/h1[text()='Arrange portlets']"))

        selen.select("position", "value=%s" % channel_portlet_data['position_label'])
        selen.select("portlet_id", "label=%s (%s)" % (channel_portlet_data['title'],
                                            channel_portlet_data['portlet']))
        selen.type("location", channel_portlet_data['display_url'])
        selen.click("//input[@name='action' and @value='Assign']")
        selen.wait_for_page_to_load("30000")

        self.failUnless(selen.is_element_present
                ("//div[@id='center_content']/h1[text()='Arrange portlets']"))

    def selenium_verify_display(self, channel_portlet_data):
        selen = self.selenium
        selen.open("/portal/info", True)
        self.assertTrue(selen.is_text_present(channel_portlet_data['title']),
                    "Channel  %s not displayed" % channel_portlet_data['title'])
        self.assertTrue(selen.is_element_present("link=%s" % news_data['news_title']),
                            "Link %s not displayed" % news_data['news_title'])
        self.assertTrue(selen.is_element_present("link=%s" % news_data_2['news_title']),
                            "Link %s not displayed" % news_data_2['news_title'])

    def selenium_add_news(self, news_data):
        """add news without picture"""
        selen = self.selenium
        selen.open("/portal/info", True)
        selen.select("typetoadd", "value=news_add_html")
        selen.wait_for_page_to_load("30000")

        selen.type("title", news_data['news_title'])
        selen.type("coverage", news_data['geo_coverage'])
        selen.type("keywords", news_data['keywords'])
        if not news_data['release_date']:
            selen.click("link=Today")
        else:
            selen.type("releasedate", news_data['releade_date'])
        if news_data['comments']:
            selen.click("discussion")
        if news_data['expiration_date']:
            selen.type("expirationdate", news_data['expiration_date'])
        selen.type("resourceurl", news_data['concerned_url'])
        selen.type("source", news_data['source'])
        selen.click("//input[@value='Submit']")
        selen.wait_for_page_to_load("30000")