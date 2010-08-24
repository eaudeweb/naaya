# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania
#
#
#
#$Id: EWInstaller.py 11693 2008-09-11 08:52:49Z bulanmir $


#Python imports
import xmlrpclib
from urlparse import urlparse
import rotor

#Zope imports
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

#Product imports
from constants import *
from Products.EWPublisher.constants import *
from Products.EWApplications.constants import *
from Products.EWPublisher.EWCore.UtilsTool.session_tool import session_tool
from Products.EWPublisher.EWCore.UtilsTool.utils import utils
from Products.EWPublisher.EWContent.EWSite import manage_addEWSite
from BasicAuthTransport import BasicAuthTransport

#check if RDFCalendar product is present
try:
    from Products.RDFCalendar.RDFCalendar import manage_addRDFCalendar
    flagRDFCalendar = 1
except:
    flagRDFCalendar = 0
#check if LinkChecker product is present
try:
    from Products.LinkChecker.LinkChecker import manage_addLinkChecker
    flagLinkChecker = 1
except:
    flagLinkChecker = 0
#check if MessageBoard product is present
try:
    from Products.MessageBoard.MessageBoard import manage_addMessageBoard
    flagMessageBoard = 1
except:
    flagMessageBoard = 0
#check if ManagedMeetings product is present
try:
    from Products.ManagedMeetings.ManagedMeetings import manage_addManagedMeetings
    flagManagedMeetings = 1
except:
    flagManagedMeetings = 0
#check if HelpDeskAgent product is present
try:
    from Products.HelpDeskAgent.HelpDesk import manage_addHelpDesk
    flagHelpDeskAgent = 1
except:
    flagHelpDeskAgent = 0
#check if GoogleSearchInterface product is present
try:
    from Products.GoogleSearchInterface.GoogleSearchInterface import manage_addGoogleSearchInterface
    flagGoogleSearchInterface = 1
except:
    flagGoogleSearchInterface = 0
#check if ChangeNotification product is present
try:
    from Products.ChangeNotification.NotificationsFolder import manage_addNotificationsFolder
    flagChangeNotification = 1
except:
    flagChangeNotification = 0

