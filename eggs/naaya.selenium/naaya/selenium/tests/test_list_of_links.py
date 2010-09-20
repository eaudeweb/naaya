#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import re
import optparse
sys.path.append(os.path.join(os.getcwd(), '..'))

from Products.Naaya.tests.SeleniumTestCase import SeleniumTestCase

link_list_data = {
    'tid': 'TestID',
    'title': 'Linkuri de test',
}


class NaayaList_of_linksTest(SeleniumTestCase):
#This test case verifies the following Naaya features:
#    1. Introducing a new list of links with an usual id and title and portlet
#    2. Introducing a new list of links with an usual id and title without portlet
#    3. Introducing a new list of links with an usual id and an empty title
#    4. Introducing a new list of links with an usual id and a new utf8 title
#    5. Introducing a new list of links with a new utf8 id and title
#    6. Introducing a new list of links with an usual id and the title containing special chars
#    7. Introducing a new list of links with an id and title containing special chars
#        these tests also test the following:
#            the portlet of list being displayed in manage portlets
#    8. Introducing a new link in the 1. list with usual title
#    9. Introducing a new link in the 1. list with empty title
#    10. Introducing a new link in the 1. list with title containing special chars
#    11. Introducing a new link in the 1. list with number as title
#    12. Introducing a new link in the 1. list with new utf8 chars in title
#        these tests also test the following:
#            display the portlet of the list of links
#            verify the apparition of the list of links and the link on "info" as an anonymous
#            update the link by changing it's permission for anonymous
#            verify the apparition after update
    def selenium_initialize(self):
        """initializing..."""
        selen = self.selenium
        self.login_user('admin', '')
        selen.open("/portal/admin_linkslists_html", True)
        selen.wait_for_page_to_load("30000")
        self.assertTrue(selen.is_text_present("Add new list of links"))
        self.assertTrue(selen.is_element_present
                        ("//div[@id='center_content']/fieldset/legend"))

    def selenium_initialize_link(self):
        """initialize a list of links"""
        selen = self.selenium
        self.selenium_initialize()
        self.selenium_data_introduction(link_list_data)

    def test_normal_char_input(self):
        """testing usual title and ID of List of Links"""
        self.selenium_initialize()
        selen = self.selenium
        self.selenium_data_introduction(link_list_data)
        extras_tabel = selen.get_table\
                         ("//div[@id='center_content']/form/table.3.1")
        self.selenium_verify_output(extras_tabel, link_list_data)
        self.selenium_verify_portlet_presence(extras_tabel)

    def test_normal_char_input_without_portlet(self):
        """testing usual title and ID of List of Links"""
        self.selenium_initialize()
        selen = self.selenium
        self.selenium_data_introduction_wp(link_list_data)
        extras_tabel = selen.get_table\
                         ("//div[@id='center_content']/form/table.3.1")
        self.selenium_verify_output(extras_tabel, link_list_data)
        self.selenium_verify_portlet_presence(extras_tabel)

    def test_empty_link_list_title(self):
        """testing a List of Links with usual ID and blank title"""
        self.selenium_initialize()
        selen = self.selenium
        link_list_data = {
            'tid': 'IDtest03',
            'title': '',
        }
        self.selenium_data_introduction(link_list_data)
        extras_tabel = selen.get_table\
                     ("//div[@id='center_content']/form/table.3.1")
        self.selenium_verify_output(extras_tabel, link_list_data)
        self.selenium_verify_portlet_presence(extras_tabel)

    def test_utf8_link_list_title(self):
        """testing a List of Links with usual ID and a title with cyrilic characters"""
        self.selenium_initialize()
        selen = self.selenium
        link_list_data = {
            'tid': 'Idtest04',
            'title': u"стуўфхцчшщъыьэюяабвгґдеёжӂзіийј",
        }
        self.selenium_data_introduction(link_list_data)
        extras_tabel = selen.get_table\
                     ("//div[@id='center_content']/form/table.3.1")
        self.selenium_verify_output(extras_tabel, link_list_data)
        self.selenium_verify_portlet_presence(extras_tabel)

    def test_utf8_link_list_title_and_id(self):
        """testing a List of Links with cyrilic characters at ID and Title"""
        self.selenium_initialize()
        selen = self.selenium
        link_list_data = {
            'tid': u"стуўфхцчшщъыьэюяабвгґдеёжӂзіийј",
            'title': u"стуўфхцчшщъыьэюяабвгґдеёжӂзіийј",
        }
        self.selenium_data_introduction(link_list_data)
        extras_tabel = selen.get_table\
                     ("//div[@id='center_content']/form/table.3.1")
        self.selenium_verify_output(extras_tabel, link_list_data)
        self.selenium_verify_portlet_presence(extras_tabel)

    def test_special_link_list_title(self):
        """testing a List of Links with usual ID and special characters as title"""
        self.selenium_initialize()
        selen = self.selenium
        link_list_data = {
            'tid': 'IDtest06',
            'title': '!@#$%^&*()/\'',
        }
        self.selenium_data_introduction(link_list_data)
        extras_tabel = selen.get_table\
                     ("//div[@id='center_content']/form/table.3.1")
        self.selenium_verify_output(extras_tabel, link_list_data)
        self.selenium_verify_portlet_presence(extras_tabel)

    def test_special_link_list_title_and_id(self):
        """testing a List of Links with special characters as title and ID"""
        self.selenium_initialize()
        selen = self.selenium
        link_list_data = {
            'tid': '!@#$%^&*()/\'',
            'title': '!@#$%^&*()/\'',
        }
        self.selenium_data_introduction(link_list_data)
        extras_tabel = selen.get_table\
                     ("//div[@id='center_content']/form/table.3.1")
        self.selenium_verify_output(extras_tabel, link_list_data)
        self.selenium_verify_portlet_presence(extras_tabel)

    def test_normal_char_link(self):
        self.selenium_initialize_link()
        selen = self.selenium
        selen.open('portal/admin_linkslists_html',True)
        link_data = {
            'title_link': 'title link',
            'description_link': 'description link',
            'url_link': 'portal/admin_linkslists_html',
            'permission_index_link': 0,  #may be from 0 to 11
            'order_link': 0,
        }
        self.selenium_add_link(link_data, link_list_data)
        portlet_data = {
            'position_label': 'Left',  #can be left,center,right
            'display_url': 'info',
        }
        link_data['display_url'] = portlet_data['display_url']
        self.selenium_arrange_link_list(portlet_data, link_list_data)
        self.logout_user()
        self.selenium_verify_list_aparition(link_list_data, link_data)
        self.login_user('admin', '')
        self.permission_index_link = 7
        self.selenium_update_link(link_data, link_list_data)
        self.logout_user()
        self.selenium_verify_list_aparition(link_list_data, link_data)

    def test_empty_char_link(self):
        self.selenium_initialize_link()
        selen = self.selenium
        selen.open('portal/admin_linkslists_html', True)
        link_data = {
            'title_link': '',
            'description_link': '',
            'url_link': '',
            'permission_index_link': 0,  #may be from 0 to 11
            'order_link': 0,
        }
        self.selenium_add_link(link_data, link_list_data)
        portlet_data = {
            'position_label': 'Left',  #can be left,center,right
            'display_url': 'info',
        }
        link_data['display_url'] = portlet_data['display_url']
        self.selenium_arrange_link_list(portlet_data, link_list_data)
        self.logout_user()
        self.selenium_verify_list_aparition(link_list_data, link_data)
        self.login_user('admin', '')
        self.permission_index_link = 7
        self.selenium_update_link(link_data, link_list_data)
        self.logout_user()
        self.selenium_verify_list_aparition(link_list_data, link_data)

    def test_special_char_link(self):
        self.selenium_initialize_link()
        selen = self.selenium
        selen.open('portal/admin_linkslists_html', True)
        link_data = {
            'title_link': '!@#$%^&*()-=?|\//+',
            'description_link': '!@#$%^&*()-=?|\//+',
            'url_link': '!@#$%^&*()-=?|\//+',
            'permission_index_link': 0,  #may be from 0 to 11
            'order_link': 0,
        }
        self.selenium_add_link(link_data, link_list_data)
        portlet_data = {
            'position_label': 'Left',  #can be left,center,right
            'display_url': 'info',
        }
        link_data['display_url'] = portlet_data['display_url']
        self.selenium_arrange_link_list(portlet_data, link_list_data)
        self.logout_user()
        self.selenium_verify_list_aparition(link_list_data, link_data)
        self.login_user('admin', '')
        self.permission_index_link = 7
        self.selenium_update_link(link_data, link_list_data)
        self.logout_user()
        self.selenium_verify_list_aparition(link_list_data, link_data)

    def test_numbers_char_link(self):
        self.selenium_initialize_link()
        selen = self.selenium
        selen.open('portal/admin_linkslists_html', True)
        link_data = {
            'title_link': 15,
            'description_link': 15,
            'url_link': 15,
            'permission_index_link': 0,  #may be from 0 to 11
            'order_link': 0,
        }
        self.selenium_add_link(link_data, link_list_data)
        portlet_data = {
            'position_label': 'Left',  #can be left,center,right
            'display_url': 'info',
        }
        link_data['display_url'] = portlet_data['display_url']
        self.selenium_arrange_link_list(portlet_data, link_list_data)
        self.logout_user()
        self.selenium_verify_list_aparition(link_list_data, link_data)
        self.login_user('admin', '')
        self.permission_index_link = 7
        self.selenium_update_link(link_data, link_list_data)
        self.logout_user()
        self.selenium_verify_list_aparition(link_list_data, link_data)

    def test_utf8_char_link(self):
        self.selenium_initialize_link()
        selen = self.selenium
        selen.open('portal/admin_linkslists_html', True)
        link_data = {
            'title_link': u"стуўфхцчшщъыьэюяабвгґдеёжӂзіийј",
            'description_link': u"стуўфхцчшщъыьэюяабвгґдеёжӂзіийј",
            'url_link': u"стуўфхцчшщъыьэюяабвгґдеёжӂзіийј",
            'permission_index_link': 0,  #may be from 0 to 11
            'order_link': 0,
        }
        self.selenium_add_link(link_data, link_list_data)
        portlet_data = {
            'position_label': 'Left',  #can be left,center,right
            'display_url': 'info',
        }
        link_data['display_url'] = portlet_data['display_url']
        self.selenium_arrange_link_list(portlet_data, link_list_data)
        self.logout_user()
        self.selenium_verify_list_aparition(link_list_data, link_data)
        self.login_user('admin', '')
        self.permission_index_link = 7
        self.selenium_update_link(link_data, link_list_data)
        self.logout_user()
        self.selenium_verify_list_aparition(link_list_data, link_data)

    def selenium_data_introduction(self, list_data):
        selen = self.selenium
        selen.open("/portal/admin_linkslists_html", True)
        selen.type("id", list_data['tid'])
        selen.type("title", list_data['title'])
        selen.click("//input[@value='Add']")
        selen.wait_for_page_to_load("30000")
        self.assertFalse(selen.is_text_present("Error"))

    def selenium_data_introduction_wp(self, list_data):
        selen = self.selenium
        selen.type("id", list_data['tid'])
        selen.type("title", list_data['title'])
        selen.click("portlet")
        selen.click("//input[@value='Add']")
        selen.wait_for_page_to_load("30000")
        self.assertFalse(selen.is_text_present("Error"))

    def selenium_verify_output(self, out_str, list_data):
        selen = self.selenium
        in_str = list_data['title']
        if not selen.is_text_present("Saved changes"):
            self.assertTrue(selen.is_text_present('warning'),
                            'error adding a link to a list of links')
        else:
            return self.assertEqual(out_str, in_str)

    def selenium_add_link(self, link_data, list_data):
        selen = self.selenium
        selen.click("link=Lists of links")
        selen.wait_for_page_to_load("30000")
        self.assertTrue(selen.is_text_present("Add new list of links"))
        self.assertTrue(selen.is_element_present
                             ("//div[@id='center_content']/fieldset/legend"))
        selen.click("link=%s" % list_data['title'])
        selen.wait_for_page_to_load("30000")
        self.assertTrue(selen.is_element_present
            ("//div[@id='center_content']/h1[text()='Edit list of links']"))

        selen.type("//input[@name='title' and @value='']",link_data['title_link'])
        selen.type("description", link_data['description_link'])
        selen.click("relative")
        selen.type("url", link_data['url_link'])
        selen.select("permission", "index=%d" % link_data['permission_index_link'])
        selen.type("order", "%d" % link_data['order_link'])
        selen.click("//input[@value='Add']")
        selen.wait_for_page_to_load("30000")
        self.assertTrue(selen.is_element_present
                ("//div[@id='center_content']/h1[text()='Edit list of links']"))

    def selenium_arrange_link_list(self, portlet_data, list_data):
        selen = self.selenium
        selen.click("link=Arrange")
        selen.wait_for_page_to_load("30000")
        self.assertTrue(selen.is_element_present
            ("//div[@id='center_content']/h1[text()='Arrange portlets']"))
        selen.select("position", "label=%s" % portlet_data['position_label'])
        selen.select("portlet_id", "label=%s (Links list)" % list_data['title'])
        selen.type("location", portlet_data['display_url'])
        selen.click("//input[@name='action' and @value='Assign']")
        selen.wait_for_page_to_load("30000")
        self.assertTrue(selen.is_element_present
            ("//div[@id='center_content']/h1[text()='Arrange portlets']"))

    def selenium_verify_portlet_presence(self, extras_tabel):
        selen = self.selenium
        selen.click("link=Manage")
        selen.wait_for_page_to_load("30000")

        self.assertTrue(selen.is_element_present("link=List of links"),
                'linkul pe care vrei sa-l folosesti nu exista')
        selen.click("link=List of links")
        selen.wait_for_page_to_load("30000")
        self.assertTrue(selen.is_element_present
                        ("//div[@id='center_content']/fieldset/legend"))

        if selen.is_element_present("css=#center_content>form>table.datatable>"
                                        "tbody>tr:nth-child(1)>td:nth-child(1)"):
            verify_portlet = selen.get_text("css=#center_content>form>table.datatable>"
                                        "tbody>tr:nth-child(1)>td:nth-child(2)")
            self.assertTrue(extras_tabel == verify_portlet,
                        'The name of list %s is not properly introducted'
                        'in manage portlets' % extras_tabel)
        elif selen.is_element_present("css=#center_content"
                        ">fieldset>form>select>option:nth-child(4)"):
            verify_wp = selen.get_text("css=#center_content"
                ">fieldset>form>select>option:nth-child(4)")
            self.assertTrue(extras_tabel == verify_wp,
                        'The name of list %s is not properly introducted'
                        'in manage portlets' % extras_tabel)
        else:
            self.fail('The list: %s does not appear in manage portlets'
                          % extras_tabel)

    def selenium_verify_list_aparition(self, list_data, link_data):
        selen = self.selenium
        selen.open('/portal/%s' % link_data['display_url'] ,True)
        selen.wait_for_page_to_load("3000")
        try:
            table_extras = selen.get_text("//div[@id='left_port']/div/div[1]")
        except:
            self.assertTrue(selen.is_element_present
                            ("//div[@id='left_port']/div/div[2]/ul/li"),
                            'Bug:You displayed a blank link')
            self.assertEqual(list_data['title'], table_extras)

        if selen.is_element_present("link=%s" % link_data['title_link']):
            if link_data['permission_index_link'] not in (0,8):
                self.fail('BUG:Link displayed althought as an anonim you\'re'
                      'not allowed to see')
        elif link_data['permission_index_link'] in (0,8):
            self.fail('BUG:Link not displayed properly')

    def selenium_update_link(self, link_data, list_data):
        selen = self.selenium
        selen.open("/portal/admin_linkslists_html", True)

        selen.click("link=%s" % list_data['title'])
        selen.wait_for_page_to_load("30000")
        self.assertTrue(selen.is_element_present("//div[@id='center_content']"
                                                "/form[1]/fieldset/p/input"))
        selen.click("link=%s" % link_data['title_link'])
        selen.wait_for_page_to_load("30000")
        selen.select("permission", "index=%d" % link_data['permission_index_link'])
        selen.click("//div[@id='center_content']/form[1]/fieldset/p/input")
        selen.wait_for_page_to_load("30000")
        self.assertTrue(selen.is_element_present("//div[@id='center_content']"
                                                "/form[1]/fieldset/p/input"))