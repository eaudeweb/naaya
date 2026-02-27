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
#$Id: EWApplications.py 2705 2004-11-26 14:30:23Z finrocvs $

#Python imports
import xmlrpclib
from os.path import join

#Zope imports
from OFS.Folder import Folder
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate

#Product imports
from constants import *
from Products.EnviroWindowsInstaller.constants import EWINSTALLER_ID
import EWApplication
from BasicAuthTransport import BasicAuthTransport
from Products.EnviroWindows.EnviroWindowsSite import EnviroWindowsSite
from Products.Naaya.NySite import NySite
from Products.NaayaCore.LayoutTool import LayoutTool
from Products.NaayaCore.managers.utils import utils, list_utils, batch_utils, file_utils
from Products.NaayaBase.constants import *
from Products.Naaya.constants import *


manage_addEWApplications_html = PageTemplateFile('zpt/applications_manage_add', 
                                                 globals())
manage_addEWApplications_html.EWKind = METATYPE_EWAPPLICATIONS
manage_addEWApplications_html.EWAction = 'addEWApplications'

def addEWApplications(self, id='', title='', description='', email_subject='', 
                      email_from='', email_to='', REQUEST=None):
    """ """
    id = self.utCleanupId(id)
    if not id: id = PREFIX_EWAPPLICATIONS + self.utGenRandomId(6)
    ob = EWApplications(id, 
                        title, 
                        description, 
                        email_subject, 
                        email_from, 
                        email_to)
    self._setObject(id, ob)
    ob = self._getOb(id)
    ob.loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class EWApplications(Folder,
    utils,
    file_utils):
    """ EWApplications class """

    meta_type = METATYPE_EWAPPLICATIONS

    manage_options = (
        Folder.manage_options[0:2]
        +
        (
            {'label' : 'Properties', 'action' : 'manage_edit_html'},
        )
        +
        Folder.manage_options[3:8]
    )

    meta_types = (
        {'name': METATYPE_EWAPPLICATION, 
         'action': 'manage_addEWApplication_html'},
        
        {'name': 'Page Template', 
         'action': 'manage_addProduct/PageTemplates/manage_addPageTemplateForm',
         'permission': 'Add Page Templates'},
    )
    all_meta_types = meta_types

    manage_addEWApplication_html = EWApplication.manage_addEWApplication_html

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, 
                 email_subject, email_from, email_to):
        """ """
        self.id = id
        self.title = title
        self.description = description
        self.email_subject = email_subject
        self.email_from = email_from
        self.email_to = email_to
        utils.__dict__['__init__'](self)
        file_utils.__dict__['__init__'](self)

    def __setstate__(self, state):
        """ """
        EWApplications.inheritedAttribute('__setstate__')(self, state)

    def __generateZopePageTemplate(self, p_folder, p_id, p_title, p_content):
        #add a ZopePageTemplate object
        manage_addPageTemplate(p_folder, id=p_id, title=p_title, text='')
        p_folder._getOb(p_id).pt_edit(text=p_content, content_type='')

    def __getContent(self, p_context={}, p_page=None):
        #Render interface pages
        return self._getOb(p_page).pt_render(extra_context=p_context)

    security.declareProtected('Add EWApplications object', 'loadDefaultData')
    def loadDefaultData(self):
        #loads all the wizard pages into Zope as PageTemplate objects
        self.__generateZopePageTemplate(
            self, 'applications_index', 'Start page', self.futRead(
                join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 
                     'applications_index.zpt')
            )
        )
        self.__generateZopePageTemplate(
            self, 'applications_step1', 'Step 1', self.futRead(
                join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 
                     'applications_step1.zpt')
            )
        )
        self.__generateZopePageTemplate(
            self, 'applications_step2', 'Step 2', self.futRead(
                join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 
                     'applications_step2.zpt')
            )
        )
        self.__generateZopePageTemplate(
            self, 'applications_step3', 'Step 3', self.futRead(
                join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 
                     'applications_step3.zpt')
            )
        )
        self.__generateZopePageTemplate(
            self, 'applications_step4', 'Step 4', self.futRead(
                join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 
                     'applications_step4.zpt')
            )
        )
        self.__generateZopePageTemplate(
            self, 'applications_confirm', 'Confirm', self.futRead(
                join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 
                     'applications_confirm.zpt')
            )
        )
        self.__generateZopePageTemplate(
            self, 'applications_finish', 'Finish', self.futRead(
                join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 
                     'applications_finish.zpt')
            )
        )
        self.__generateZopePageTemplate(
            self, 'applications_error', 'Application error', self.futRead(
                join(EWAPPLICATIONS_PRODUCT_PATH, 'zpt', 
                     'applications_error.zpt')
            )
        )

    #Wizard methods
    def getEmptyApplicationData(self):
        return {
            'site_title':'',
            'subtitle':'',
            'description':'',
            'publisher':'',
            'contributor':'',
            'languages':[],
            'creator':'',
            'rights':'',
            'agreed':'checked',
            'warning':'', 'contact_name':'',
            'contact_email':'',
            'administrator_name':'',
            'administrator_email':'',
            'username':'',
            'password':'',
            'portal_url':'',
            'products':[],
            'main_topic_a_title':'',
            'main_topic_b_title':'',
            'main_topic_c_title':'',
            'main_topic_d_title':'',
            'site_icon':None,
            'skin':'eionet',
            'colourscheme':'orange'
        }

    def getEWLogo(self):
        """."""
        file = open(join(
            EWPUBLISHER_PRODUCT_PATH, 'EWContent', 'images', 'EWLogo.gif'),
                    'rb')
        content = file.read()
        file.close()
        return content

    def setMyPicture(self, p_picture):
        """ """
        self.logo_icon = None
        if p_picture:
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.logo_icon = l_read
                        self._p_changed = 1
            else:
                self.logo_icon = p_picture
                if self.logo_icon is not None:
                    print 'is not none'
                self._p_changed = 1
                return self.logo_icon

    def applicationInit(self):
        self.REQUEST.SESSION.set(
            APPLICATION_DATA, self.getEmptyApplicationData()
        )

    def step1_process(self, site_title='', subtitle='', description='', 
                      publisher='', contributor='', creator='', rights='', 
                      languages=[], agreed='', REQUEST=None):
        """ """
        application_data = REQUEST.SESSION.get(
            APPLICATION_DATA, self.getEmptyApplicationData()
        )
        application_data['site_title'] = site_title
        application_data['subtitle'] = subtitle
        application_data['description'] = description
        application_data['publisher'] = publisher
        application_data['contributor'] = contributor
        application_data['creator'] = creator
        application_data['rights'] = rights
        if type(languages) != type([]):
            application_data['languages'] = [languages]
        else:
            application_data['languages'] = languages
        if not agreed:
            application_data['warning'] = \
            'You must agree to the Terms of Service'
            
            REQUEST.SESSION.set(APPLICATION_DATA, application_data)
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/step1_html')
        else:
            REQUEST.SESSION.set(APPLICATION_DATA, application_data)
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/step2_html')

    def step2_process(self, contact_name='', contact_email='', 
                      administrator_name='', administrator_email='', 
                      username='', password='', portal_url='', REQUEST=None):
        """ """
        application_data = REQUEST.SESSION.get(
            APPLICATION_DATA, self.getEmptyApplicationData()
        )
        application_data['contact_name'] = contact_name
        application_data['contact_email'] = contact_email
        application_data['administrator_name'] = administrator_name
        application_data['administrator_email'] = administrator_email
        application_data['portal_url'] = portal_url
        application_data['username'] = username
        application_data['password'] = password
        REQUEST.SESSION.set(APPLICATION_DATA, application_data)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/step3_html')

    def step3_process(self, products=None, REQUEST=None):
        """ """
        if products is None: products = []
        else:
            try:
                products.reverse()
            except:
                products = [products]
        application_data = REQUEST.SESSION.get(
            APPLICATION_DATA, self.getEmptyApplicationData())
        application_data['products'] = products
        REQUEST.SESSION.set(APPLICATION_DATA, application_data)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/step4_html')

    def step4_process(self, theMasterList='envirowindows', 
                      theSlaveList='EW-skin-00', site_logo=None, REQUEST=None):
        """ """
        layout_tool = self.getLayoutTool()
        application_data = REQUEST.SESSION.get(
            APPLICATION_DATA, self.getEmptyApplicationData()
        )
        layout_list = layout_tool.getDataForLayoutSettings()[2]
        for skin in layout_list:
            if skin[0] == theMasterList:
                application_data['skin_name'] = skin[1]
                
        for skin in layout_list:
            for style in skin[2]:
                if style[1] == theSlaveList:
                    application_data['skin_style_name'] = style[0]
                    
                    
        a = site_logo.read()
        if a == '':
            application_data['site_logo'] = 'Nothing'
        else:
            application_data['site_logo'] = a
            
        application_data['skin'] =  theMasterList
        application_data['skin_style'] = theSlaveList
        REQUEST.SESSION.set(APPLICATION_DATA, application_data)
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/confirm_html')

    def get_selected_logo(self, REQUEST=None):
        """Get picture stream"""
        try:
            REQUEST.RESPONSE.setHeader('Content-Type', 'image/jpeg')
            REQUEST.RESPONSE.setHeader('Content-Disposition', 
                                       'inline; filename="logo.jpg"')
            return REQUEST.SESSION.get('application_data')['site_logo']
        except: return None


    def confirm_process(self, REQUEST):
        """ """
        application_data = REQUEST.SESSION.get(
            APPLICATION_DATA, self.getEmptyApplicationData()
        )
        if application_data['site_title'] != '':
            #create application object
            id = PREFIX_EWAPPLICATION + self.utGenRandomId(6)
            ob = EWApplication.EWApplication(id,
                                             application_data['site_title'], 
                                             application_data['site_logo'], 
                                             application_data, '', 
                                             self.utGetTodayDate()
                                             )
            self._setObject(id, ob)
            #send notification email
            l_products = ', '.join(application_data['products'])
            if l_products == '': l_products = 'None'
    
            l_subject = self.email_subject
            l_from = self.email_from
            l_to = self.email_to
            l_content = """
    An application for the creation of an EnviroWindows-compliant portal has been made
    with the following information:
    
    Portal title:             %s
    Portal subtitle:          %s
    Description:              %s
    Publisher                 %s
    Contributor:              %s
    Creator:                  %s
    Rights:                   %s
    Languages:                %s
    
    Contact person:           %s
    Contact email:            %s
    Administrator name:       %s
    Administrator email:      %s
    Portal URL:               %s
    
    You can review this application and decide to create the portal or reject it
    from the applications' basket in the EnviroWindows website.
    """ % (
            application_data['site_title'],
            application_data['subtitle'],
            application_data['description'],
            application_data['publisher'],
            application_data['contributor'],
            application_data['creator'],
            application_data['rights'],
            str(application_data['languages'])[1:-1],
            application_data['contact_name'],
            application_data['contact_email'],
            application_data['administrator_name'],
            application_data['administrator_email'],
            application_data['portal_url'])
            self.getSite().getEmailTool().sendEmail(l_content, 
                                                    l_to, 
                                                    l_from, 
                                                    l_subject)
            try:
                REQUEST.SESSION.delete(APPLICATION_DATA)
            except:
                pass            
            REQUEST.RESPONSE.redirect(self.absolute_url() + 
                                      '/finish_html')
        else:
            REQUEST.RESPONSE.redirect(self.absolute_url() + 
                                      '/application_error_html')

    # API
    def getApplicationsContainer(self):
        #returns this object
        return self

    def getApplications(self):
        #returns all applications
        return self.objectValues(METATYPE_EWAPPLICATION)

    def getEWInstaller(self):
        #return the root's object EWInstaller
        return self.unrestrictedTraverse(EWINSTALLER_ID, None)

    def __valideIssueProperty(self, param):
        """Check if exists a property with given value"""
        return param in ['request_date', 'status', 'title']

    def __validParams(self, sortby, how):
        """Validate sort parameters"""
        res = 1
        if (how != 'asc' and how != 'desc'):
            res = 0
        else:
            if (self.__valideIssueProperty(sortby)):
                res = 1
            else:
                res = 0
        return res

    def getApplicationsSorted(self, sortby, how):
        """returns all applications sorted by an attribute"""
        l_apps = self.getApplications()
        if self.__validParams(sortby, how):
            if how == 'asc': how = 0
            else: how = 1
            l_apps = self.utSortObjsListByAttr(l_apps, sortby, how)
        return l_apps

    def getEWCategories(self):
        """get EW categories, using the /methods/get_fps python script"""
        try: return self.getEWSite().methods.get_fps()
        except: return []

    def getConstant(self, constant=''):
        #gets the value from a constant from constants.py;
        #used mainly for status_messages
        return eval(constant)

    # ZMI FORMS
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/applications_manage_edit', 
                                        globals())

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', email_subject='', 
                         email_from='', email_to='', REQUEST=None):
        """Update EWApplications instance properties"""
        self.title = title
        self.description = description
        self.email_subject = email_subject
        self.email_from = email_from
        self.email_to = email_to
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    # SITE FORMS
    security.declareProtected(view, 'index_html')
    def index_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_index')

    security.declareProtected(view, 'step1_html')
    def step1_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_step1')

    security.declareProtected(view, 'step2_html')
    def step2_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_step2')

    security.declareProtected(view, 'step4_html')
    def step3_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_step3')

    security.declareProtected(view, 'step4_html')
    def step4_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_step4')

    security.declareProtected(view, 'confirm_html')
    def confirm_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_confirm')

    security.declareProtected(view, 'finish_html')
    def finish_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_finish')

    security.declareProtected(view, 'application_error_html')
    def application_error_html(self, record=None, REQUEST=None, RESPONSE=None):
        """ """
        return self.__getContent({'here': self}, 'applications_error')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'basket_html')
    basket_html = PageTemplateFile('zpt/applications_basket', globals())

InitializeClass(EWApplications)