def addEWInstaller(self, REQUEST=None):
    """ """
    ob = EWInstaller(EWINSTALLER_ID, EWINSTALLER_TITLE)
    self._setObject(EWINSTALLER_ID, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class EWInstaller(SimpleItem,
    session_tool,
    utils):

    meta_type = METATYPE_EWINSTALLER
    icon = 'misc_/EWInstaller/EWInstaller.gif'

    manage_options = SimpleItem.manage_options

    def __init__(self, id, title):
        #constructor
        self.id = id
        self.title = title
        session_tool.__dict__['__init__'](self)
        utils.__dict__['__init__'](self)

    #security stuff
    security = ClassSecurityInfo()

    # API
    def getEWInstaller(self):
        #return this object
        return self

    __known_products = {
            'Helpdesk ticketing': {'id': 'helpdesk', 'title': 'HelpDesk-Agent', 'notify_add': 1, 'notify_modify': 1, 'mail_from_address': '', 'add_issue_email_subject': 'HelpDesk Agent: new issue posted', 'update_issue_email_subject': 'HelpDesk Agent: issue modification', 'delete_issue_email_subject': 'HelpDesk Agent: issue deleted', 'add_issue_comment_email_subject': 'HelpDesk Agent: new comment to issue posted', 'update_issue_comment_email_subject': 'HelpDesk Agent: comment modification', 'delete_issue_comment_email_subject': 'HelpDesk Agent: comment deleted', 'issue_ticket_length': 15, 'security': 'private', 'default_priority': 1},
            'Calendar of events': {'id': 'calendar', 'title': 'Calendar of events', 'first_day_week': 'Monday', 'week_day_len': 3},
            'Meeting management': {'id': 'meetings', 'title': 'Folder for meetings', 'description':'', 'event_types': [], 'mailhost': 'Mailhost'},
            'Message board': {'id': 'messageboard', 'title': 'Message Board', 'description':'Discussion forum', 'mailhost': 'MailHost'},
            'Notifications on uploads': {'id': 'notificationstool', 'title': 'Notifications on uploads', 'news_metatypes': [METATYPE_EWNEWS, METATYPE_EWEVENT], 'upload_metatypes': [METATYPE_EWDOCUMENT, METATYPE_EWFILE], 'folder_metatypes': [METATYPE_EWFOLDER], 'subject_line': 'Notifications', 'news_line': 'Newsletter', 'from_address': 'Postmaster', 'timeout': 2, 'method_use': 'crontab', 'work_mode': 1, 'modifications': 1, 'notification_immediate': 0, 'notification_daily': 0, 'notification_weekly': 0},
            'Remote links checking': {'id': 'linkchecker', 'title': 'Remote links checking'},
            'Google search interface': {'id': 'googlesearch', 'title': 'Google Search Interface', 'search_type': 0}
        }

    def getProductsStruct(self, p_struct):
        #returns the products dictionary
        return p_struct['products']

    def getProductsEmptyStruct(self, p_products):
        #returns an empty dictionary with info about all known products
        l_res = {}
        for l_product in p_products:
            if self.__known_products.has_key(l_product):
                l_res[l_product] = self.__known_products[l_product]
        return l_res


    def getProductToConfigure(self, p_struct, p_product=''):
        #given a product id, it returns the previous, current and next product id
        #that will be processed in the wizard
        l_prev = l_current = l_next = None
        l_keys = p_struct['products'].keys()
        if p_product == '':
            #the first one
            if len(l_keys)>0: l_current = l_keys[0]
            if len(l_keys)>1: l_next = l_keys[1]
        else:
            l_index = l_keys.index(p_product)
            if l_index>0: l_prev = l_keys[l_index-1]
            l_current = p_product
            if l_index+1<len(l_keys): l_next = l_keys[l_index+1]
        return l_prev, l_current, l_next

    def getPrevNextLinkForProductsPage(self, p_struct, p_product=''):
        #return the 'Previous' ans 'Next' links for products page
        if p_product == '':
            l_keys = p_struct['products'].keys()
            if len(l_keys)>0: l_prev_link = 'install_products_html?product=%s' % l_keys[-1]
            else: l_prev_link = 'install_step3_html'
            l_next_link = ''
        else:
            l_prev, l_current, l_next = self.getProductToConfigure(p_struct, p_product)
            if l_prev is not None: l_prev_link = 'install_products_html?product=%s' % l_prev
            else: l_prev_link = 'install_step3_html'
            if l_next is not None: l_next_link = 'install_products_html?product=%s' % l_next
            else: l_next_link = 'install_confirm_html'
        return l_prev_link, l_next_link

    def getKeyForProduct(self, p_struct, p_product, p_key):
        #return the value for given product key
        return p_struct['products'][p_product][p_key]

    def setKeyForProduct(self, p_struct, p_product, p_key, p_value):
        #set the value for given product key
        p_struct['products'][p_product][p_key] = p_value

    # Wizard methods
    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'getInstallData')
    def getInstallData(self, location='', id='', site_title='', subtitle='', description='', publisher='',
        contributor='', creator='', rights='', language='', http_proxy='',
        mail_server_name='localhost', mail_server_port=25, administrator_email='', administrator_name='', portal_url='', contact_email='',
        number_latest_uploads=5, number_announcements=5, topic='', category='', category_url='', products=None, skin='eionet', colourscheme='orange',
        notify_on_errors=0, DestinationURL='manage_main', status='', status_message_mail='',  ewindows_portal_url='', applications_url='', username='', password='', site_icon=None, main_topic_a_title='',  main_topic_b_title='', main_topic_c_title='', main_topic_d_title='', application_url=''):
        #builds a dictionary representing all the data needed to create a portal
        l_dict = {
            'location':location, 'id':id, 'site_title':site_title, 'subtitle':subtitle, 'description':description, 'publisher':publisher,'contributor':contributor, 'creator':creator, 'rights':rights, 'language':language, 'http_proxy':http_proxy, 'mail_server_name':mail_server_name, 'mail_server_port':mail_server_port, 'administrator_email':administrator_email, 'administrator_name':administrator_name, 'portal_url':portal_url, 'contact_email':contact_email, 'number_latest_uploads':number_latest_uploads, 'number_announcements':number_announcements, 'topic': topic, 'category':category, 'category_url':category_url, 'products': products, 'skin':skin, 'colourscheme':colourscheme, 'notify_on_errors':notify_on_errors, 'DestinationURL': DestinationURL, 'status': status, 'status_message_mail': status_message_mail,  'ewindows_portal_url': ewindows_portal_url, 'applications_url':applications_url, 'username':username, 'password': password, 'site_icon':site_icon, 'main_topic_a_title':main_topic_a_title, 'main_topic_b_title':main_topic_b_title,  'main_topic_c_title':main_topic_c_title, 'main_topic_d_title':main_topic_d_title, 'application_url':application_url
        }
        #if site_icon is not None:
        #    site_icon = site_icon.read()
        #else:
        #    site_icon = None

        if products is None: products = []
        else: products = self.utConvertToList(products)
        return l_dict

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_init')
    def install_init(self, location='', id='', site_title='', subtitle='', description='', publisher='', contributor='', creator='', rights='', language='', http_proxy='', mail_server_name='localhost', mail_server_port=25, administrator_email='', administrator_name='', portal_url='', contact_email='', number_latest_uploads=5, number_announcements=5, topic='', category='', category_url='', products=None, skin='eionet', colourscheme='orange', notify_on_errors=0, DestinationURL='manage_main',  status='', status_message_mail='',  ewindows_portal_url='', applications_url='', username='', password='', site_icon=None, main_topic_a_title='', main_topic_b_title='', main_topic_c_title='', main_topic_d_title='', application_url=''):
        """ """
        if products is None: products = []
        else: products = self.utConvertToList(products)
        self.setSession(SESSION_INSTALL_DATA,
            self.getInstallData(location, id, site_title, subtitle, description, publisher, contributor, creator, rights, language, http_proxy, mail_server_name, mail_server_port, administrator_email, administrator_name, portal_url, contact_email, number_latest_uploads, number_announcements, topic, category, category_url, products, skin, colourscheme, notify_on_errors, DestinationURL, status, status_message_mail,  ewindows_portal_url, applications_url, username, password, site_icon, main_topic_a_title, main_topic_b_title, main_topic_c_title, main_topic_d_title, application_url
            )
        )

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_abort')
    def install_abort(self, REQUEST):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        DestinationURL = install_data['DestinationURL']
        REQUEST.SESSION.delete('install_data')
        if DestinationURL == 'manage_main': return self.manage_main(self, REQUEST, update_menu=1)
        else: return REQUEST.RESPONSE.redirect('%s?action=abort' % DestinationURL)

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_location_process')
    def install_location_process(self, location='', REQUEST=None):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        install_data['location'] = location
        self.setSession(SESSION_INSTALL_DATA, install_data)
        REQUEST.RESPONSE.redirect('install_step1_html')

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_step1_process')
    def install_step1_process(self, id='', site_title='', subtitle='', description='', publisher='', contributor='', creator='', rights='', language='', REQUEST=None):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        install_data['id'] = id
        install_data['site_title'] = site_title
        install_data['subtitle'] = subtitle
        install_data['description'] = description
        install_data['publisher'] = publisher
        install_data['contributor'] = contributor
        install_data['language'] = language
        install_data['creator'] = creator
        install_data['rights'] = rights
        self.setSession(SESSION_INSTALL_DATA, install_data)
        REQUEST.RESPONSE.redirect('install_step2_html')

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_step2_process')
    def install_step2_process(self, http_proxy='', mail_server_name='', mail_server_port='', administrator_email='', portal_url='', number_latest_uploads='', number_announcements='', notify_on_errors='', REQUEST=None):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        install_data['http_proxy'] = http_proxy
        install_data['mail_server_name'] = mail_server_name
        install_data['mail_server_port'] = mail_server_port
        install_data['administrator_email'] = administrator_email
        install_data['portal_url'] = portal_url
        try: install_data['number_latest_uploads'] = abs(int(number_latest_uploads))
        except: install_data['number_latest_uploads'] = 5
        try: install_data['number_announcements'] = abs(int(number_announcements))
        except: install_data['number_announcements'] = 5
        if notify_on_errors: install_data['notify_on_errors'] = 1
        else: install_data['notify_on_errors'] = 0
        self.setSession(SESSION_INSTALL_DATA, install_data)
        REQUEST.RESPONSE.redirect('install_step3_html')

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_step3_process')
    def install_step3_process(self, skin='eionet', eionet_colourscheme='orange', autumn_colourscheme='brown', metal_colourscheme='blue', REQUEST=None):
        """ """
        colourscheme = eval(skin + '_colourscheme')
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        install_data['skin'] = skin
        install_data['colourscheme'] = colourscheme
        self.setSession(SESSION_INSTALL_DATA, install_data)
        #are there any other products to be configured?
        l_prev, l_current, l_next = self.getProductToConfigure(install_data)
        if l_current is not None: REQUEST.RESPONSE.redirect('install_products_html?product=%s' % l_current)
        else: REQUEST.RESPONSE.redirect('install_confirm_html')

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_products_process')
    def install_products_process(self, product, REQUEST):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        #process current product values
        if product == 'Calendar of events':
            #process form
            l_id = REQUEST.get('id', '')
            l_title = REQUEST.get('title', '')
            l_first_day_week = REQUEST.get('first_day_week', 'Monday')
            l_week_day_len = REQUEST.get('week_day_len', 3)
            try: l_week_day_len = abs(int(l_week_day_len))
            except: l_week_day_len = 3
            #set values
            self.setKeyForProduct(install_data, product, 'id', l_id)
            self.setKeyForProduct(install_data, product, 'title', l_title)
            self.setKeyForProduct(install_data, product, 'first_day_week', l_first_day_week)
            self.setKeyForProduct(install_data, product, 'week_day_len', l_week_day_len)
        elif product == 'Remote links checking':
            #process form
            l_id = REQUEST.get('id', '')
            l_title = REQUEST.get('title', '')
            #set values
            self.setKeyForProduct(install_data, product, 'id', l_id)
            self.setKeyForProduct(install_data, product, 'title', l_title)
        elif product == 'Message board':
            #process form
            l_id = REQUEST.get('id', '')
            l_title = REQUEST.get('title', '')
            l_description = REQUEST.get('description', '')
            #set values
            self.setKeyForProduct(install_data, product, 'id', l_id)
            self.setKeyForProduct(install_data, product, 'title', l_title)
            self.setKeyForProduct(install_data, product, 'description', l_description)
        elif product == 'Meeting management':
            #process form
            l_id = REQUEST.get('id', '')
            l_title = REQUEST.get('title', '')
            l_description = REQUEST.get('description', '')
            l_event_types = self.utConvertLinesToList(REQUEST.get('event_types', []))
            #set values
            self.setKeyForProduct(install_data, product, 'id', l_id)
            self.setKeyForProduct(install_data, product, 'title', l_title)
            self.setKeyForProduct(install_data, product, 'description', l_description)
            self.setKeyForProduct(install_data, product, 'event_types', l_event_types)
        elif product == 'Helpdesk ticketing':
            #process form
            l_id = REQUEST.get('id', '')
            l_title = REQUEST.get('title', '')
            if REQUEST.has_key('notify_add'): l_notify_add = 1
            else: l_notify_add = 0
            if REQUEST.has_key('notify_modify'): l_notify_modify = 1
            else: l_notify_modify = 0
            l_mail_from_address = REQUEST.get('mail_from_address', '')
            l_add_issue_email_subject = REQUEST.get('add_issue_email_subject', '')
            l_update_issue_email_subject = REQUEST.get('update_issue_email_subject', '')
            l_delete_issue_email_subject = REQUEST.get('delete_issue_email_subject', '')
            l_add_issue_comment_email_subject = REQUEST.get('add_issue_comment_email_subject', '')
            l_update_issue_comment_email_subject = REQUEST.get('update_issue_comment_email_subject', '')
            l_delete_issue_comment_email_subject = REQUEST.get('delete_issue_comment_email_subject', '')
            l_issue_ticket_length = REQUEST.get('issue_ticket_length', '15')
            try: l_issue_ticket_length = abs(int(l_issue_ticket_length))
            except: l_issue_ticket_length = 15
            l_security = REQUEST.get('security', 'private')
            l_default_priority = REQUEST.get('default_priority', '1')
            try: l_default_priority = abs(int(l_default_priority))
            except: l_default_priority = 1
            #set values
            self.setKeyForProduct(install_data, product, 'id', l_id)
            self.setKeyForProduct(install_data, product, 'title', l_title)
            self.setKeyForProduct(install_data, product, 'notify_add', l_notify_add)
            self.setKeyForProduct(install_data, product, 'notify_modify', l_notify_modify)
            self.setKeyForProduct(install_data, product, 'mail_from_address', l_mail_from_address)
            self.setKeyForProduct(install_data, product, 'add_issue_email_subject', l_add_issue_email_subject)
            self.setKeyForProduct(install_data, product, 'update_issue_email_subject', l_update_issue_email_subject)
            self.setKeyForProduct(install_data, product, 'delete_issue_email_subject', l_delete_issue_email_subject)
            self.setKeyForProduct(install_data, product, 'add_issue_comment_email_subject', l_add_issue_comment_email_subject)
            self.setKeyForProduct(install_data, product, 'update_issue_comment_email_subject', l_update_issue_comment_email_subject)
            self.setKeyForProduct(install_data, product, 'delete_issue_comment_email_subject', l_delete_issue_comment_email_subject)
            self.setKeyForProduct(install_data, product, 'issue_ticket_length', l_issue_ticket_length)
            self.setKeyForProduct(install_data, product, 'security', l_security)
            self.setKeyForProduct(install_data, product, 'default_priority', l_default_priority)
        elif product == 'Google search interface':
            #process form
            l_title = REQUEST.get('title', '')
            l_search_type = REQUEST.get('search_type', '')
            try: l_search_type = abs(int(l_search_type))
            except: l_search_type = 0
            #set values
            self.setKeyForProduct(install_data, product, 'title', l_title)
            self.setKeyForProduct(install_data, product, 'search_type', l_search_type)
        elif product == 'Notifications on uploads':
            #process form
            l_id = REQUEST.get('id', '')            
            l_title = REQUEST.get('title', '')
            l_news_metatypes = self.utConvertLinesToList(REQUEST.get('news_metatypes', []))
            l_upload_metatypes = self.utConvertLinesToList(REQUEST.get('upload_metatypes', []))
            l_folder_metatypes = self.utConvertLinesToList(REQUEST.get('folder_metatypes', []))
            l_subject_line = REQUEST.get('subject_line', '')
            l_news_line = REQUEST.get('news_line', '')
            l_from_address = REQUEST.get('from_address', '')
            l_timeout = REQUEST.get('timeout', 2)
            try: l_timeout = abs(int(l_timeout))
            except: l_timeout = 2
            l_method_use = REQUEST.get('method_use', 'crontab')
            l_from_address = REQUEST.get('from_address', '')
            l_work_mode = REQUEST.get('work_mode', '1')
            try: l_work_mode = abs(int(l_work_mode))
            except: l_work_mode = 1
            if REQUEST.has_key('modifications'): l_modifications = 1
            else: l_modifications = 0
            if REQUEST.has_key('notification_immediate'): l_notification_immediate = 1
            else: l_notification_immediate = 0
            if REQUEST.has_key('notification_daily'): l_notification_daily = 1
            else: l_notification_daily = 0
            if REQUEST.has_key('notification_weekly'): l_notification_weekly = 1
            else: l_notification_weekly = 0
            #set values
            self.setKeyForProduct(install_data, product, 'id', l_id)
            self.setKeyForProduct(install_data, product, 'title', l_title)
            self.setKeyForProduct(install_data, product, 'news_metatypes', l_news_metatypes)
            self.setKeyForProduct(install_data, product, 'upload_metatypes', l_upload_metatypes)
            self.setKeyForProduct(install_data, product, 'folder_metatypes', l_folder_metatypes)
            self.setKeyForProduct(install_data, product, 'subject_line', l_subject_line)
            self.setKeyForProduct(install_data, product, 'news_line', l_news_line)
            self.setKeyForProduct(install_data, product, 'from_address', l_from_address)
            self.setKeyForProduct(install_data, product, 'timeout', l_timeout)
            self.setKeyForProduct(install_data, product, 'method_use', l_method_use)
            self.setKeyForProduct(install_data, product, 'work_mode', l_work_mode)
            self.setKeyForProduct(install_data, product, 'modifications', l_modifications)
            self.setKeyForProduct(install_data, product, 'notification_immediate', l_notification_immediate)
            self.setKeyForProduct(install_data, product, 'notification_daily', l_notification_daily)
            self.setKeyForProduct(install_data, product, 'notification_weekly', l_notification_weekly)
        #are there any other products to be configured?
        l_prev, l_current, l_next = self.getProductToConfigure(install_data, product)
        if l_next is not None: REQUEST.RESPONSE.redirect('install_products_html?product=%s' % l_next)
        else: REQUEST.RESPONSE.redirect('install_confirm_html')

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_finish')
    def install_finish(self, REQUEST):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        if install_data['location'] == '': l_location = self.utGetROOT()
        else: l_location = self.unrestrictedTraverse(install_data['location'], self.utGetROOT())

        #create the portal with the default structure
        id = self.utCleanupId(install_data['id'])
        if not id: id = PREFIX_EWSITE + self.utGenRandomId(6)
        manage_addEWSite(l_location, id, install_data['site_title'], install_data['site_title'], install_data['subtitle'],
            install_data['description'], install_data['publisher'], install_data['contributor'],
            install_data['creator'], install_data['rights'], install_data['language'], install_data['number_latest_uploads'],
            install_data['number_announcements'], install_data['http_proxy'],
            install_data['mail_server_name'], int(install_data['mail_server_port']), install_data['administrator_email'],
            install_data['portal_url'], install_data['notify_on_errors'],
            install_data['skin'], install_data['colourscheme'])
        ob = l_location._getOb(id)

        #used for adding in quicklinks portlet the links to additional products, if any
        quicklinks = ob.getPortletsTool().getLinksListById('quicklinks')

        #add a link to the new created ewsite in application's index
        self.unrestrictedTraverse(install_data['application_url']).ewsite_id = ob.absolute_url()

        #add EWFolders
        if install_data['main_topic_a_title'] != '':
            ob.addEWFolder('', install_data['main_topic_a_title'], '', '', '', '', '10', '', install_data['administrator_email'])
        if install_data['main_topic_b_title'] != '':
            ob.addEWFolder('', install_data['main_topic_b_title'], '', '', '', '', '20', '', install_data['administrator_email'])
        if install_data['main_topic_c_title'] != '':
            ob.addEWFolder('', install_data['main_topic_c_title'], '', '', '', '', '30', '', install_data['administrator_email'])
        if install_data['main_topic_d_title'] != '':
            ob.addEWFolder('', install_data['main_topic_d_title'], '', '', '', '', '40', '', install_data['administrator_email'])

        #the EWfolders added above, will be main topics
        maintopics = [x.id for x in ob.getMainEWFolders()]
        ob.getPropertiesTool().manageMainTopics(maintopics)

        #add user and role (admin)
        if install_data['username'] != '' and install_data['password'] != '':
            ob.getAuthenticationTool().manage_addUser(install_data['username'], install_data['password'], install_data['password'], ['Manager'], '', install_data['administrator_name'], install_data['administrator_name'], install_data['administrator_email'])
        try: REQUEST.SESSION.delete('site_errors')
        except: pass
        try: REQUEST.SESSION.delete('site_infos')
        except: pass

        #add a logo in /portal_templates - EWLogo.gif
        try:
            img_ob = ob.getTemplateTool()._getOb('EWLogo.gif')
            img_ob.update_data(data=install_data['site_icon'])
        except:
            pass

        #additional products
        for l_product in self.getProductsStruct(install_data).keys():
            if l_product == 'Calendar of events':
                if flagRDFCalendar == 1:
                    #product is present, add instance
                    if quicklinks is not None:
                        quicklinks.add_link_item('calendar', 'Calendar of Events', 'Calendar of Events', '/calendar', '1', '', '10')
                    manage_addRDFCalendar(ob,
                        self.getKeyForProduct(install_data, l_product, 'id'),
                        self.getKeyForProduct(install_data, l_product, 'title'),
                        self.getKeyForProduct(install_data, l_product, 'first_day_week'),
                        self.getKeyForProduct(install_data, l_product, 'week_day_len')
                    )
            elif l_product == 'Remote links checking':
                if flagLinkChecker == 1:
                    #product is present, add instance
                    manage_addLinkChecker(ob,
                        self.getKeyForProduct(install_data, l_product, 'id'),
                        self.getKeyForProduct(install_data, l_product, 'title')
                    )
            elif l_product == 'Message board':
                if flagMessageBoard == 1:
                    if quicklinks is not None:
                        quicklinks.add_link_item('messageboard', 'Message board', 'Message Board', '/messageboard', '1', '', '30')
                    #product is present, add instance
                    manage_addMessageBoard(ob,
                        self.getKeyForProduct(install_data, l_product, 'id'),
                        self.getKeyForProduct(install_data, l_product, 'title'),
                        self.getKeyForProduct(install_data, l_product, 'description'),
                        500000,
                        self.getKeyForProduct(install_data, l_product, 'mailhost'),
                        0
                    )
            elif l_product == 'Meeting management':
                if flagManagedMeetings == 1:
                    #product is present, add instance
                    manage_addManagedMeetings(ob,
                        self.getKeyForProduct(install_data, l_product, 'id'),
                        self.getKeyForProduct(install_data, l_product, 'title'),
                        self.getKeyForProduct(install_data, l_product, 'description'),
                        self.getKeyForProduct(install_data, l_product, 'event_types'),
                        self.getKeyForProduct(install_data, l_product, 'mailhost')
                    )
            elif l_product == 'Helpdesk ticketing':
                if flagHelpDeskAgent == 1:
                    if quicklinks is not None:
                        quicklinks.add_link_item('helpdesk', 'Helpdesk Agent', 'Helpdesk Agent', '/helpdesk', '1', '', '20')
                    #product is present, add instance
                    manage_addHelpDesk(ob,
                        self.getKeyForProduct(install_data, l_product, 'id'),
                        self.getKeyForProduct(install_data, l_product, 'title'),
                        '%s/%s' % (ob.absolute_url(1), EWUSER_ID),
                        ob.mail_server_name, ob.mail_server_port,
                        self.getKeyForProduct(install_data, l_product, 'notify_add'),
                        self.getKeyForProduct(install_data, l_product, 'notify_modify'),
                        self.getKeyForProduct(install_data, l_product, 'mail_from_address'),
                        self.getKeyForProduct(install_data, l_product, 'add_issue_email_subject'),
                        self.getKeyForProduct(install_data, l_product, 'update_issue_email_subject'),
                        self.getKeyForProduct(install_data, l_product, 'delete_issue_email_subject'),
                        self.getKeyForProduct(install_data, l_product, 'add_issue_comment_email_subject'),
                        self.getKeyForProduct(install_data, l_product, 'update_issue_comment_email_subject'),
                        self.getKeyForProduct(install_data, l_product, 'delete_issue_comment_email_subject'),
                        self.getKeyForProduct(install_data, l_product, 'issue_ticket_length'),
                        self.getKeyForProduct(install_data, l_product, 'security'),
                        self.getKeyForProduct(install_data, l_product, 'default_priority')
                    )
            elif l_product == 'Google search interface':
                if flagGoogleSearchInterface == 1:
                    #product is present, add instance
                    manage_addGoogleSearchInterface(ob,
                        self.getKeyForProduct(install_data, l_product, 'title'),
                        self.getKeyForProduct(install_data, l_product, 'search_type')
                    )
            elif l_product == 'Notifications on uploads':
                if flagChangeNotification == 1:
                    if quicklinks is not None:
                        quicklinks.add_link_item('notificationstool', 'Notifications Tool', 'Notifications Tool', '/notificationstool', '1', '', '40')
                    manage_addNotificationsFolder(ob,
                        self.getKeyForProduct(install_data, l_product, 'id'),
                        self.getKeyForProduct(install_data, l_product, 'title'),
                        self.getKeyForProduct(install_data, l_product, 'news_metatypes'),
                        self.getKeyForProduct(install_data, l_product, 'upload_metatypes'),
                        self.getKeyForProduct(install_data, l_product, 'folder_metatypes'),
                        ob.title,
                        self.getKeyForProduct(install_data, l_product, 'subject_line'),
                        self.getKeyForProduct(install_data, l_product, 'news_line'),
                        self.getKeyForProduct(install_data, l_product, 'from_address'),
                        self.getKeyForProduct(install_data, l_product, 'timeout'),
                        self.getKeyForProduct(install_data, l_product, 'method_use'),
                        self.getKeyForProduct(install_data, l_product, 'work_mode'),
                        self.getKeyForProduct(install_data, l_product, 'modifications'),
                        self.getKeyForProduct(install_data, l_product, 'notification_immediate'),
                        self.getKeyForProduct(install_data, l_product, 'notification_daily'),
                        self.getKeyForProduct(install_data, l_product, 'notification_weekly')
                    )

