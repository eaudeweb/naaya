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
#$Id: EWInstaller.py 3981 2005-06-30 12:12:40Z baciuadr $


#Python imports
import xmlrpclib
from urlparse import urlparse

#Zope imports
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

#Product imports
from constants import *
from Products.EnviroWindowsApplications.constants import *
from BasicAuthTransport import BasicAuthTransport
from Products.EnviroWindows.EnviroWindowsSite import manage_addEnviroWindowsSite
from Products.EnviroWindows.EnviroWindowsSite import EnviroWindowsSite
from Products.Naaya.NySite import NySite
from Products.NaayaBase.constants import *
from Products.Naaya.constants import *
from Products.NaayaCore.LayoutTool import LayoutTool
from Products.NaayaCore.managers.session_manager import session_manager
from Products.NaayaCore.managers.utils import utils, list_utils, batch_utils, file_utils


#check if LinkChecker product is present
try:
    from Products.NaayaLinkChecker.LinkChecker import manage_addLinkChecker
    from Products.NaayaLinkChecker.LinkChecker import LinkChecker
    flagNaayaLinkChecker = 1
except:
    flagNaayaLinkChecker = 0
#check if MessageBoard product is present
try:
    from Products.NaayaForum.NyForum import manage_addNyForum
    flagNaayaForum = 1
except:
    flagNaayaForum = 0

