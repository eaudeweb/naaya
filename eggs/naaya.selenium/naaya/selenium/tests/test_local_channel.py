from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase
from naaya.content.news.news_item import addNyNews
import transaction

local_channel_data = {
    'local_title': 'Channel Test',
    'local_description': 'description of channel',
    'local_language': 'Auto-detect',
    'local_type': 'News',
    'local_meta': 'Naaya News',
    'local_no_items': 0,
}
news_data = {
    'title': 'Test news',
}
news_data_2 = {
    'title': 'Test news 2',
}


class NaayaChannelsTest(SeleniumTestCase):
    """This test case verifies the features:
    - Adding a local channel
    - Arranging the local channel's portlet on 'info' main section
    - the display of the channels portlet and the news added

    """
    def selenium_initialize_local(self, news_data, news_data_2):
        """Initializing..."""
        self.login_user('admin', '')
        addNyNews(self.portal.info, title=news_data['title'],
                  contributor='admin', submitted=1)
        addNyNews(self.portal.info, title=news_data_2['title'],
                  contributor='admin', submitted=1)
        transaction.commit()

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
        selen.wait_for_page_to_load(self._selenium_page_timeout)

    def selenium_arrange_folder_portlet(self, channel_portlet_data):
        selen = self.selenium
        selen.click("link=Arrange")
        selen.wait_for_page_to_load(self._selenium_page_timeout)
        self.assertTrue(
            selen.is_element_present("//div[@id='center_content']/"
                                     "h1[text()='Arrange portlets']"))

        selen.select("position", "value=%s"
                     % channel_portlet_data['position_label'])
        selen.select("portlet_id", "label=%s (%s)"
                     % (channel_portlet_data['title'],
                     channel_portlet_data['portlet']))
        selen.type("location", channel_portlet_data['display_url'])
        selen.click("//input[@name='action' and @value='Assign']")
        selen.wait_for_page_to_load(self._selenium_page_timeout)

        self.assertTrue(
            selen.is_element_present("//div[@id='center_content']/"
                                     "h1[text()='Arrange portlets']"))

    def selenium_verify_display(self, channel_portlet_data):
        selen = self.selenium
        selen.open("/portal/info", True)
        self.assertTrue(
            selen.is_text_present(channel_portlet_data['title']),
            "Channel  %s not displayed" % channel_portlet_data['title'])
        self.assertTrue(
            selen.is_element_present("link=%s" % news_data['title']),
            "Link %s not displayed" % news_data['title'])
        self.assertTrue(
            selen.is_element_present("link=%s" % news_data_2['title']),
            "Link %s not displayed" % news_data_2['title'])