#        # create YihawURL in EnviroWindows
#        is_featured_partner=''
#        if install_data['topic'] != '':
#            p_topic_url = install_data['topic'].replace('publisher.finsiel.ro/ew', 'ewindows.eu.org')
#            is_featured_partner = """
#Your portal is an EnviroWindows Featured Partner Site, under the category
#%s.
#A link to your new portal has been added on the EnviroWindows website, in the folder:
#%s
#
#                """ % (install_data['category'], p_topic_url)
#            self.addEWURLs(install_data['site_title'], install_data['description'], ob.absolute_url(), install_data['topic'], install_data['category_url'], '')
        #finish
        # send emails to appliants: administrator and contact
        p_to = [install_data['administrator_email'], install_data['contact_email']]
        new_status = APPLICATION_STATUS_APPROVED
        p_from = self.unrestrictedTraverse( install_data['applications_url']).email_from
        manuale = 'http://publisher.finsiel.ro/manuals'
        p_subject = 'Your portal application on EnviroWindows has been approved'
        p_content = """
You have applied for an EnviroWindows-compliant portal hosted on the EnviroWindows servers.
The application has been approved and your portal has been created at:
%s

An account was created for you on this portal with management rights:
Username: %s
Password: %s

In order to get help on content contribution and portal administration, please consult:
%s

Regards,
EnviroWindows Team

****************************************************
IMPORTANT NOTICE: This is an automatic service.
Please do not reply to this message.
****************************************************
        """ % (ob.absolute_url(), install_data['username'], install_data['password'], manuale)
        self.unrestrictedTraverse(install_data['ewindows_portal_url']).getEmailTool().sendGenericEmail(p_content, p_to, p_from, p_subject)

        DestinationURL = install_data['DestinationURL']
        self.delSession(SESSION_INSTALL_DATA)
        if DestinationURL == 'manage_main': return self.manage_main(self, REQUEST, update_menu=1)
        else: return REQUEST.RESPONSE.redirect('%s?action=finish' % DestinationURL)

    def addEWURLs(self, p_title, p_description, p_url, p_topic_folder_url, p_category_url, p_language):
        #adds two EWURL objects: one in the specified location and one in the specified category
        #connect to server
        try:
            self.getEWSite().methods.set_fps(p_topic_folder_url, p_title, p_description, p_url, p_category_url)
        except:
            pass

    # Wizard pages
    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_template_html')
    install_template_html = PageTemplateFile('zpt/install_template', globals())

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_location_html')
    install_location_html = PageTemplateFile('zpt/install_location', globals())

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_welcome_html')
    install_welcome_html = PageTemplateFile('zpt/install_welcome', globals())

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_step1_html')
    install_step1_html = PageTemplateFile('zpt/install_step1', globals())

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_step2_html')
    install_step2_html = PageTemplateFile('zpt/install_step2', globals())

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_step3_html')
    install_step3_html = PageTemplateFile('zpt/install_step3', globals())

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_products_html')
    install_products_html = PageTemplateFile('zpt/install_products', globals())

    security.declareProtected(PERMISSION_PUBLISH_EWOBJECTS, 'install_confirm_html')
    install_confirm_html = PageTemplateFile('zpt/install_confirm', globals())

InitializeClass(EWInstaller)