def addEWInstaller(self, REQUEST=None):
    """ """
    ob = EWInstaller(EWINSTALLER_ID, EWINSTALLER_TITLE)
    self._setObject(EWINSTALLER_ID, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class EWInstaller(SimpleItem,
    session_manager,
    utils):

    meta_type = METATYPE_EWINSTALLER
    icon = 'misc_/EnviroWindowsInstaller/EWInstaller.gif'

    manage_options = SimpleItem.manage_options

    def __init__(self, id, title):
        #constructor
        self.id = id
        self.title = title
        session_manager.__dict__['__init__'](self)
        utils.__dict__['__init__'](self)

    #security stuff
    security = ClassSecurityInfo()

    # API
    def getEWInstaller(self):
        #return this object
        return self

    __known_products = {
            'Discussion forum': {'id': 'discussion_forum', 'title': 'Discussion forum', 'description':'Discussion forum', 'mailhost': 'MailHost'},
            'Remote links checking': {'id': 'portal_linkchecker', 'title': 'Remote links checking'},
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
        if isinstance(p_struct['products'], dict):
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
            l_keys = isinstance(p_struct['products'], dict) and\
                    p_struct['products'].keys() or []
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
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getInstallData')
    def getInstallData(self, location='', id='', site_title='', subtitle='', description='', publisher='',contributor='', creator='', rights='', languages=[],
                       http_proxy='', mail_server_name='localhost', mail_server_port=25, administrator_email='', administrator_name='', portal_url='',
                       contact_email='', number_latest_uploads=5, number_announcements=5, products=None,
                       skin='envirowindows', skin_style='EW-skin-00', notify_on_errors=0, DestinationURL='manage_main', status='', status_message_mail='',
                       ewindows_portal_url='', applications_url='', username='', password='', site_logo=None, application_url=''):

        if products is None: products = {}
        if site_logo is None: site_logo = ''

        #builds a dictionary representing all the data needed to create a portal
        l_dict = {
            'location':location, 'id':id, 'site_title':site_title, 'subtitle':subtitle, 'description':description, 'publisher':publisher,
            'contributor':contributor, 'creator':creator, 'rights':rights, 'languages':languages, 'http_proxy':http_proxy, 'mail_server_name':mail_server_name,
            'mail_server_port':mail_server_port, 'administrator_email':administrator_email, 'administrator_name':administrator_name, 'portal_url':portal_url,
            'contact_email':contact_email, 'number_latest_uploads':number_latest_uploads, 'number_announcements':number_announcements, 'products': products,
            'skin':skin, 'skin_style':skin_style, 'notify_on_errors':notify_on_errors, 'DestinationURL': DestinationURL, 'status': status, 'status_message_mail': status_message_mail,
            'ewindows_portal_url': ewindows_portal_url, 'applications_url':applications_url, 'username':username, 'password': password, 'site_logo':site_logo, 'application_url':application_url
        }


        return l_dict

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_init')
    def install_init(self, location='', id='', site_title='', subtitle='', description='', publisher='', contributor='', creator='', rights='',
                     languages=[], http_proxy='', mail_server_name='localhost', mail_server_port=25, administrator_email='', administrator_name='',
                     portal_url='', contact_email='', number_latest_uploads=5, number_announcements=5, products=None, skin='envirowindows', skin_style='EW-skin-00', notify_on_errors=0, DestinationURL='manage_main',  status='',
                     status_message_mail='',  ewindows_portal_url='', applications_url='', username='', password='', site_logo=None, application_url=''):
        """ """
        if products is None: products = {}
        if site_logo is None: site_logo = ''

        self.setSession(SESSION_INSTALL_DATA,
            self.getInstallData(location, id, site_title, subtitle, description, publisher, contributor, creator, rights, languages, http_proxy,
                                mail_server_name, mail_server_port, administrator_email, administrator_name, portal_url, contact_email, number_latest_uploads,
                                number_announcements, products, skin, skin_style, notify_on_errors, DestinationURL, status,
                                status_message_mail, ewindows_portal_url, applications_url, username, password, site_logo, application_url
            )
        )

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_abort')
    def install_abort(self, REQUEST):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        DestinationURL = install_data['DestinationURL']
        REQUEST.SESSION.delete('install_data')
        if DestinationURL == 'manage_main': return self.manage_main(self, REQUEST, update_menu=1)
        else: return REQUEST.RESPONSE.redirect('%s?action=abort' % DestinationURL)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_location_process')
    def install_location_process(self, location='', REQUEST=None):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        install_data['location'] = location
        self.setSession(SESSION_INSTALL_DATA, install_data)
        REQUEST.RESPONSE.redirect('install_step1_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_step1_process')
    def install_step1_process(self, id='', site_title='', subtitle='', description='', publisher='', contributor='', creator='', rights='', languages=[], REQUEST=None):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        install_data['id'] = id
        install_data['site_title'] = site_title
        install_data['subtitle'] = subtitle
        install_data['description'] = description
        install_data['publisher'] = publisher
        install_data['contributor'] = contributor
        if type(languages) != type([]):
            install_data['languages'] = [languages]
        else:
            install_data['languages'] = languages
        install_data['creator'] = creator
        install_data['rights'] = rights
        self.setSession(SESSION_INSTALL_DATA, install_data)
        REQUEST.RESPONSE.redirect('install_step2_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_step2_process')
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

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_step3_process')
    def install_step3_process(self, theMasterList, theSlaveList, REQUEST=None):
        """ """
        layout_tool = self.getLayoutTool()
        layout_list = layout_tool.getDataForLayoutSettings()[2]
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        if install_data['skin'] == theMasterList and install_data['skin_style'] == theSlaveList:
            pass
        else:
            install_data['skin'] = theMasterList
            install_data['skin_style'] = theSlaveList

        for skin in layout_list:
            if skin[0] == theMasterList:
                install_data['skin_name'] = skin[1]
        if 'skin_name' not in install_data:
            raise ValueError('No skin master match for %s' % theMasterList)

        for skin in layout_list:
            for style in skin[2]:
                if style[1] == theSlaveList:
                    install_data['skin_style_name'] = style[0]
        if 'skin_style_name' not in install_data:
            raise ValueError('No skin slave match for %s' % theSlaveList)

        self.setSession(SESSION_INSTALL_DATA, install_data)
        #are there any other products to be configured?
        l_prev, l_current, l_next = self.getProductToConfigure(install_data)
        if l_current is not None: REQUEST.RESPONSE.redirect('install_products_html?product=%s' % l_current)
        else:
            REQUEST.RESPONSE.redirect('install_confirm_html')


    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_products_process')
    def install_products_process(self, product, REQUEST):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        #process current product values
        if product == 'Remote links checking':
            #process form
            l_id = REQUEST.get('id', '')
            l_title = REQUEST.get('title', '')
            #set values
            self.setKeyForProduct(install_data, product, 'id', l_id)
            self.setKeyForProduct(install_data, product, 'title', l_title)

        elif product == 'Discussion forum':
            #process form
            l_id = REQUEST.get('id', '')
            l_title = REQUEST.get('title', '')
            l_description = REQUEST.get('description', '')
            #set values
            self.setKeyForProduct(install_data, product, 'id', l_id)
            self.setKeyForProduct(install_data, product, 'title', l_title)
            self.setKeyForProduct(install_data, product, 'description', l_description)

        #are there any other products to be configured?
        l_prev, l_current, l_next = self.getProductToConfigure(install_data, product)
        if l_next is not None: REQUEST.RESPONSE.redirect('install_products_html?product=%s' % l_next)
        else: REQUEST.RESPONSE.redirect('install_confirm_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_finish')
    def install_finish(self, REQUEST):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        if install_data['location'] == '': l_location = self.utGetROOT()
        else: l_location = self.unrestrictedTraverse(install_data['location'], self.utGetROOT())

        #create the portal with the default structure
        id = self.utCleanupId(install_data['id'])
        if not id: id = PREFIX_SITE + self.utGenRandomId(6)
        manage_addEnviroWindowsSite(l_location, id=id, title=install_data['site_title'])
        ob = l_location._getOb(id)

        #add user and role (admin)
        if install_data['username'] != '' and install_data['password'] != '':
            ob.getAuthenticationTool().manage_addUser(install_data['username'], install_data['password'], install_data['password'], ['Manager'], '', install_data['administrator_name'], install_data['administrator_name'], install_data['administrator_email'])
        try: REQUEST.SESSION.delete('site_errors')
        except: pass
        try: REQUEST.SESSION.delete('site_infos')
        except: pass

        #add and set defaut language
        properties_tool = ob.getPropertiesTool()
        for lang in install_data['languages']:
            properties_tool.manage_addLanguage(lang)
        #properties_tool.manage_changeDefaultLang(install_data['language'])

        #change portal metadata
        ob.admin_metadata(
            site_title=install_data['site_title'],
            site_subtitle=install_data['subtitle'],
            description=install_data['description'],
            publisher=install_data['publisher'],
            contributor=install_data['contributor'],
            creator=install_data['creator'],
            rights=install_data['rights'],
            )

        #change portal layout
        ob.admin_layout(
            theMasterList=install_data['skin'],
            theSlaveList=install_data['skin_style']
            )

        #change portal logo
        if install_data['site_logo'] != 'Nothing':
            image_ob = ob.getLayoutTool()._getOb('logo.gif')
            image_ob.update_data(data=install_data['site_logo'])
            image_ob._p_changed=1

        #administrator area
        ob.admin_email(mail_server_name=install_data['mail_server_name'],
                       mail_server_port=install_data['mail_server_port'],
                       administrator_email=install_data['administrator_email'],
                       notify_on_errors_email=install_data['notify_on_errors']
                       )
        ob.admin_properties(http_proxy=install_data['http_proxy'],
                            portal_url=install_data['portal_url']
                            )


        #latest uploads & news
        ob.portal_syndication.latestuploads_rdf.manageProperties(title='Latest uploads',
                                                                 description='Latest uploads',
                                                                 numberofitems=install_data['number_latest_uploads']
                                                                 )

        ob.portal_syndication.latestnews_rdf.manageProperties(title='Latest news',
                                                                 description='Latest news',
                                                                 numberofitems=install_data['number_announcements']
                                                                 )

        #additional products
        for l_product in self.getProductsStruct(install_data).keys():
            if l_product == 'Remote links checking':
                if flagNaayaLinkChecker == 1:
                    #product is present, add instance

                    manage_addLinkChecker(ob,
                        self.getKeyForProduct(install_data, l_product, 'id'),
                        self.getKeyForProduct(install_data, l_product, 'title')
                    )
                    linkchecker_metatype = ['Naaya URL', 'Naaya Folder', 'Naaya Document']

                    ob.portal_linkchecker.use_catalog = 1
                    ob.portal_linkchecker.catalog_name="portal_catalog"
                    ob.portal_linkchecker.batch_size = 20

                    #add default Linkchecker metatype
                    for meta in linkchecker_metatype:
                        ob.portal_linkchecker.manage_addMetaType(MetaType=meta)
                        if meta == 'Naaya URL':
                            ob.portal_linkchecker.manage_addProperty(MetaType=meta, Property='description')
                            ob.portal_linkchecker.manage_addProperty(MetaType=meta, Property='locator')

                        elif meta == 'Naaya Folder':
                            ob.portal_linkchecker.manage_addProperty(MetaType=meta, Property='description')

                        elif meta == 'Naaya Document':
                            ob.portal_linkchecker.manage_addProperty(MetaType=meta, Property='description')
                            ob.portal_linkchecker.manage_addProperty(MetaType=meta, Property='body')

            elif l_product == 'Discussion forum':
                if flagNaayaForum == 1:
                   #product is present, add instance
                    manage_addNyForum(ob,
                        self.getKeyForProduct(install_data, l_product, 'id'),
                        self.getKeyForProduct(install_data, l_product, 'title'),
                        self.getKeyForProduct(install_data, l_product, 'description')
                        )
                    current_per = ob.getAuthenticationTool().getPermission('Add comments')
                    current_per['permissions'].append('Add Naaya Forum Message')

                    ob.getAuthenticationTool().editPermission(name='Authenticated', permissions=current_per)

        # send emails to appliants: administrator and contact
        p_to = [install_data['administrator_email'], install_data['contact_email']]
        new_status = APPLICATION_STATUS_APPROVED
        p_from = self.unrestrictedTraverse(install_data['applications_url']).email_from
        #p_from = self.
        manuale = 'http://ew.eea.europa.eu/naaya/'
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
        self.unrestrictedTraverse(install_data['ewindows_portal_url']).getEmailTool().sendEmail(p_content, p_to, p_from, p_subject)

        DestinationURL = install_data['DestinationURL']
        self.delSession(SESSION_INSTALL_DATA)
        if DestinationURL == 'manage_main': return self.manage_main(self, REQUEST, update_menu=1)
        else: return REQUEST.RESPONSE.redirect('%s?action=finish' % DestinationURL)

    def getAppSkin(self):
        """ """
        install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        layout_tool = self.getLayoutTool()

        current_layouts = layout_tool.getDataForLayoutSettings()
        chosen_layouts = (install_data['skin'], install_data['skin_style'], current_layouts[2])
        return chosen_layouts

    def get_selected_logo(self, REQUEST=None):
        """ """
        try:
            REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
            REQUEST.RESPONSE.setHeader('Content-Disposition', 'inline; filename="logo.jpg"')
            return self.site_logo
        except: return None

    #def getLanguages(self):
        #"""Returns a list of languages with the language selected in the application as the first item."""
        #install_data = self.getSession(SESSION_INSTALL_DATA, self.getInstallData())
        #langs = self.gl_get_all_languages()
        #selected_lang = install_data['language']
        #sel_lang = {}

        #for lang in langs:
            #if lang['code'] == selected_lang:
                #sel_lang = lang

        #langs.remove(sel_lang)
        #langs.insert(0, sel_lang)

        #return langs

    # Wizard pages
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_template_html')
    install_template_html = PageTemplateFile('zpt/install_template', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_location_html')
    install_location_html = PageTemplateFile('zpt/install_location', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_welcome_html')
    install_welcome_html = PageTemplateFile('zpt/install_welcome', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_step1_html')
    install_step1_html = PageTemplateFile('zpt/install_step1', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_step2_html')
    install_step2_html = PageTemplateFile('zpt/install_step2', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_step3_html')
    install_step3_html = PageTemplateFile('zpt/install_step3', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_products_html')
    install_products_html = PageTemplateFile('zpt/install_products', globals())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'install_confirm_html')
    install_confirm_html = PageTemplateFile('zpt/install_confirm', globals())

InitializeClass(EWInstaller)
